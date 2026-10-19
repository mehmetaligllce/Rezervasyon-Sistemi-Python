import sys
import os

PROJE_KOK = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJE_KOK not in sys.path:
    sys.path.insert(0, PROJE_KOK)

import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
from datetime import datetime

from json_io.dosya_okuma import baslangic_json_okuma
from ui.takvim_gorunumu import TakvimGorunumu
from ui.talep_formu import TalepFormu

class KampusRezervasyonApp(ctk.CTk):
    """
    Kampüs Kaynak Rezervasyon Sistemi - Masaüstü Uygulaması
    """
    def __init__(self, baslangic_yolu=None):
        super().__init__()

        self.title("Kampüs Kaynak Rezervasyon Sistemi")
        self.geometry("1280x760")
        self.minsize(1024, 640)

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Sistem Durumu (Bellekte tutulur)
        self.baslangic_veri = {}
        self.rezervasyonlar = []
        self.simule_saat = datetime(2027, 3, 8, 8, 0)

        # Varsayılan başlangıç dosyasını yükle
        if not baslangic_yolu:
            # Öncelikli olarak yeni örneğe, yoksa ana dizindekine bak
            if os.path.exists("Örnek/yeni_ornek/Örnek/baslangic.json"):
                baslangic_yolu = "Örnek/yeni_ornek/Örnek/baslangic.json"
            elif os.path.exists("Örnek/baslangic.json"):
                baslangic_yolu = "Örnek/baslangic.json"

        if baslangic_yolu and os.path.exists(baslangic_yolu):
            self._baslangic_yukle(baslangic_yolu)

        self._arayuz_kur()

    def _baslangic_yukle(self, yol):
        try:
            self.baslangic_veri = baslangic_json_okuma(yol)
            self.simule_saat = datetime.fromisoformat(self.baslangic_veri["saat"])
            self.rezervasyonlar = []
        except Exception as e:
            messagebox.showerror("Hata", f"Başlangıç dosyası yüklenemedi:\n{e}")

    def _arayuz_kur(self):
        # 1. Üst Başlık ve Dosya Seçim Barı
        ust_bar = ctk.CTkFrame(self, height=54, corner_radius=0, fg_color="#181818")
        ust_bar.pack(fill="x", side="top")

        lbl_logo = ctk.CTkLabel(
            ust_bar, text="🏛 KAMPÜS KAYNAK REZERVASYON",
            font=ctk.CTkFont(size=16, weight="bold"), text_color="#3B8ED0"
        )
        lbl_logo.pack(side="left", padx=20, pady=12)

        self.btn_dosya_sec = ctk.CTkButton(
            ust_bar, text="📁 Başlangıç Dosyası Seç", width=160, height=32,
            fg_color="#2D3748", hover_color="#4A5568", command=self._dosya_sec_diyalog
        )
        self.btn_dosya_sec.pack(side="left", padx=10, pady=12)

        self.lbl_durum_bilgi = ctk.CTkLabel(
            ust_bar, text=f"Saat: {self.simule_saat.strftime('%Y-%m-%d %H:%M')}",
            font=ctk.CTkFont(size=14, weight="bold"), text_color="#A0AEC0"
        )
        self.lbl_durum_bilgi.pack(side="right", padx=20, pady=12)

        # 2. Ana Gövde (Sol: Takvim, Sağ: Talep Formu)
        govde = ctk.CTkFrame(self, fg_color="transparent")
        govde.pack(fill="both", expand=True, padx=12, pady=12)

        # Sol Panel (Takvim)
        self.takvim_paneli = TakvimGorunumu(
            govde,
            baslangic_veri=self.baslangic_veri,
            rezervasyonlar=self.rezervasyonlar,
            get_saat_fn=lambda: self.simule_saat,
            on_rezervasyon_secildi=self._rezervasyon_detay_goster
        )
        self.takvim_paneli.pack(side="left", fill="both", expand=True, padx=(0, 8))

        # Sağ Panel (Talep Formu)
        self.talep_paneli = TalepFormu(
            govde,
            baslangic_veri=self.baslangic_veri,
            rezervasyonlar=self.rezervasyonlar,
            get_saat_fn=lambda: self.simule_saat,
            on_rezervasyon_callback=self._rezervasyon_eklendi_callback,
            width=360
        )
        self.talep_paneli.pack(side="right", fill="y", padx=(8, 0))

    def _dosya_sec_diyalog(self):
        yol = filedialog.askopenfilename(
            title="Başlangıç Dosyası Seç (baslangic.json)",
            filetypes=[("JSON Dosyası", "*.json"), ("Tüm Dosyalar", "*.*")]
        )
        if yol:
            self._baslangic_yukle(yol)
            self.lbl_durum_bilgi.configure(text=f"Saat: {self.simule_saat.strftime('%Y-%m-%d %H:%M')}")
            self.takvim_paneli.baslangic_veri = self.baslangic_veri
            self.takvim_paneli.rezervasyonlar = self.rezervasyonlar
            self.takvim_paneli.secilen_gun = self.simule_saat.strftime("%Y-%m-%d")
            self.takvim_paneli.lbl_gun.configure(text=self.takvim_paneli.secilen_gun)
            self.takvim_paneli.ciz()

            self.talep_paneli.baslangic_veri = self.baslangic_veri
            self.talep_paneli.rezervasyonlar = self.rezervasyonlar
            self.talep_paneli.listeleri_guncelle()

    def _rezervasyon_eklendi_callback(self, yeni_r):
        """Form üzerinden rezervasyon başarıyla yapıldığında takvimi yeniler"""
        self.takvim_paneli.ciz()

    def _rezervasyon_detay_goster(self, oge):
        """Takvimde bir kutuya tıklandığında detay penceresi açar"""
        tur = oge.get("tur")
        if tur == "REZERVASYON":
            msg = (
                f"Rezervasyon No: {oge.get('id')}\n"
                f"Kullanıcı: {oge.get('kullanici')}\n"
                f"Kaynak: {oge.get('kaynak')}\n"
                f"Zaman: {oge.get('baslangic')}  ➜  {oge.get('bitis')}\n"
                f"Durum: {oge.get('durum')}\n"
                f"Ücret: {oge.get('ucret', '-')} KP"
            )
            messagebox.showinfo("Rezervasyon Detayı", msg)
        elif tur == "BAKIM":
            msg = f"Bakım Penceresi\nZaman: {oge.get('baslangic')}  ➜  {oge.get('bitis')}"
            messagebox.showinfo("Bakım Detayı", msg)
        elif tur == "HAZIRLIK":
            msg = (
                f"Hazırlık / Soğuma Süresi\n"
                f"Rezervasyon: {oge.get('rezervasyon_id')}\n"
                f"Zaman: {oge.get('baslangic')}  ➜  {oge.get('bitis')}"
            )
            messagebox.showinfo("Hazırlık Detayı", msg)

def baslat():
    app = KampusRezervasyonApp()
    app.mainloop()

if __name__ == "__main__":
    baslat()
