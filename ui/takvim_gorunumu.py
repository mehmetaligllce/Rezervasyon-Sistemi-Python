import tkinter as tk
from datetime import datetime, timedelta
import customtkinter as ctk

import core.sabitler as sbt
from core.takvim import takvim_verisi_uret

FONT = "Segoe UI"

RENK = {
    "zemin": "#1E3A34",      
    "panel": "#27493F",      
    "kart": "#315A4D",       
    "cizgi": "#3A6060",      
    "metin": "#E6F2EC",      
    "soluk": "#E2D2EE",      
    "vurgu": "#B14F64",      
    "vurgu_koyu": "#963F52", 
    "iyi": "#10B981",        
    "kotu": "#EF4444",      
    "uyari": "#F59E0B",      
}

DURUM_RENKLERI = {
    "ONAYLI": "#10B981",      
    "KULLANIMDA": "#2563EB",   
    "TAMAMLANDI": "#64748B",   
    "GELMEDI": "#701A75",      
    "IPTAL": "#FF6347",        
    "BAKIM": "#FF8C00",        
    "HAZIRLIK": "#06B6D4",     
}

GUNLER = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]


class TakvimGorunumu(ctk.CTkFrame):
    SOL = 150
    UST = 42
    SAG = 14

    def __init__(self, master, modul, on_secim=None, on_gun_degisti=None, **kwargs):
        super().__init__(master, corner_radius=14, fg_color=RENK["panel"], **kwargs)
        self.modul = modul
        self.on_secim = on_secim
        self.on_gun_degisti = on_gun_degisti
        self.secilen_gun = self._saat_gunu()
        self.secili_id = None
        self.kutular = []
        self._ust_bar()
        self._tuval()
        self._lejant()

    def _saat_gunu(self):
        saat = self.modul.saat()
        return (saat or datetime.now()).strftime("%Y-%m-%d")

    def _dugme(self, parent, metin, komut, genislik=36):
        return ctk.CTkButton(
            parent, text=metin, width=genislik, height=30, corner_radius=8,
            fg_color=RENK["kart"], hover_color=RENK["cizgi"], text_color=RENK["metin"],
            font=(FONT, 13, "bold"), command=komut,
        )

    def _ust_bar(self):
        bar = ctk.CTkFrame(self, fg_color="transparent")
        bar.pack(fill="x", padx=16, pady=(14, 6))
        self._dugme(bar, "‹", self._onceki).pack(side="left")
        self.lbl_gun = ctk.CTkLabel(
            bar, text="", width=230, font=(FONT, 16, "bold"), text_color=RENK["metin"]
        )
        self.lbl_gun.pack(side="left", padx=6)
        self._dugme(bar, "›", self._sonraki).pack(side="left")
        self._dugme(bar, "Bugün", self._bugun, 72).pack(side="left", padx=(10, 0))
        ctk.CTkLabel(
            bar, text="Kutuya tıkla → detay ve eylemler", font=(FONT, 12), text_color=RENK["soluk"]
        ).pack(side="right")
        self._gun_yaz()

    def _tuval(self):
        cerceve = ctk.CTkFrame(self, fg_color=RENK["zemin"], corner_radius=10)
        cerceve.pack(fill="both", expand=True, padx=16, pady=6)
        self.canvas = tk.Canvas(cerceve, bg=RENK["zemin"], bd=0, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=2, pady=2)
        self.canvas.bind("<Configure>", lambda e: self.ciz())
        self.canvas.bind("<Button-1>", self._tikla)
        self.canvas.bind("<Motion>", self._gezin)

    def _lejant(self):
        satir = ctk.CTkFrame(self, fg_color="transparent")
        satir.pack(fill="x", padx=16, pady=(2, 12))
        for durum, renk in DURUM_RENKLERI.items():
            ctk.CTkLabel(
                satir, text="●", width=12, text_color=renk, font=(FONT, 12)
            ).pack(side="left", padx=(0, 2))
            ctk.CTkLabel(
                satir, text=durum.capitalize(), text_color=RENK["soluk"], font=(FONT, 11)
            ).pack(side="left", padx=(0, 12))

    def _gun_yaz(self):
        d = datetime.strptime(self.secilen_gun, "%Y-%m-%d")
        self.lbl_gun.configure(text=f"{self.secilen_gun}  ·  {GUNLER[d.weekday()]}")

    def gun_ata(self, gun):
        self.secilen_gun = gun
        self._gun_yaz()
        self.ciz()
        if self.on_gun_degisti:
            self.on_gun_degisti(gun)

    def _kaydir(self, gun_sayisi):
        d = datetime.strptime(self.secilen_gun, "%Y-%m-%d") + timedelta(days=gun_sayisi)
        self.gun_ata(d.strftime("%Y-%m-%d"))

    def _onceki(self):
        self._kaydir(-1)

    def _sonraki(self):
        self._kaydir(1)

    def _bugun(self):
        self.gun_ata(self._saat_gunu())

    def _yuvarlak(self, x1, y1, x2, y2, r=6, **kw):
        r = max(1, min(r, (x2 - x1) / 2, (y2 - y1) / 2))
        p = [x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r, x2, y2 - r, x2, y2,
             x2 - r, y2, x1 + r, y2, x1, y2, x1, y2 - r, x1, y1 + r, x1, y1]
        return self.canvas.create_polygon(p, smooth=True, **kw)

    def ciz(self):
        c = self.canvas
        c.delete("all")
        self.kutular = []
        w, h = c.winfo_width(), c.winfo_height()
        if w < 300 or h < 120:
            return
        sistem = self.modul.sistem
        if sistem is None:
            c.create_text(w / 2, h / 2, text="Başlangıç dosyası seçilmedi",
                          fill=RENK["soluk"], font=(FONT, 13))
            return

        bas_saat, bit_saat = sbt.REZERVASYON_BASLANGIC, sbt.REZERVASYON_BITIS
        toplam = (bit_saat - bas_saat) * 60
        zaman_w = w - self.SOL - self.SAG

        def x_of(dk):
            return self.SOL + dk / toplam * zaman_w

        takvim = takvim_verisi_uret(sistem, self.secilen_gun)
        kaynaklar = self.modul.kaynaklar()
        alt = {
            k["id"]: max([o.get("alt_satir", 0) for o in takvim.get(k["id"], [])], default=0) + 1
            for k in kaynaklar
        }
        birim = max(30, min(58, (h - self.UST - 6) / (sum(alt.values()) or 1)))

        c.create_rectangle(0, 0, w, self.UST, fill=RENK["panel"], outline="")
        c.create_text(14, self.UST / 2, anchor="w", text="KAYNAK",
                      fill=RENK["soluk"], font=(FONT, 9, "bold"))

        y = self.UST
        satir_yer = {}
        for i, k in enumerate(kaynaklar):
            sat_h = birim * alt[k["id"]]
            satir_yer[k["id"]] = (y, sat_h)
            c.create_rectangle(0, y, w, y + sat_h,
                               fill="#1E3A34" if i % 2 == 0 else "#234339", outline="")
            c.create_text(14, y + sat_h / 2 - 8, anchor="w", text=k["id"],
                          fill=RENK["metin"], font=(FONT, 10, "bold"))
            c.create_text(14, y + sat_h / 2 + 8, anchor="w", text=k["ad"][:20],
                          fill=RENK["soluk"], font=(FONT, 8))
            y += sat_h
        y_son = y

        for dk in range(0, toplam + 1, 15):
            x = x_of(dk)
            if dk % 60 == 0:
                c.create_line(x, self.UST - 12, x, y_son, fill="#38405A")
                saat = bas_saat + dk // 60
                if saat < bit_saat:
                    c.create_text(x + 5, 14, anchor="w", text=f"{saat:02d}:00",
                                  fill=RENK["soluk"], font=(FONT, 9, "bold"))
                else:
                    c.create_text(x - 3, 14, anchor="e", text=f"{saat:02d}:00",
                                  fill=RENK["soluk"], font=(FONT, 9, "bold"))
            elif dk % 30 == 0:
                c.create_line(x, self.UST - 8, x, y_son, fill="#2C3247")
            else:
                c.create_line(x, self.UST - 5, x, y_son, fill="#212637")

        for k in kaynaklar:
            kid = k["id"]
            y0, _ = satir_yer[kid]
            for oge in takvim.get(kid, []):
                self._kutu_ciz(oge, kid, y0, birim, bas_saat, toplam, x_of)

        saat = self.modul.saat()
        if saat and saat.strftime("%Y-%m-%d") == self.secilen_gun:
            dk = (saat.hour - bas_saat) * 60 + saat.minute
            if 0 <= dk <= toplam:
                x = x_of(dk)
                c.create_line(x, self.UST - 12, x, y_son, fill=RENK["kotu"], width=2)
                self._yuvarlak(x - 22, self.UST - 22, x + 22, self.UST - 6, 5, fill=RENK["kotu"], outline="")
                c.create_text(x, self.UST - 14, text=saat.strftime("%H:%M"),
                              fill="#FFFFFF", font=(FONT, 8, "bold"))

    def _kutu_ciz(self, oge, kid, y0, birim, bas_saat, toplam, x_of):
        try:
            bas = datetime.fromisoformat(oge["baslangic"])
            bit = datetime.fromisoformat(oge["bitis"])
        except Exception:
            return
        bas_dk = max(0, min(toplam, (bas.hour - bas_saat) * 60 + bas.minute))
        bit_dk = max(0, min(toplam, (bit.hour - bas_saat) * 60 + bit.minute))
        if bit_dk <= bas_dk:
            return
        x1, x2 = x_of(bas_dk) + 1, x_of(bit_dk) - 1
        y1 = y0 + oge.get("alt_satir", 0) * birim + 4
        y2 = y1 + birim - 8

        tur = oge.get("tur")
        stipple = ""
        kenar = RENK["zemin"]
        dash = None
        genislik = 1
        if tur == "REZERVASYON":
            durum = oge.get("durum", "ONAYLI")
            renk = DURUM_RENKLERI.get(durum, "#2FB67C")
            ilk = f"{oge.get('id')} · {oge.get('kullanici', '')}"
            metin = f"{ilk}\n{durum}" if (y2 - y1) >= 30 else ilk
            if durum in ("IPTAL", "GELMEDI"):
                kenar, dash = "#C9CEDD", (3, 2)
            elif durum == "TAMAMLANDI":
                kenar = "#3E4459"
            if oge.get("id") == self.secili_id:
                kenar, genislik, dash = "#FFFFFF", 2, None
        elif tur == "BAKIM":
            renk, stipple, metin = DURUM_RENKLERI["BAKIM"], "gray50", "BAKIM"
        elif tur == "HAZIRLIK":
            renk, stipple, metin = DURUM_RENKLERI["HAZIRLIK"], "gray50", "HAZIRLIK"
        else:
            renk, metin = "#555B70", str(tur)

        opsiyon = {"fill": renk, "outline": kenar, "width": genislik}
        if stipple:
            opsiyon["stipple"] = stipple
        if dash:
            opsiyon["dash"] = dash
        self._yuvarlak(x1, y1, x2, y2, 6, **opsiyon)

        max_kar = int((x2 - x1 - 10) / 6.3)
        if max_kar >= 3:
            satirlar = [s[:max_kar] for s in metin.split("\n")]
            yazi_renk = "#0F172A" if oge.get("durum") == "ONAYLI" else "#FFFFFF"
            self.canvas.create_text(x1 + 7, (y1 + y2) / 2, anchor="w", text="\n".join(satirlar),
                                    fill=yazi_renk, font=(FONT, 8, "bold"))
        self.kutular.append((x1, y1, x2, y2, dict(oge, kaynak=oge.get("kaynak", kid))))

    def _kutu_bul(self, x, y):
        for x1, y1, x2, y2, oge in reversed(self.kutular):
            if x1 <= x <= x2 and y1 <= y <= y2:
                return oge
        return None

    def _gezin(self, e):
        self.canvas.configure(cursor="hand2" if self._kutu_bul(e.x, e.y) else "")

    def _tikla(self, e):
        oge = self._kutu_bul(e.x, e.y)
        if oge is None:
            return
        self.secili_id = oge.get("id") if oge.get("tur") == "REZERVASYON" else None
        self.ciz()
        if self.on_secim:
            self.on_secim(oge)
