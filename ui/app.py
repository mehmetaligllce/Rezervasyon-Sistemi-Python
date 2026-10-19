import sys
import os

PROJE_KOK = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJE_KOK not in sys.path:
    sys.path.insert(0, PROJE_KOK)

import json
import copy
from datetime import datetime, timedelta
from tkinter import filedialog, messagebox

import customtkinter as ctk

from core.sistem import Sistem
from json_io.dosya_okuma import baslangic_veri_okuma
from core.dogrulama import rezervasyon_dogrula
from core.ucret_hesapla import ucret_hesapla
from core.durum import rezervasyon_durum
from core.simule import saat_ilerlet
from core.sorgu import sorgu_isle
from core.paket import paket_isle
from core.bekleme import bekleme_kaydet
from core.ekle import kullanici_ekle, kaynak_ekle

from ui.takvim_gorunumu import TakvimGorunumu, RENK, DURUM_RENKLERI, FONT, GUN_ADLARI
from ui.talep_formu import TalepFormu, aciklama, yazi, kutu, dugme, menu

VARSAYILAN_DOSYALAR = (
    "Örnek/yeni_ornek/Örnek/baslangic.json",
    "Örnek/baslangic.json",
    "baslangic.json",
)


class ModulKoprusu:
    """Arayüz ile rezervasyon modülü arasındaki tek temas noktası."""

    def __init__(self):
        self.sistem = None
        self.gunluk = []
        self.dinleyici = None
        self._no = 0

    def yukle(self, yol):
        veri = baslangic_veri_okuma(yol)
        self.sistem = Sistem(copy.deepcopy(veri), [])
        self.gunluk.clear()
        self._no = 0

    def komut(self, komut, kaydet=True):
        if self.sistem is None:
            return {"durum": "RED", "kod": "BULUNAMADI"}
        sonuc = self._komut_yurut(komut)
        if not kaydet:
            return sonuc
        self._no += 1
        kayit = {"no": self._no, "komut": komut["komut"]}
        kayit.update({k: v for k, v in sonuc.items() if k not in ("no", "komut")})
        self.gunluk.append({"girdi": komut, "sonuc": kayit})
        if self.dinleyici:
            self.dinleyici()
        return kayit

    def _komut_yurut(self, k: dict) -> dict:
        komut_turu = k.get("komut")

        if komut_turu == "rezervasyon":
            durum = rezervasyon_dogrula(self.sistem, k)
            if durum != "BASARILI":
                return {"durum": "RED", "kod": durum}
            else:
                ucret = ucret_hesapla(self.sistem, k)
                kullanici = next(t for t in self.sistem.baslangic_veri["kullanicilar"] if t["id"] == k["kullanici"])
                kullanici["bakiye"] -= ucret
                r_id = f"r{len(self.sistem.rezervasyonlar) + 1}"
                self.sistem.rezervasyonlar.append({
                    "id": r_id,
                    "kullanici": k["kullanici"],
                    "kaynak": k["kaynak"],
                    "baslangic": k["baslangic"],
                    "bitis": k["bitis"],
                    "ucret": ucret,
                    "durum": "ONAYLI",
                })
                return {
                    "durum": "TAMAM",
                    "rezervasyon_id": r_id,
                    "ucret": ucret,
                    "bakiye": kullanici["bakiye"],
                }

        elif komut_turu == "fiyat":
            durum = rezervasyon_dogrula(self.sistem, k)
            if durum != "BASARILI":
                return {"durum": "RED", "kod": durum}
            else:
                ucret = ucret_hesapla(self.sistem, k)
                return {"durum": "TAMAM", "ucret": ucret}

        elif komut_turu in ["giris", "cikis", "iptal"]:
            return rezervasyon_durum(self.sistem, k)

        elif komut_turu == "saat":
            yeni_saat = datetime.fromisoformat(k["zaman"])
            sonuc = saat_ilerlet(self.sistem, yeni_saat)
            if sonuc.get("durum") == "TAMAM":
                self.sistem.saat = yeni_saat
            return sonuc

        elif komut_turu == "sorgu":
            return sorgu_isle(self.sistem, k)

        elif komut_turu == "paket":
            sonuc = paket_isle(self.sistem, k)
            if sonuc.get("durum") == "TAMAM":
                self.sistem.paket_sayac += 1
            return sonuc

        elif komut_turu == "bekleme":
            durum = rezervasyon_dogrula(self.sistem, k)
            if durum == "BASARILI":
                return {"durum": "RED", "kod": "BEKLEME_GEREKSIZ"}
            elif durum in ["KESISME", "HAZIRLIK_IHLALI"]:
                self.sistem.bekleme_sayac += 1
                return bekleme_kaydet(self.sistem, k)
            else:
                return {"durum": "RED", "kod": durum}

        elif komut_turu == "kullanici_ekle":
            return kullanici_ekle(self.sistem, k)

        elif komut_turu == "kaynak_ekle":
            return kaynak_ekle(self.sistem, k)

        else:
            return {"durum": "TAMAM"}

    def saat(self):
        return self.sistem.saat if self.sistem else None

    def veri(self):
        return self.sistem.baslangic_veri if self.sistem else {}

    def kullanicilar(self):
        return self.veri().get("kullanicilar", [])

    def kaynaklar(self):
        return self.veri().get("kaynaklar", [])

    def kullanici(self, kid):
        return next((k for k in self.kullanicilar() if k["id"] == kid), None)

    def sorgu_kullanici(self, kid):
        return self.komut({"komut": "sorgu", "tur": "kullanici", "id": kid}, kaydet=False)

    def bekleme_kayitlari(self, kid):
        if self.sistem is None:
            return []
        return [b for b in getattr(self.sistem, "bekleme_listesi", []) if b.get("kullanici") == kid]


