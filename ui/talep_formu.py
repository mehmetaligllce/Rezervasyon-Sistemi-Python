from datetime import datetime

import customtkinter as ctk

import core.sabitler as sbt
from ui.takvim_gorunumu import RENK, FONT

BEKLEME_KODLARI = ("KESISME", "HAZIRLIK_IHLALI")


def saat_secenekleri():
    return [
        f"{dk // 60:02d}:{dk % 60:02d}"
        for dk in range(sbt.REZERVASYON_BASLANGIC * 60, sbt.REZERVASYON_BITIS * 60 + 1, 15)
    ]


def yazi(master, metin, **kw):
    kw.setdefault("font", (FONT, 12))
    kw.setdefault("text_color", RENK["soluk"])
    return ctk.CTkLabel(master, text=metin, **kw)


def kutu(master, degisken, **kw):
    kw.setdefault("height", 32)
    kw.setdefault("corner_radius", 8)
    kw.setdefault("fg_color", RENK["kart"])
    kw.setdefault("border_color", RENK["cizgi"])
    kw.setdefault("text_color", RENK["metin"])
    kw.setdefault("font", (FONT, 13))
    return ctk.CTkEntry(master, textvariable=degisken, **kw)


def dugme(master, metin, komut, tur="ikincil", **kw):
    renkler = {
        "birincil": (RENK["vurgu"], RENK["vurgu_koyu"]),
        "tehlike": (RENK["kotu"], "#D84A4A"),
        "ikincil": (RENK["kart"], RENK["cizgi"]),
    }
    normal, uzerinde = renkler[tur]
    kw.setdefault("height", 32)
    return ctk.CTkButton(
        master, text=metin, command=komut, fg_color=normal, hover_color=uzerinde,
        text_color="#FFFFFF" if tur != "ikincil" else RENK["metin"],
        text_color_disabled=RENK["soluk"], corner_radius=8, font=(FONT, 12, "bold"), **kw,
    )


def menu(master, degisken, degerler, **kw):
    return ctk.CTkOptionMenu(
        master, variable=degisken, values=degerler, height=32, corner_radius=8,
        fg_color=RENK["kart"], button_color=RENK["cizgi"], button_hover_color=RENK["vurgu_koyu"],
        text_color=RENK["metin"], dropdown_fg_color=RENK["kart"], font=(FONT, 12),
        dropdown_font=(FONT, 12), dynamic_resizing=False, **kw,
    )


class KalemSatiri(ctk.CTkFrame):
    def __init__(self, master, degisti):
        super().__init__(master, fg_color="transparent")
        self.v_kaynak = ctk.StringVar(value="—")
        self.v_bas = ctk.StringVar(value="11:00")
        self.v_bit = ctk.StringVar(value="13:00")
        saatler = saat_secenekleri()

        self.menu = menu(self, self.v_kaynak, ["—"])
        self.menu.grid(row=0, column=0, sticky="ew")
        for sutun, degisken in ((1, self.v_bas), (2, self.v_bit)):
            ctk.CTkComboBox(
                self, variable=degisken, values=saatler, width=92, height=32, corner_radius=8,
                fg_color=RENK["kart"], border_color=RENK["cizgi"], button_color=RENK["cizgi"],
                button_hover_color=RENK["vurgu_koyu"], text_color=RENK["metin"],
                dropdown_fg_color=RENK["kart"], font=(FONT, 12), dropdown_font=(FONT, 12),
            ).grid(row=0, column=sutun, padx=(6, 0))
        self.columnconfigure(0, weight=1)
        for v in (self.v_kaynak, self.v_bas, self.v_bit):
            v.trace_add("write", lambda *a: degisti())

    def kaynaklari_ayarla(self, secenekler):
        self.menu.configure(values=secenekler)
        if self.v_kaynak.get() not in secenekler:
            self.v_kaynak.set(secenekler[0])

    def kaynak_id(self):
        secim = self.v_kaynak.get()
        return "" if secim == "—" else secim.split(" · ")[0].strip()

    def saatleri_ata(self, bas, bit):
        self.v_bas.set(bas)
        self.v_bit.set(bit)


