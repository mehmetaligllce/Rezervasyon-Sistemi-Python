import tkinter as tk
import customtkinter as ctk
from datetime import datetime, timedelta
from core.takvim import takvim_verisi_uret
import core.sabitler as sbt

DURUM_RENKLERI = {
    "ONAYLI": "#2ECC71",       # Yeşil
    "KULLANIMDA": "#3498DB",   # Mavi
    "TAMAMLANDI": "#4A6572",   # Nötr Koyu Mavi/Gri
    "GELMEDI": "#E74C3C",      # Kırmızı
    "IPTAL": "#7F8C8D",        # Soluk Gri
    "BAKIM": "#E67E22",        # Turuncu
    "HAZIRLIK": "#F39C12"      # Sarı/Hardal
}

class TakvimGorunumu(ctk.CTkFrame):
    """
    08:00 - 22:00 Kaynak Takvimi Bileşeni
    - Saat ekseni (15 dk adımlar ve saat başı çizgileri)
    - Her kaynak için ayrı satır (çakışmalarda alt satır)
    - Durum renkleri, bakım ve hazırlık kutuları
    - Simüle saatin kırmızı dikey çizgiyle gösterimi
    - Kutuya tıklandığında detay gösterimi
    """
    def __init__(self, master, baslangic_veri: dict, rezervasyonlar: list, get_saat_fn, on_rezervasyon_secildi=None, **kwargs):
        super().__init__(master, corner_radius=12, **kwargs)
        self.baslangic_veri = baslangic_veri
        self.rezervasyonlar = rezervasyonlar
        self.get_saat_fn = get_saat_fn
        self.on_rezervasyon_secildi = on_rezervasyon_secildi

        # Başlangıçta simüle saatin gününü seç
        suanki = self.get_saat_fn()
        self.secilen_gun = suanki.strftime("%Y-%m-%d") if isinstance(suanki, datetime) else str(suanki)[:10]

        self._ust_bar_olustur()
        self._cizim_alanini_olustur()
        self._lejant_olustur()

        # İlk çizim
        self.after(100, self.ciz)

    def _ust_bar_olustur(self):
        ust_frame = ctk.CTkFrame(self, fg_color="transparent")
        ust_frame.pack(fill="x", padx=16, pady=(12, 6))

        # Gün değiştirme butonları
        self.btn_onceki = ctk.CTkButton(ust_frame, text="◀ Önceki Gün", width=95, height=30, command=self._onceki_gun)
        self.btn_onceki.pack(side="left", padx=(0, 6))

        self.lbl_gun = ctk.CTkLabel(ust_frame, text=self.secilen_gun, font=ctk.CTkFont(size=16, weight="bold"))
        self.lbl_gun.pack(side="left", padx=8)

        self.btn_sonraki = ctk.CTkButton(ust_frame, text="Sonraki Gün ▶", width=95, height=30, command=self._sonraki_gun)
        self.btn_sonraki.pack(side="left", padx=(6, 12))

        self.btn_bugun = ctk.CTkButton(
            ust_frame, text="Bugün", width=70, height=30, fg_color="#4A5568", hover_color="#2D3748",
            command=self._bugune_git
        )
        self.btn_bugun.pack(side="left")

        # Sağ tarafta simüle saat bilgisi
        self.lbl_saat_bilgi = ctk.CTkLabel(
            ust_frame, text="", font=ctk.CTkFont(size=13, weight="bold"), text_color="#3B8ED0"
        )
        self.lbl_saat_bilgi.pack(side="right", padx=8)

    def _cizim_alanini_olustur(self):
        # Kaydırılabilir canvas çerçevesi
        canvas_frame = ctk.CTkFrame(self, fg_color="#1E1E1E", corner_radius=8)
        canvas_frame.pack(fill="both", expand=True, padx=16, pady=6)

        self.canvas = tk.Canvas(
            canvas_frame, bg="#1A1A1A", bd=0, highlightthickness=0
        )
        self.canvas.pack(fill="both", expand=True, padx=4, pady=4)
        self.canvas.bind("<Configure>", lambda e: self.ciz())
        self.canvas.bind("<Button-1>", self._canvas_tiklandi)

    def _lejant_olustur(self):
        lejant_frame = ctk.CTkFrame(self, fg_color="transparent")
        lejant_frame.pack(fill="x", padx=16, pady=(4, 10))

        ctk.CTkLabel(lejant_frame, text="Durumlar:", font=ctk.CTkFont(size=12, weight="bold")).pack(side="left", padx=(0, 8))
        for durum, renk in DURUM_RENKLERI.items():
            kutu = ctk.CTkLabel(
                lejant_frame, text=f" ■ {durum} ", text_color=renk, font=ctk.CTkFont(size=11, weight="bold")
            )
            kutu.pack(side="left", padx=4)

    def _onceki_gun(self):
        d = datetime.strptime(self.secilen_gun, "%Y-%m-%d") - timedelta(days=1)
        self.secilen_gun = d.strftime("%Y-%m-%d")
        self.lbl_gun.configure(text=self.secilen_gun)
        self.ciz()

    def _sonraki_gun(self):
        d = datetime.strptime(self.secilen_gun, "%Y-%m-%d") + timedelta(days=1)
        self.secilen_gun = d.strftime("%Y-%m-%d")
        self.lbl_gun.configure(text=self.secilen_gun)
        self.ciz()

    def _bugune_git(self):
        suanki = self.get_saat_fn()
        self.secilen_gun = suanki.strftime("%Y-%m-%d") if isinstance(suanki, datetime) else str(suanki)[:10]
        self.lbl_gun.configure(text=self.secilen_gun)
        self.ciz()

    def ciz(self):
        """Takvimi sıfırdan çizer"""
        self.canvas.delete("all")
        self.tiklanabilir_kutular = []

        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w < 100 or h < 100:
            return

        # Üst simüle saat bilgisini güncelle
        suanki_saat = self.get_saat_fn()
        suanki_str = suanki_saat.strftime("%Y-%m-%d %H:%M") if isinstance(suanki_saat, datetime) else str(suanki_saat)
        self.lbl_saat_bilgi.configure(text=f"Simüle Saat: {suanki_str}")

        # Zaman aralığı sabitleri
        SOL_BASLIK_W = 140
        UST_ZAMAN_H = 34
        ZAMAN_W = w - SOL_BASLIK_W - 20
        if ZAMAN_W <= 0:
            return

        BAS_SAAT = sbt.REZERVASYON_BASLANGIC  # 8
        BIT_SAAT = sbt.REZERVASYON_BITIS      # 22
        TOPLAM_DAKIKA = (BIT_SAAT - BAS_SAAT) * 60  # 14 * 60 = 840 dk

        # Zaman cetveli başlığı (08:00 - 22:00)
        self.canvas.create_rectangle(0, 0, w, UST_ZAMAN_H, fill="#252526", outline="")
        self.canvas.create_text(
            SOL_BASLIK_W // 2, UST_ZAMAN_H // 2, text="KAYNAK", fill="#CCCCCC", font=("Segoe UI", 10, "bold")
        )

        for saat in range(BAS_SAAT, BIT_SAAT + 1):
            dk = (saat - BAS_SAAT) * 60
            x = SOL_BASLIK_W + (dk / TOPLAM_DAKIKA) * ZAMAN_W
            # Saat başı metni
            if saat < BIT_SAAT:
                self.canvas.create_text(
                    x + 18, UST_ZAMAN_H // 2, text=f"{saat:02d}:00", fill="#888888", font=("Segoe UI", 9)
                )
            # Dikey kılavuz çizgisi
            self.canvas.create_line(x, UST_ZAMAN_H, x, h, fill="#333333", dash=(2, 2))

        # Takvim verisini core'dan al
        takvim_verisi = takvim_verisi_uret(self.baslangic_veri, self.rezervasyonlar, self.secilen_gun)
        kaynaklar = self.baslangic_veri.get("kaynaklar", [])

        SATIR_TABAN_H = 46
        y_cursor = UST_ZAMAN_H

        for k in kaynaklar:
            kid = k["id"]
            ogeler = takvim_verisi.get(kid, [])

            # Maksimum alt satır sayısını bul
            max_alt = max([o.get("alt_satir", 0) for o in ogeler], default=0)
            satir_h = SATIR_TABAN_H * (max_alt + 1)

            # Kaynak arka planı ve sol etiketi
            self.canvas.create_rectangle(0, y_cursor, w, y_cursor + satir_h, fill="#202020", outline="#2D2D2D")
            self.canvas.create_text(
                12, y_cursor + satir_h // 2, anchor="w",
                text=f"{kid}\n{k['ad']}", fill="#E0E0E0", font=("Segoe UI", 9, "bold")
            )
            self.canvas.create_line(SOL_BASLIK_W, y_cursor, SOL_BASLIK_W, y_cursor + satir_h, fill="#383838")

            # Kaynağın bloklarını çiz
            for oge in ogeler:
                alt = oge.get("alt_satir", 0)
                kutu_y = y_cursor + alt * SATIR_TABAN_H + 5
                kutu_h = SATIR_TABAN_H - 10

                try:
                    bas_dt = datetime.fromisoformat(oge["baslangic"])
                    bit_dt = datetime.fromisoformat(oge["bitis"])
                except Exception:
                    continue

                # Dakika koordinatları
                bas_dk = (bas_dt.hour - BAS_SAAT) * 60 + bas_dt.minute
                bit_dk = (bit_dt.hour - BAS_SAAT) * 60 + bit_dt.minute

                # Sınırlar
                bas_dk = max(0, min(TOPLAM_DAKIKA, bas_dk))
                bit_dk = max(0, min(TOPLAM_DAKIKA, bit_dk))
                if bit_dk <= bas_dk:
                    continue

                x1 = SOL_BASLIK_W + (bas_dk / TOPLAM_DAKIKA) * ZAMAN_W
                x2 = SOL_BASLIK_W + (bit_dk / TOPLAM_DAKIKA) * ZAMAN_W

                tur = oge.get("tur")
                if tur == "REZERVASYON":
                    durum = oge.get("durum", "ONAYLI")
                    renk = DURUM_RENKLERI.get(durum, "#2ECC71")
                    etiket = f"{oge['id']} ({oge.get('kullanici','')}) {durum}"
                elif tur == "BAKIM":
                    renk = DURUM_RENKLERI["BAKIM"]
                    etiket = "BAKIM"
                elif tur == "HAZIRLIK":
                    renk = DURUM_RENKLERI["HAZIRLIK"]
                    etiket = "HAZIRLIK"
                else:
                    renk = "#555555"
                    etiket = tur

                # Kutuyu çiz
                rect_id = self.canvas.create_rectangle(
                    x1, kutu_y, x2, kutu_y + kutu_h, fill=renk, outline="#1A1A1A", width=1.5
                )

                # Kutunun içine yazı yaz (sığıyorsa)
                if (x2 - x1) > 40:
                    self.canvas.create_text(
                        (x1 + x2) // 2, kutu_y + kutu_h // 2,
                        text=etiket, fill="#FFFFFF", font=("Segoe UI", 8, "bold")
                    )

                self.tiklanabilir_kutular.append((x1, kutu_y, x2, kutu_y + kutu_h, oge))

            y_cursor += satir_h

        # Simüle saat çizgisi (Seçilen gün bugüne eşitse dikey kırmızı çizgi)
        if isinstance(suanki_saat, datetime) and suanki_saat.strftime("%Y-%m-%d") == self.secilen_gun:
            if BAS_SAAT <= suanki_saat.hour <= BIT_SAAT:
                sim_dk = (suanki_saat.hour - BAS_SAAT) * 60 + suanki_saat.minute
                sim_x = SOL_BASLIK_W + (sim_dk / TOPLAM_DAKIKA) * ZAMAN_W
                self.canvas.create_line(sim_x, UST_ZAMAN_H, sim_x, y_cursor, fill="#E74C3C", width=2.5)
                self.canvas.create_polygon(
                    sim_x - 5, UST_ZAMAN_H, sim_x + 5, UST_ZAMAN_H, sim_x, UST_ZAMAN_H + 8, fill="#E74C3C"
                )

    def _canvas_tiklandi(self, event):
        x, y = event.x, event.y
        for x1, y1, x2, y2, oge in getattr(self, "tiklanabilir_kutular", []):
            if x1 <= x <= x2 and y1 <= y <= y2:
                if self.on_rezervasyon_secildi:
                    self.on_rezervasyon_secildi(oge)
                break