def olay_metni(e):
    parca = [e.get("zaman", "")[11:16], e.get("tur", "")]
    if "bekleme" in e and "rezervasyon" in e:
        parca.append(f"{e['bekleme']}→{e['rezervasyon']}")
    elif "rezervasyon" in e:
        parca.append(str(e["rezervasyon"]))
    return " ".join(p for p in parca if p)


def sayi(metin):
    metin = metin.strip()
    for tur in (int, float):
        try:
            return tur(metin)
        except ValueError:
            pass
    return metin


class KullaniciKarti(ctk.CTkFrame):
    def __init__(self, master, modul, secildi):
        super().__init__(master, fg_color=RENK["panel"], corner_radius=14)
        self.modul = modul
        self.secildi = secildi
        self.aktif_id = None
        self.v_menu = ctk.StringVar(value="—")
        self.menu = menu(self, self.v_menu, ["—"], command=self._sec)
        self.menu.pack(fill="x", padx=14, pady=(14, 10))

        satir = ctk.CTkFrame(self, fg_color="transparent")
        satir.pack(fill="x", padx=14, pady=(0, 14))
        satir.columnconfigure((0, 1), weight=1, uniform="a")
        self.lbl_bakiye, self.bar_bakiye = self._istatistik(satir, 0, "BAKİYE")
        self.lbl_guv, self.bar_guv = self._istatistik(satir, 1, "GÜVENİLİRLİK")

    def _istatistik(self, parent, sutun, baslik):
        kutu_ = ctk.CTkFrame(parent, fg_color=RENK["kart"], corner_radius=10)
        kutu_.grid(row=0, column=sutun, sticky="ew", padx=(0, 6) if sutun == 0 else (6, 0))
        yazi(kutu_, baslik, font=(FONT, 10, "bold")).pack(anchor="w", padx=12, pady=(8, 0))
        etiket = ctk.CTkLabel(kutu_, text="—", font=(FONT, 18, "bold"), text_color=RENK["metin"])
        etiket.pack(anchor="w", padx=12)
        bar = ctk.CTkProgressBar(kutu_, height=6, progress_color=RENK["vurgu"], fg_color=RENK["cizgi"])
        bar.set(0)
        bar.pack(fill="x", padx=12, pady=(2, 10))
        return etiket, bar

    def menu_yenile(self):
        secenekler = {
            k["id"]: f"{k['id']} · {k['ad']} ({k['rol']})" for k in self.modul.kullanicilar()
        }
        self.menu.configure(values=list(secenekler.values()) or ["—"])
        if self.aktif_id not in secenekler:
            self.aktif_id = next(iter(secenekler), None)
        self.v_menu.set(secenekler.get(self.aktif_id, "—"))

    def sec(self, kid):
        self.aktif_id = kid
        self.menu_yenile()
        self.secildi()

    def _sec(self, secim):
        self.aktif_id = secim.split(" · ")[0]
        self.secildi()

    def istatistik(self, sorgu):
        bakiye, guv = sorgu.get("bakiye"), sorgu.get("guvenilirlik")
        kullanici = self.modul.kullanici(self.aktif_id) if self.aktif_id else None
        kota = None
        if kullanici:
            kota = self.modul.veri().get("roller", {}).get(kullanici["rol"], {}).get("haftalik_kota")
        if bakiye is None:
            self.lbl_bakiye.configure(text="—")
            self.lbl_guv.configure(text="—")
            self.bar_bakiye.set(0)
            self.bar_guv.set(0)
            return
        self.lbl_bakiye.configure(text=f"{bakiye} / {kota} KP" if kota else f"{bakiye} KP")
        self.bar_bakiye.set(max(0, min(1, bakiye / kota)) if kota else 0)
        self.lbl_guv.configure(text=f"{guv} / 100")
        self.bar_guv.set(max(0, min(1, guv / 100)))