class TalepFormu(ctk.CTkScrollableFrame):
    def __init__(self, master, modul, kullanici_getter, gun_getter, gun_ata, **kwargs):
        super().__init__(
            master, fg_color="transparent",
            scrollbar_button_color=RENK["cizgi"],
            scrollbar_button_hover_color=RENK["vurgu"],
            **kwargs,
        )
        self.modul = modul
        self.kullanici_getter = kullanici_getter
        self.gun_getter = gun_getter
        self.gun_ata = gun_ata
        self.v_tarih = ctk.StringVar(value=gun_getter())
        self.kalem_sayisi = 2
        self.son_talep = None
        self._plan = None
        self.satirlar = []
        self._kur()
        self.varsayilanlari_yenile()

    def _yeni_satir(self):
        s = KalemSatiri(self.kalem_cerceve, self.planla)
        secenekler = [f"{k['id']} · {k['ad']}" for k in self.modul.kaynaklar()] or ["—"]
        s.kaynaklari_ayarla(secenekler)
        bas, bit = self._varsayilan_saatler()
        s.saatleri_ata(bas, bit)
        return s

    def _kur(self):
        ust = ctk.CTkFrame(self, fg_color="transparent")
        ust.pack(fill="x", pady=(2, 6))
        self.mod = ctk.CTkSegmentedButton(
            ust, values=["Tek", "Paket"], command=self._mod_degisti, height=30,
            fg_color=RENK["kart"], selected_color=RENK["vurgu"], selected_hover_color=RENK["vurgu_koyu"],
            unselected_color=RENK["kart"], unselected_hover_color=RENK["cizgi"], font=(FONT, 12, "bold"),
        )
        self.mod.set("Tek")
        self.mod.pack(side="left")
        self.ent_tarih = kutu(ust, self.v_tarih, width=118, justify="center")
        self.ent_tarih.pack(side="right")
        self.ent_tarih.bind("<Return>", lambda e: self._tarih_uygula())
        self.ent_tarih.bind("<FocusOut>", lambda e: self._tarih_uygula())
        yazi(ust, "Gün").pack(side="right", padx=(0, 8))
        self.v_tarih.trace_add("write", lambda *a: self.planla())

        baslik = ctk.CTkFrame(self, fg_color="transparent")
        baslik.pack(fill="x")
        baslik.columnconfigure(0, weight=1)
        yazi(baslik, "Kaynak", font=(FONT, 11)).grid(row=0, column=0, sticky="w")
        yazi(baslik, "Başlangıç", font=(FONT, 11), width=92).grid(row=0, column=1, padx=(6, 0))
        yazi(baslik, "Bitiş", font=(FONT, 11), width=92).grid(row=0, column=2, padx=(6, 0))

        self.kalem_cerceve = ctk.CTkFrame(self, fg_color="transparent")
        self.kalem_cerceve.pack(fill="x")

        self.paket_bar = ctk.CTkFrame(self, fg_color="transparent")
        dugme(self.paket_bar, "+ Kalem", lambda: self._kalem_degistir(1), height=28, width=90).pack(side="left")
        dugme(self.paket_bar, "− Kalem", lambda: self._kalem_degistir(-1), height=28, width=90).pack(side="left", padx=6)

        fiyat = ctk.CTkFrame(self, fg_color=RENK["kart"], corner_radius=10)
        fiyat.pack(fill="x", pady=(6, 6))
        fiyat_ust = ctk.CTkFrame(fiyat, fg_color="transparent")
        fiyat_ust.pack(fill="x", padx=10, pady=(6, 2))
        yazi(fiyat_ust, "TAHMİNİ ÜCRET", font=(FONT, 10, "bold")).pack(side="left")
        self.lbl_fiyat = ctk.CTkLabel(fiyat_ust, text="—", font=(FONT, 18, "bold"), text_color=RENK["vurgu"])
        self.lbl_fiyat.pack(side="right")
        self.lbl_fiyat_not = yazi(fiyat, "", wraplength=360, justify="left")
        self.lbl_fiyat_not.pack(anchor="w", padx=10, pady=(0, 6))

        self.btn_rezerve = dugme(self, "Rezerve Et", self.gonder, "birincil", height=36)
        self.btn_rezerve.pack(fill="x", pady=(2, 0))

        self.sonuc_alani = ctk.CTkFrame(self, fg_color=RENK["kart"], corner_radius=10)
        self.sonuc_alani.pack(fill="x", pady=(8, 0))
        self.btn_bekleme = dugme(self, "⏳  Bu aralık için bekleme kaydı aç", self.bekleme_ac, height=34)

    def _satirlari_diz(self):
        for s in self.satirlar:
            s.pack_forget()
        n = 1 if self.mod.get() == "Tek" else len(self.satirlar)
        for s in self.satirlar[:n]:
            s.pack(fill="x", pady=3)
        if self.mod.get() == "Paket":
            self.paket_bar.pack(fill="x", pady=(2, 0), after=self.kalem_cerceve)
        else:
            self.paket_bar.pack_forget()

    def _mod_degisti(self, _):
        if self.mod.get() == "Paket":
            self.btn_rezerve.configure(text="Paketi Rezerve Et")
        else:
            self.btn_rezerve.configure(text="Rezerve Et")
        self._satirlari_diz()
        self.planla()

    def _kalem_degistir(self, fark):
        if fark > 0:
            self.satirlar.append(self._yeni_satir())
        elif fark < 0 and len(self.satirlar) > 1:
            eski = self.satirlar.pop()
            eski.destroy()
        self.kalem_sayisi = len(self.satirlar)
        self._satirlari_diz()
        self.planla()

    def _tarih_uygula(self):
        gun = self.v_tarih.get().strip()
        try:
            datetime.strptime(gun, "%Y-%m-%d")
        except ValueError:
            return
        self.gun_ata(gun)

    def gun_yaz(self, gun):
        if self.v_tarih.get() != gun:
            self.v_tarih.set(gun)

    def listeleri_guncelle(self):
        secenekler = [f"{k['id']} · {k['ad']}" for k in self.modul.kaynaklar()] or ["—"]
        for s in self.satirlar:
            s.kaynaklari_ayarla(secenekler)

    def varsayilanlari_yenile(self):
        self.v_tarih.set(self.gun_getter())
        while len(self.satirlar) > 2:
            self.satirlar.pop().destroy()
        while len(self.satirlar) < 2:
            self.satirlar.append(self._yeni_satir())
        bas, bit = self._varsayilan_saatler()
        for s in self.satirlar:
            s.saatleri_ata(bas, bit)
        self.kalem_sayisi = 2
        self.mod.set("Tek")
        self.btn_rezerve.configure(text="Rezerve Et")
        self._satirlari_diz()
        self.listeleri_guncelle()
        self._bekleme_gizle()
        self._sonuc_goster([("Fiyat, alanlar değiştikçe otomatik hesaplanır.", RENK["soluk"])])
        self.planla()

    def _varsayilan_saatler(self):
        saat = self.modul.saat()
        if saat is None:
            return "11:00", "13:00"
        bas_dk = ((saat.hour * 60 + saat.minute + 14) // 15) * 15
        bas_dk = min(max(bas_dk, sbt.REZERVASYON_BASLANGIC * 60), (sbt.REZERVASYON_BITIS - 1) * 60)
        bit_dk = min(bas_dk + 60, sbt.REZERVASYON_BITIS * 60)
        return f"{bas_dk // 60:02d}:{bas_dk % 60:02d}", f"{bit_dk // 60:02d}:{bit_dk % 60:02d}"

    def _kalemler(self):
        tarih = self.v_tarih.get().strip()
        n = 1 if self.mod.get() == "Tek" else self.kalem_sayisi
        return [
            {
                "kaynak": s.kaynak_id(),
                "baslangic": f"{tarih}T{s.v_bas.get().strip()}",
                "bitis": f"{tarih}T{s.v_bit.get().strip()}",
            }
            for s in self.satirlar[:n]
        ]

    def planla(self, *_):
        if self._plan:
            self.after_cancel(self._plan)
        self._plan = self.after(250, self.onizle)
        self._bekleme_gizle()

    def onizle(self):
        self._plan = None
        if self.modul.sistem is None:
            return
        kid = self.kullanici_getter() or ""
        paket = self.mod.get() == "Paket"
        toplam, hatalar = 0, []
        for i, kalem in enumerate(self._kalemler()):
            bas, bit = kalem.get("baslangic", ""), kalem.get("bitis", "")
            if len(bas) < 16 or len(bit) < 16:
                return
            try:
                datetime.fromisoformat(bas)
                datetime.fromisoformat(bit)
            except ValueError:
                return
            s = self.modul.komut({"komut": "fiyat", "kullanici": kid, **kalem}, kaydet=False)
            if s.get("durum") == "TAMAM":
                toplam += s.get("ucret", 0)
            else:
                hatalar.append((i + 1, s.get("kod", "?")))
        if not hatalar:
            self.lbl_fiyat.configure(text=f"{toplam} KP", text_color=RENK["vurgu"])
            self.lbl_fiyat_not.configure(text="Paket toplamı" if paket else "Talep geçerli görünüyor")
        else:
            self.lbl_fiyat.configure(text="—", text_color=RENK["soluk"])
            if paket:
                self.lbl_fiyat_not.configure(text="  ".join(f"Kalem {i}: {kod}" for i, kod in hatalar))
            else:
                kod = hatalar[0][1]
                self.lbl_fiyat_not.configure(text=f"{kod}")

    def _sonuc_goster(self, satirlar):
        for w in self.sonuc_alani.winfo_children():
            w.destroy()
        for i, (metin, renk) in enumerate(satirlar):
            ctk.CTkLabel(
                self.sonuc_alani, text=metin, text_color=renk, wraplength=360, justify="left", anchor="w",
                font=(FONT, 13, "bold") if i == 0 else (FONT, 12),
            ).pack(anchor="w", padx=12, pady=(10 if i == 0 else 0, 10 if i == len(satirlar) - 1 else 2))

    def _bekleme_gizle(self):
        self.btn_bekleme.pack_forget()
        self.son_talep = None

    @staticmethod
    def _kisa(k):
        return f"{k['kaynak']} {k['baslangic'][11:16]}–{k['bitis'][11:16]}"

    def gonder(self):
        kid = self.kullanici_getter() or ""
        kalemler = self._kalemler()
        if self.mod.get() == "Tek":
            s = self.modul.komut({"komut": "rezervasyon", "kullanici": kid, **kalemler[0]})
            if s.get("durum") == "TAMAM":
                self._sonuc_goster([
                    (f"✔  {s.get('rezervasyon_id')} oluşturuldu", RENK["iyi"]),
                    (f"Ücret {s.get('ucret')} KP · yeni bakiye {s.get('bakiye')} KP", RENK["metin"]),
                ])
                return
            kod = s.get("kod", "?")
            self._sonuc_goster([(f"✘  {kod}", RENK["kotu"])])
            if kod in BEKLEME_KODLARI:
                self.son_talep = {"kullanici": kid, **kalemler[0]}
                self.btn_bekleme.pack(fill="x", pady=(8, 0))
            return

        s = self.modul.komut({"komut": "paket", "kullanici": kid, "kalemler": kalemler})
        if s.get("durum") == "TAMAM":
            satirlar = [
                (f"✔  {s.get('paket_id')} oluşturuldu · toplam {s.get('toplam')} KP", RENK["iyi"]),
                (f"Yeni bakiye {s.get('bakiye')} KP", RENK["metin"]),
            ]
            for rid, ucret, k in zip(s.get("rezervasyonlar", []), s.get("ucretler", []), kalemler):
                satirlar.append((f"{rid}  ·  {self._kisa(k)}  ·  {ucret} KP", RENK["metin"]))
            self._sonuc_goster(satirlar)
            return
        kod = s.get("kod", "?")
        satirlar = [(f"✘  {kod}", RENK["kotu"])]
        for kalem in s.get("kalemler", []):
            sira = kalem.get("sira", 0)
            ad = f"Kalem {sira + 1} · {self._kisa(kalemler[sira])}" if sira < len(kalemler) else f"Kalem {sira + 1}"
            if kalem.get("durum") == "TAMAM":
                satirlar.append((f"✔  {ad}  geçti", RENK["iyi"]))
            else:
                kk = kalem.get("kod", "?")
                satirlar.append((f"✘  {ad} · {kk}", RENK["kotu"]))
        self._sonuc_goster(satirlar)

    def bekleme_ac(self):
        if not self.son_talep:
            return
        s = self.modul.komut({"komut": "bekleme", **self.son_talep})
        self._bekleme_gizle()
        if s.get("durum") == "TAMAM":
            self._sonuc_goster([
                (f"⏳  {s.get('bekleme_id')} kaydedildi", RENK["iyi"]),
                (f"Bekleme listesinde sıra: {s.get('sira')}", RENK["metin"]),
            ])
        else:
            kod = s.get("kod", "?")
            self._sonuc_goster([(f"✘  {kod}", RENK["kotu"])])