class RezervasyonListesi(ctk.CTkScrollableFrame):
    def __init__(self, master, modul, secildi, aktif_kullanici):
        super().__init__(master, fg_color="transparent")
        self.modul = modul
        self.secildi = secildi
        self._aktif = aktif_kullanici

    def yenile(self, sorgu):
        for w in self.winfo_children():
            w.destroy()
        kid = sorgu.get("kullanici") or None
        rezervasyonlar = sorgu.get("rezervasyonlar", [])
        if not rezervasyonlar:
            yazi(self, "Bu kullanıcının rezervasyonu yok.").pack(anchor="w", padx=6, pady=4)
        for r in rezervasyonlar:
            renk = DURUM_RENKLERI.get(r.get("durum"), RENK["soluk"])
            satir = ctk.CTkFrame(self, fg_color="transparent")
            satir.pack(fill="x", pady=1)
            ctk.CTkLabel(satir, text="●", width=16, text_color=renk, font=(FONT, 12)).pack(side="left")
            metin = (
                f"{r['id']}  {r['kaynak']}  {r['baslangic'][5:10]} "
                f"{r['baslangic'][11:16]}–{r['bitis'][11:16]}  {r['durum']}  {r.get('ucret', '-')} KP"
            )
            ctk.CTkButton(
                satir, text=metin, anchor="w", height=30, corner_radius=8, fg_color=RENK["kart"],
                hover_color=RENK["cizgi"], text_color=RENK["metin"], font=(FONT, 12),
                command=lambda r=r: self.secildi(dict(r, tur="REZERVASYON", kullanici=kid or r.get("kullanici"))),
            ).pack(side="left", fill="x", expand=True)

        bekleyenler = self.modul.bekleme_kayitlari(self._aktif())
        if bekleyenler:
            yazi(self, "BEKLEME KAYITLARI", font=(FONT, 10, "bold")).pack(anchor="w", padx=6, pady=(12, 2))
            for b in bekleyenler:
                yazi(
                    self,
                    f"⏳ {b['id']}  {b['kaynak']}  {b['baslangic'][5:10]} "
                    f"{b['baslangic'][11:16]}–{b['bitis'][11:16]}",
                    text_color=RENK["metin"],
                ).pack(anchor="w", padx=6, pady=1)


class RezervasyonDetay(ctk.CTkFrame):
    def __init__(self, master, modul, aktif_kullanici):
        super().__init__(master, fg_color=RENK["panel"], corner_radius=14)
        self.modul = modul
        self.aktif_kullanici = aktif_kullanici
        self.oge = None
        self.columnconfigure(0, weight=1)
        self.lbl_baslik = ctk.CTkLabel(self, text="", anchor="w", font=(FONT, 15, "bold"), text_color=RENK["metin"])
        self.lbl_baslik.grid(row=0, column=0, sticky="w", padx=16, pady=(10, 0))
        self.lbl_alt = ctk.CTkLabel(self, text="", anchor="w", font=(FONT, 12), text_color=RENK["soluk"])
        self.lbl_alt.grid(row=1, column=0, sticky="w", padx=16)
        self.lbl_sonuc = ctk.CTkLabel(
            self, text="", anchor="w", justify="left", wraplength=620, font=(FONT, 12), text_color=RENK["soluk"]
        )
        self.lbl_sonuc.grid(row=2, column=0, sticky="w", padx=16, pady=(2, 10))

        butonlar = ctk.CTkFrame(self, fg_color="transparent")
        butonlar.grid(row=0, column=1, rowspan=3, padx=14)
        self.dugmeler = [
            dugme(butonlar, "Giriş", lambda: self.eylem("giris"), width=74),
            dugme(butonlar, "Çıkış", lambda: self.eylem("cikis"), width=74),
            dugme(butonlar, "İptal", lambda: self.eylem("iptal"), "tehlike", width=74),
            dugme(butonlar, "Bekle", self.bekle, width=74),
        ]
        for d in self.dugmeler:
            d.pack(side="left", padx=3)
        self.goster()

    def sec(self, oge):
        self.oge = oge
        self.lbl_sonuc.configure(text="")
        self.goster()

    def yenile(self):
        if self.oge and self.oge.get("tur") == "REZERVASYON" and self.modul.sistem:
            guncel = next((r for r in self.modul.sistem.rezervasyonlar if r["id"] == self.oge["id"]), None)
            if guncel:
                self.oge = dict(self.oge, **guncel)
        self.goster()

    def goster(self):
        oge = self.oge
        for d in self.dugmeler:
            d.configure(state="normal" if oge and oge.get("tur") == "REZERVASYON" else "disabled")
        if not oge:
            self.lbl_baslik.configure(text="Rezervasyon seçilmedi")
            self.lbl_alt.configure(text="Takvimde bir kutuya ya da Rezervasyon sekmesinde bir satıra tıkla.",
                                   text_color=RENK["soluk"])
            return
        zaman = f"{oge.get('baslangic', '')[:10]}  {oge.get('baslangic', '')[11:16]} → {oge.get('bitis', '')[11:16]}"
        tur = oge.get("tur")
        if tur == "REZERVASYON":
            kullanici = self.modul.kullanici(oge.get("kullanici"))
            ad = f"{oge.get('kullanici')} · {kullanici['ad']}" if kullanici else str(oge.get("kullanici"))
            self.lbl_baslik.configure(text=f"{oge['id']}  ·  {ad}  ·  {oge.get('kaynak')}")
            ek = f"   ·   {oge['ucret']} KP" if oge.get("ucret") is not None else ""
            if oge.get("paket"):
                ek += f"   ·   paket {oge['paket']}"
            self.lbl_alt.configure(
                text=f"{zaman}   ·   {oge.get('durum')}{ek}",
                text_color=DURUM_RENKLERI.get(oge.get("durum"), RENK["soluk"]),
            )
        elif tur == "BAKIM":
            self.lbl_baslik.configure(text=f"Bakım penceresi  ·  {oge.get('kaynak')}")
            self.lbl_alt.configure(text=zaman, text_color=DURUM_RENKLERI["BAKIM"])
        else:
            self.lbl_baslik.configure(text=f"Hazırlık / soğuma  ·  {oge.get('kaynak')}")
            self.lbl_alt.configure(text=f"{zaman}   ·   {oge.get('rezervasyon_id', '')}",
                                   text_color=DURUM_RENKLERI["HAZIRLIK"])

    def _sonuc_yaz(self, s, tamam_metni):
        if s.get("durum") == "TAMAM":
            satirlar = [tamam_metni]
            for e in s.get("olaylar", []):
                satirlar.append("⚡ " + olay_metni(e))
            self.lbl_sonuc.configure(text="\n".join(satirlar), text_color=RENK["iyi"])
        else:
            kod = s.get("kod", "?")
            self.lbl_sonuc.configure(text=f"✘ {kod} · {aciklama(kod)}", text_color=RENK["kotu"])

    def eylem(self, ad):
        s = self.modul.komut({"komut": ad, "rezervasyon": self.oge["id"]})
        if ad == "giris":
            yeni = s.get("yeni_durum", "KULLANIMDA")
            metin = f"✔ Giriş yapıldı · {yeni}"
        elif ad == "cikis":
            yeni = s.get("yeni_durum", "TAMAMLANDI")
            g = s.get("guvenilirlik")
            metin = f"✔ {yeni}" + (f" · güvenilirlik {g}" if g is not None else "")
        else:
            g = s.get("guvenilirlik")
            g_ek = f" · güvenilirlik {g}" if g is not None else ""
            metin = f"✔ İptal edildi · iade {s.get('iade', 0)} KP · bakiye {s.get('bakiye', '-')} KP{g_ek}"
        self._sonuc_yaz(s, metin)

    def bekle(self):
        o = self.oge
        s = self.modul.komut({
            "komut": "bekleme", "kullanici": self.aktif_kullanici() or "",
            "kaynak": o["kaynak"], "baslangic": o["baslangic"], "bitis": o["bitis"],
        })
        self._sonuc_yaz(s, f"⏳ {s.get('bekleme_id')} kaydedildi · sıra {s.get('sira')}")


class UyeEkleFormu(ctk.CTkFrame):
    def __init__(self, master, modul, eklendi):
        super().__init__(master, fg_color="transparent")
        self.modul = modul
        self.eklendi = eklendi
        self._roller = None
        self._sertifikalar = None
        self.sert = {}
        self.v_id, self.v_ad = ctk.StringVar(), ctk.StringVar()
        self.v_rol, self.v_bakiye, self.v_guv = ctk.StringVar(value="—"), ctk.StringVar(), ctk.StringVar(value="100")

        govde = ctk.CTkFrame(self, fg_color="transparent")
        govde.pack(fill="x", pady=(6, 0))
        govde.columnconfigure(1, weight=1)
        self.menu_rol = menu(govde, self.v_rol, ["—"], command=self._rol_degisti)
        for i, (ad, widget) in enumerate((
            ("ID", kutu(govde, self.v_id)),
            ("Ad", kutu(govde, self.v_ad)),
            ("Rol", self.menu_rol),
            ("Bakiye", kutu(govde, self.v_bakiye)),
            ("Güvenilirlik", kutu(govde, self.v_guv)),
        )):
            yazi(govde, ad).grid(row=i, column=0, sticky="w", pady=4)
            widget.grid(row=i, column=1, sticky="ew", padx=(12, 0), pady=4)

        yazi(self, "Sertifikalar", font=(FONT, 11)).pack(anchor="w", pady=(8, 2))
        self.sert_alani = ctk.CTkFrame(self, fg_color="transparent")
        self.sert_alani.pack(fill="x")
        dugme(self, "Üyeyi ekle", self.ekle, "birincil", height=38).pack(fill="x", pady=(12, 8))
        self.lbl_sonuc = yazi(self, "", wraplength=380, justify="left", font=(FONT, 13, "bold"))
        self.lbl_sonuc.pack(anchor="w")

    def yenile(self, ilk=False):
        veri = self.modul.veri()
        roller = tuple(veri.get("roller", {}))
        sertifikalar = tuple(sorted({
            t["sertifika"] for t in veri.get("kaynak_turleri", {}).values() if t.get("sertifika")
        } | {s for k in self.modul.kullanicilar() for s in k.get("sertifikalar", [])}))
        if roller != self._roller or ilk:
            self._roller = roller
            self.menu_rol.configure(values=list(roller) or ["—"])
            self.v_rol.set(roller[0] if roller else "—")
            self._rol_degisti(self.v_rol.get())
            self.v_id.set(f"u{len(self.modul.kullanicilar()) + 1}")
        if sertifikalar != self._sertifikalar:
            self._sertifikalar = sertifikalar
            for w in self.sert_alani.winfo_children():
                w.destroy()
            self.sert = {}
            for i, s in enumerate(sertifikalar):
                self.sert[s] = ctk.BooleanVar(value=False)
                ctk.CTkCheckBox(
                    self.sert_alani, text=s, variable=self.sert[s], font=(FONT, 12),
                    text_color=RENK["metin"], fg_color=RENK["vurgu"], hover_color=RENK["vurgu_koyu"],
                    checkbox_width=18, checkbox_height=18,
                ).grid(row=i // 2, column=i % 2, sticky="w", padx=(0, 16), pady=2)

    def _rol_degisti(self, rol):
        kota = self.modul.veri().get("roller", {}).get(rol, {}).get("haftalik_kota")
        if kota is not None:
            self.v_bakiye.set(str(kota))

    def ekle(self):
        komut = {
            "komut": "kullanici_ekle", "id": self.v_id.get().strip(), "ad": self.v_ad.get().strip(),
            "rol": self.v_rol.get(), "sertifikalar": [c for c, v in self.sert.items() if v.get()],
            "bakiye": sayi(self.v_bakiye.get()), "guvenilirlik": sayi(self.v_guv.get()),
        }
        s = self.modul.komut(komut)
        if s.get("durum") == "TAMAM":
            self.lbl_sonuc.configure(text=f"✔ {komut['id']} eklendi", text_color=RENK["iyi"])
            self.v_id.set(f"u{len(self.modul.kullanicilar()) + 1}")
            self.v_ad.set("")
            self.eklendi(komut["id"])
        else:
            kod = s.get("kod", "?")
            self.lbl_sonuc.configure(text=f"✘ {kod}\n{aciklama(kod)}", text_color=RENK["kotu"])


class KaynakEkleFormu(ctk.CTkFrame):
    def __init__(self, master, modul):
        super().__init__(master, fg_color="transparent")
        self.modul = modul
        self._turler = None
        self._roller = None
        self.roller = {}
        self.v_id, self.v_ad, self.v_tur = ctk.StringVar(), ctk.StringVar(), ctk.StringVar(value="—")

        govde = ctk.CTkFrame(self, fg_color="transparent")
        govde.pack(fill="x", pady=(6, 0))
        govde.columnconfigure(1, weight=1)
        self.menu_tur = menu(govde, self.v_tur, ["—"])
        for i, (ad, widget) in enumerate((
            ("ID", kutu(govde, self.v_id)),
            ("Ad", kutu(govde, self.v_ad)),
            ("Tür", self.menu_tur),
        )):
            yazi(govde, ad).grid(row=i, column=0, sticky="w", pady=4)
            widget.grid(row=i, column=1, sticky="ew", padx=(12, 0), pady=4)

        yazi(self, "İzinli roller", font=(FONT, 11)).pack(anchor="w", pady=(8, 2))
        self.rol_alani = ctk.CTkFrame(self, fg_color="transparent")
        self.rol_alani.pack(fill="x")
        dugme(self, "Kaynağı ekle", self.ekle, "birincil", height=38).pack(fill="x", pady=(12, 8))
        self.lbl_sonuc = yazi(self, "", wraplength=380, justify="left", font=(FONT, 13, "bold"))
        self.lbl_sonuc.pack(anchor="w")

    def yenile(self, ilk=False):
        veri = self.modul.veri()
        turler = tuple(veri.get("kaynak_turleri", {}))
        roller = tuple(veri.get("roller", {}))
        if turler != self._turler or ilk:
            self._turler = turler
            self.menu_tur.configure(values=list(turler) or ["—"])
            self.v_tur.set(turler[0] if turler else "—")
        if roller != self._roller or ilk:
            self._roller = roller
            for w in self.rol_alani.winfo_children():
                w.destroy()
            self.roller = {}
            for i, r in enumerate(roller):
                self.roller[r] = ctk.BooleanVar(value=True)
                ctk.CTkCheckBox(
                    self.rol_alani, text=r, variable=self.roller[r], font=(FONT, 12),
                    text_color=RENK["metin"], fg_color=RENK["vurgu"], hover_color=RENK["vurgu_koyu"],
                    checkbox_width=18, checkbox_height=18,
                ).grid(row=i // 2, column=i % 2, sticky="w", padx=(0, 16), pady=2)

    def ekle(self):
        komut = {
            "komut": "kaynak_ekle", "id": self.v_id.get().strip(), "ad": self.v_ad.get().strip(),
            "tur": self.v_tur.get(), "izinli_roller": [r for r, v in self.roller.items() if v.get()],
        }
        s = self.modul.komut(komut)
        if s.get("durum") == "TAMAM":
            self.lbl_sonuc.configure(text=f"✔ {komut['id']} eklendi, takvimde görünüyor", text_color=RENK["iyi"])
            self.v_id.set("")
            self.v_ad.set("")
        else:
            kod = s.get("kod", "?")
            self.lbl_sonuc.configure(text=f"✘ {kod}\n{aciklama(kod)}", text_color=RENK["kotu"])


class GunlukPaneli(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=RENK["panel"], corner_radius=14)
        self.columnconfigure(0, weight=3)
        self.columnconfigure(1, weight=2)
        self.rowconfigure(1, weight=1)
        ctk.CTkLabel(self, text="Olay günlüğü", font=(FONT, 13, "bold"), text_color=RENK["metin"]).grid(
            row=0, column=0, sticky="w", padx=16, pady=(8, 0))
        self.liste = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.liste.grid(row=1, column=0, sticky="nsew", padx=(8, 4), pady=(2, 8))
        self.json_kutusu = ctk.CTkTextbox(
            self, fg_color=RENK["kart"], text_color=RENK["metin"], font=("Consolas", 11),
            wrap="word", corner_radius=10,
        )
        self.json_kutusu.grid(row=0, column=1, rowspan=2, sticky="nsew", padx=(4, 10), pady=10)
        self._yaz("Ayrıntı için günlükten bir satır seçin.")

    def _yaz(self, metin):
        self.json_kutusu.configure(state="normal")
        self.json_kutusu.delete("1.0", "end")
        self.json_kutusu.insert("1.0", metin)
        self.json_kutusu.configure(state="disabled")

    def temizle(self):
        for w in self.liste.winfo_children():
            w.destroy()
        self._yaz("Ayrıntı için günlükten bir satır seçin.")

    @staticmethod
    def _ozet(girdi, sonuc):
        if sonuc.get("durum") != "TAMAM":
            return f"✘ {sonuc.get('kod', '?')}"
        if girdi["komut"] == "saat":
            return f"✔ {len(sonuc.get('olaylar', []))} olay → {girdi['zaman'][11:16]}"
        ek = [f"{k}={v}" for k, v in sonuc.items()
              if k not in ("no", "komut", "durum") and isinstance(v, (str, int, float))]
        return "✔ " + " ".join(ek)

    def _satir(self, metin, renk, kayit, girinti=0):
        ctk.CTkButton(
            self.liste, text=metin, anchor="w", height=22, corner_radius=6, fg_color="transparent",
            hover_color=RENK["kart"], text_color=renk, font=("Consolas", 11),
            command=lambda: self.sec(kayit),
        ).pack(fill="x", padx=(girinti, 0))

    def ekle(self, kayit):
        girdi, sonuc = kayit["girdi"], kayit["sonuc"]
        kim = girdi.get("kullanici") or girdi.get("rezervasyon") or girdi.get("id") or ""
        metin = f"#{sonuc['no']:<3}{girdi['komut']:<15}{str(kim):<8}{self._ozet(girdi, sonuc)}"
        self._satir(metin, RENK["metin"] if sonuc.get("durum") == "TAMAM" else RENK["kotu"], kayit)
        for e in sonuc.get("olaylar", []):
            self._satir("└ " + olay_metni(e), RENK["uyari"], kayit, 26)
        self.after(40, lambda: self.liste._parent_canvas.yview_moveto(1.0))

    def sec(self, kayit):
        self._yaz(
            "KOMUT\n" + json.dumps(kayit["girdi"], ensure_ascii=False)
            + "\n\nSONUÇ\n" + json.dumps(kayit["sonuc"], ensure_ascii=False)
        )


class KampusRezervasyonApp(ctk.CTk):
    def __init__(self, baslangic_yolu=None):
        super().__init__()
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        self.title("Kampüs Kaynak Rezervasyon Sistemi")
        self.geometry("1400x860")
        self.minsize(1200, 740)
        self.configure(fg_color=RENK["zemin"])

        self.modul = ModulKoprusu()
        self._gosterilen = 0
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._ust_bar()
        self._govde()
        self.gunluk = GunlukPaneli(self)
        self.gunluk.configure(height=190)
        self.gunluk.grid(row=2, column=0, sticky="ew", padx=14, pady=(0, 14))
        self.gunluk.grid_propagate(False)
        self.modul.dinleyici = self.guncelle

        yol = baslangic_yolu or next((y for y in VARSAYILAN_DOSYALAR if os.path.exists(y)), None)
        if yol:
            self.dosya_yukle(yol)

    def _ust_bar(self):
        bar = ctk.CTkFrame(self, fg_color=RENK["panel"], corner_radius=14, height=70)
        bar.grid(row=0, column=0, sticky="ew", padx=14, pady=14)
        bar.pack_propagate(False)

        ctk.CTkLabel(bar, text="🏛  Kampüs Kaynak Rezervasyon", font=(FONT, 17, "bold"),
                     text_color=RENK["vurgu"]).pack(side="left", padx=(18, 14))
        dugme(bar, "📁  Başlangıç dosyası", self._dosya_sec, width=170).pack(side="left")
        self.lbl_dosya = yazi(bar, "dosya seçilmedi")
        self.lbl_dosya.pack(side="left", padx=10)

        sag = ctk.CTkFrame(bar, fg_color="transparent")
        sag.pack(side="right", padx=16)
        ust = ctk.CTkFrame(sag, fg_color="transparent")
        ust.pack(anchor="e")
        self.v_zaman = ctk.StringVar()
        dugme(ust, "Git", self.saat_git, width=44, height=28).pack(side="right")
        kutu(ust, self.v_zaman, width=146, height=28, placeholder_text="2027-03-08T11:20").pack(side="right", padx=6)
        for metin, delta in (("+1 gün", timedelta(days=1)), ("+1 sa", timedelta(hours=1)), ("+15 dk", timedelta(minutes=15))):
            dugme(ust, metin, lambda d=delta: self.saat_ilerlet(d), width=58, height=28).pack(side="right", padx=2)
        self.lbl_saat = ctk.CTkLabel(ust, text="—", font=(FONT, 20, "bold"), text_color=RENK["metin"])
        self.lbl_saat.pack(side="right", padx=(0, 14))
        self.lbl_olay = yazi(sag, "", wraplength=620, justify="right", font=(FONT, 11))
        self.lbl_olay.pack(anchor="e")

    def _govde(self):
        govde = ctk.CTkFrame(self, fg_color="transparent")
        govde.grid(row=1, column=0, sticky="nsew", padx=14, pady=(0, 14))
        govde.grid_columnconfigure(0, weight=1)
        govde.grid_rowconfigure(0, weight=1)

        sol = ctk.CTkFrame(govde, fg_color="transparent")
        sol.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        sol.grid_columnconfigure(0, weight=1)
        sol.grid_rowconfigure(0, weight=1)

        self.detay = RezervasyonDetay(sol, self.modul, self.aktif_kullanici)
        self.takvim = TakvimGorunumu(
            sol, self.modul, on_secim=self.rezervasyon_secildi,
            on_gun_degisti=lambda g: self.talep.gun_yaz(g),
        )
        self.takvim.grid(row=0, column=0, sticky="nsew")
        self.detay.grid(row=1, column=0, sticky="ew", pady=(12, 0))

        sag = ctk.CTkFrame(govde, fg_color="transparent", width=450)
        sag.grid(row=0, column=1, sticky="ns")
        sag.pack_propagate(False)
        self.karti = KullaniciKarti(sag, self.modul, self.kullanici_degisti)
        self.karti.pack(fill="x")

        sekmeler = ctk.CTkTabview(
            sag, fg_color=RENK["panel"], corner_radius=14, segmented_button_fg_color=RENK["kart"],
            segmented_button_selected_color=RENK["vurgu"], segmented_button_selected_hover_color=RENK["vurgu_koyu"],
            segmented_button_unselected_color=RENK["kart"], segmented_button_unselected_hover_color=RENK["cizgi"],
        )
        sekmeler.pack(fill="both", expand=True, pady=(12, 0))
        for ad in ("Talep", "Rezervasyon", "+ Üye", "+ Kaynak"):
            sekmeler.add(ad)

        self.talep = TalepFormu(
            sekmeler.tab("Talep"), self.modul, self.aktif_kullanici,
            lambda: self.takvim.secilen_gun, self.takvim.gun_ata,
        )
        self.talep.pack(fill="both", expand=True, padx=6)
        self.rez_listesi = RezervasyonListesi(
            sekmeler.tab("Rezervasyon"), self.modul, self.rezervasyon_secildi, self.aktif_kullanici
        )
        self.rez_listesi.pack(fill="both", expand=True)
        self.uye_formu = UyeEkleFormu(sekmeler.tab("+ Üye"), self.modul, self.karti.sec)
        self.uye_formu.pack(fill="both", expand=True, padx=6)
        self.kaynak_formu = KaynakEkleFormu(sekmeler.tab("+ Kaynak"), self.modul)
        self.kaynak_formu.pack(fill="both", expand=True, padx=6)

    def aktif_kullanici(self):
        return self.karti.aktif_id

    def kullanici_degisti(self):
        self.guncelle()
        self.talep.planla()

    def rezervasyon_secildi(self, oge):
        self.detay.sec(oge)
        if oge.get("tur") == "REZERVASYON":
            self.takvim.secili_id = oge["id"]
            if oge.get("baslangic"):
                self.takvim.gun_ata(oge["baslangic"][:10])

    def _dosya_sec(self):
        yol = filedialog.askopenfilename(
            title="Başlangıç dosyası seç", filetypes=[("JSON", "*.json"), ("Tüm dosyalar", "*.*")]
        )
        if yol:
            self.dosya_yukle(yol)

    def dosya_yukle(self, yol):
        try:
            self.modul.yukle(yol)
        except Exception as e:
            messagebox.showerror("Hata", f"Başlangıç dosyası yüklenemedi:\n{e}")
            return
        self.lbl_dosya.configure(text=os.path.basename(yol))
        self.gunluk.temizle()
        self._gosterilen = 0
        self.karti.aktif_id = None
        self.detay.sec(None)
        self.lbl_olay.configure(text="")
        self.takvim.secili_id = None
        self.takvim.gun_ata(self.modul.saat().strftime("%Y-%m-%d"))
        self.talep.varsayilanlari_yenile()
        self.uye_formu.yenile(ilk=True)
        self.kaynak_formu.yenile(ilk=True)
        self.guncelle()

    def saat_ilerlet(self, delta):
        saat = self.modul.saat()
        if saat is not None:
            self._saat_komutu((saat + delta).strftime("%Y-%m-%dT%H:%M"))

    def saat_git(self):
        zaman = self.v_zaman.get().strip()
        if zaman:
            self._saat_komutu(zaman)

    def _saat_komutu(self, zaman):
        s = self.modul.komut({"komut": "saat", "zaman": zaman})
        if s.get("durum") == "TAMAM":
            olaylar = s.get("olaylar", [])
            metin = "   ·   ".join(olay_metni(e) for e in olaylar) or "Bu aralıkta olay yok"
            self.lbl_olay.configure(text=metin, text_color=RENK["uyari"] if olaylar else RENK["soluk"])
        else:
            kod = s.get("kod", "?")
            self.lbl_olay.configure(text=f"✘ {kod} · {aciklama(kod)}", text_color=RENK["kotu"])

    def guncelle(self):
        saat = self.modul.saat()
        if saat:
            self.lbl_saat.configure(
                text=f"{saat:%Y-%m-%d}  {GUN_ADLARI[saat.weekday()][:3]}  {saat:%H:%M}"
            )
        self.karti.menu_yenile()
        kid = self.karti.aktif_id
        sorgu = self.modul.sorgu_kullanici(kid) if kid else {}
        sorgu.setdefault("kullanici", kid)
        self.karti.istatistik(sorgu)
        self.rez_listesi.yenile(sorgu)
        self.takvim.ciz()
        self.talep.listeleri_guncelle()
        self.uye_formu.yenile()
        self.kaynak_formu.yenile()
        self.detay.yenile()
        for kayit in self.modul.gunluk[self._gosterilen:]:
            self.gunluk.ekle(kayit)
        self._gosterilen = len(self.modul.gunluk)


def baslat():
    yol = sys.argv[1] if len(sys.argv) > 1 else None
    KampusRezervasyonApp(yol).mainloop()


if __name__ == "__main__":
    baslat()
