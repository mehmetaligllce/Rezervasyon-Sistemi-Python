import customtkinter as ctk
from datetime import datetime
from core.dogrulama import rezervasyon_dogrula
from core.yard_fonksiyonlar import ucret_hesapla

HATA_ACIKLAMALARI = {
    "BULUNAMADI": "Kullanıcı veya kaynak bulunamadı.",
    "ZAMAN_ADIMI_HATASI": "Zaman 15 dakikalık adımlara oturmuyor veya bitiş başlangıçtan önce.",
    "GECMIS_ZAMAN": "Başlangıç zamanı simüle saatten önce olamaz.",
    "CALISMA_SAATI_DISI": "Rezervasyon 08:00–22:00 çalışma saatleri içinde ve aynı günde olmalıdır.",
    "SURE_SINIRI": "Süre 30 dakikadan kısa veya rolün azami süresinden uzun.",
    "ILERI_TARIH_SINIRI": "Kullanıcının ileri tarih sınırı aşıldı.",
    "ROL_IZNI_YOK": "Kullanıcının rolü bu kaynağı kullanmaya yetkili değil.",
    "SERTIFIKA_YOK": "Kaynak için gerekli sertifika kullanıcıda bulunmuyor.",
    "BAKIM": "Seçilen zaman aralığında kaynak bakımda.",
    "KESISME": "Bu saat aralığında başka bir rezervasyon var.",
    "HAZIRLIK_IHLALI": "Önceki rezervasyonun hazırlık/soğuma süresi henüz tamamlanmadı.",
    "ARDISIK_KULLANIM": "Aynı kaynakta ardışık iki rezervasyon arasında en az 60 dk boşluk olmalıdır.",
    "BAKIYE_YETERSIZ": "Kullanıcının bakiyesi bu rezervasyon için yetersiz."
}

class TalepFormu(ctk.CTkFrame):
    """
    Rezervasyon talep formu:
    - Kullanıcı ve kaynak seçimi
    - Başlangıç ve bitiş zamanı
    - Fiyat önizleme (hata kodu ve Türkçe açıklaması ile)
    - Rezervasyon oluşturma
    """
    def __init__(self, master, baslangic_veri: dict, rezervasyonlar: list, get_saat_fn, on_rezervasyon_callback=None, **kwargs):
        super().__init__(master, corner_radius=12, **kwargs)
        self.baslangic_veri = baslangic_veri
        self.rezervasyonlar = rezervasyonlar
        self.get_saat_fn = get_saat_fn
        self.on_rezervasyon_callback = on_rezervasyon_callback

        self._bilesenleri_olustur()

    def _bilesenleri_olustur(self):
        # Başlık
        self.lbl_baslik = ctk.CTkLabel(
            self, text="Rezervasyon Talebi", font=ctk.CTkFont(size=18, weight="bold")
        )
        self.lbl_baslik.pack(padx=16, pady=(16, 12), anchor="w")

        # Form Alanları Çerçevesi
        form_frame = ctk.CTkFrame(self, fg_color="transparent")
        form_frame.pack(padx=16, pady=4, fill="x")

        # 1. Kullanıcı Seçimi
        ctk.CTkLabel(form_frame, text="Kullanıcı:", font=ctk.CTkFont(size=13, weight="bold")).grid(row=0, column=0, sticky="w", pady=6)
        self.kullanici_listesi = [f"{k['id']} - {k['ad']} ({k['rol']})" for k in self.baslangic_veri.get("kullanicilar", [])]
        self.cmb_kullanici = ctk.CTkOptionMenu(form_frame, values=self.kullanici_listesi or ["-"])
        self.cmb_kullanici.grid(row=0, column=1, sticky="ew", padx=(10, 0), pady=6)

        # 2. Kaynak Seçimi
        ctk.CTkLabel(form_frame, text="Kaynak:", font=ctk.CTkFont(size=13, weight="bold")).grid(row=1, column=0, sticky="w", pady=6)
        self.kaynak_listesi = [f"{k['id']} - {k['ad']} ({k['tur']})" for k in self.baslangic_veri.get("kaynaklar", [])]
        self.cmb_kaynak = ctk.CTkOptionMenu(form_frame, values=self.kaynak_listesi or ["-"])
        self.cmb_kaynak.grid(row=1, column=1, sticky="ew", padx=(10, 0), pady=6)

        # 3. Tarih
        ctk.CTkLabel(form_frame, text="Tarih (YYYY-AA-GG):", font=ctk.CTkFont(size=13, weight="bold")).grid(row=2, column=0, sticky="w", pady=6)
        suanki_saat = self.get_saat_fn()
        varsayilan_tarih = suanki_saat.strftime("%Y-%m-%d") if isinstance(suanki_saat, datetime) else str(suanki_saat)[:10]
        self.ent_tarih = ctk.CTkEntry(form_frame, placeholder_text="2027-03-08")
        self.ent_tarih.insert(0, varsayilan_tarih)
        self.ent_tarih.grid(row=2, column=1, sticky="ew", padx=(10, 0), pady=6)

        # 4. Başlangıç Saati
        ctk.CTkLabel(form_frame, text="Başlangıç (SS:DD):", font=ctk.CTkFont(size=13, weight="bold")).grid(row=3, column=0, sticky="w", pady=6)
        self.ent_baslangic = ctk.CTkEntry(form_frame, placeholder_text="11:00")
        self.ent_baslangic.insert(0, "11:00")
        self.ent_baslangic.grid(row=3, column=1, sticky="ew", padx=(10, 0), pady=6)

        # 5. Bitiş Saati
        ctk.CTkLabel(form_frame, text="Bitiş (SS:DD):", font=ctk.CTkFont(size=13, weight="bold")).grid(row=4, column=0, sticky="w", pady=6)
        self.ent_bitis = ctk.CTkEntry(form_frame, placeholder_text="13:00")
        self.ent_bitis.insert(0, "13:00")
        self.ent_bitis.grid(row=4, column=1, sticky="ew", padx=(10, 0), pady=6)

        form_frame.columnconfigure(1, weight=1)

        # Butonlar Çerçevesi
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(padx=16, pady=12, fill="x")

        self.btn_fiyat = ctk.CTkButton(
            btn_frame, text="Fiyat Önizle", fg_color="#3B8ED0", hover_color="#1f6aa5",
            command=self.fiyat_onizle
        )
        self.btn_fiyat.pack(side="left", expand=True, fill="x", padx=(0, 6))

        self.btn_rezerve = ctk.CTkButton(
            btn_frame, text="Rezerve Et", fg_color="#2ECC71", hover_color="#27ae60",
            command=self.rezerve_et
        )
        self.btn_rezerve.pack(side="right", expand=True, fill="x", padx=(6, 0))

        # Geri Bildirim / Sonuç Kutusu
        self.lbl_sonuc = ctk.CTkLabel(
            self, text="Talep bilgilerini girip Fiyat Önizle butonuna basabilirsiniz.",
            font=ctk.CTkFont(size=12), text_color="#A0A0A0", wraplength=320, justify="left"
        )
        self.lbl_sonuc.pack(padx=16, pady=(4, 16), fill="x", anchor="w")

    def _secili_verileri_al(self):
        kullanici_str = self.cmb_kullanici.get()
        kaynak_str = self.cmb_kaynak.get()
        if not kullanici_str or kullanici_str == "-" or not kaynak_str or kaynak_str == "-":
            return None, "Lütfen geçerli bir kullanıcı ve kaynak seçin."

        kullanici_id = kullanici_str.split(" - ")[0].strip()
        kaynak_id = kaynak_str.split(" - ")[0].strip()
        tarih = self.ent_tarih.get().strip()
        bas_saat = self.ent_baslangic.get().strip()
        bit_saat = self.ent_bitis.get().strip()

        if not tarih or not bas_saat or not bit_saat:
            return None, "Lütfen tüm tarih ve saat alanlarını doldurun."

        baslangic_iso = f"{tarih}T{bas_saat}"
        bitis_iso = f"{tarih}T{bit_saat}"

        komut = {
            "komut": "fiyat",
            "kullanici": kullanici_id,
            "kaynak": kaynak_id,
            "baslangic": baslangic_iso,
            "bitis": bitis_iso
        }
        return komut, None

    def fiyat_onizle(self):
        komut, hata = self._secili_verileri_al()
        if hata:
            self._mesaj_goster(hata, basarili=False)
            return

        saat = self.get_saat_fn()
        # 1-12 Doğrulama kontrolleri (fiyat komutu gibi)
        sonuc = rezervasyon_dogrula(self.baslangic_veri, komut, self.rezervasyonlar, saat)
        if sonuc != "BASARILI":
            aciklama = HATA_ACIKLAMALARI.get(sonuc, "Bilinmeyen kural ihlali.")
            self._mesaj_goster(f"RED: {sonuc}\n{aciklama}", basarili=False)
            return

        # Ücret hesapla
        ucret = ucret_hesapla(self.baslangic_veri, komut, self.rezervasyonlar, saat)
        kullanici = next((k for k in self.baslangic_veri["kullanicilar"] if k["id"] == komut["kullanici"]), None)
        bakiye = kullanici["bakiye"] if kullanici else 0

        if bakiye < ucret:
            self._mesaj_goster(f"Tahmini Ücret: {ucret} KP\nUYARI: Bakiye Yetersiz! (Mevcut bakiye: {bakiye} KP)", basarili=False)
        else:
            self._mesaj_goster(f"Talep Geçerli!\nTahmini Ücret: {ucret} KP (Mevcut bakiye: {bakiye} KP, Kalan: {bakiye - ucret} KP)", basarili=True)

    def rezerve_et(self):
        komut, hata = self._secili_verileri_al()
        if hata:
            self._mesaj_goster(hata, basarili=False)
            return

        komut["komut"] = "rezervasyon"
        saat = self.get_saat_fn()

        # Doğrulama (13. kontrol bakiye dahil)
        sonuc = rezervasyon_dogrula(self.baslangic_veri, komut, self.rezervasyonlar, saat)
        if sonuc != "BASARILI":
            aciklama = HATA_ACIKLAMALARI.get(sonuc, "Bilinmeyen kural ihlali.")
            self._mesaj_goster(f"RED: {sonuc}\n{aciklama}", basarili=False)
            return

        ucret = ucret_hesapla(self.baslangic_veri, komut, self.rezervasyonlar, saat)
        kullanici = next((k for k in self.baslangic_veri["kullanicilar"] if k["id"] == komut["kullanici"]), None)
        
        # Bakiye düş
        kullanici["bakiye"] -= ucret

        # Yeni rezervasyon ID ata
        yeni_no = len(self.rezervasyonlar) + 1
        yeni_r = {
            "id": f"r{yeni_no}",
            "kullanici": komut["kullanici"],
            "kaynak": komut["kaynak"],
            "baslangic": komut["baslangic"],
            "bitis": komut["bitis"],
            "durum": "ONAYLI",
            "ucret": ucret
        }
        self.rezervasyonlar.append(yeni_r)

        self._mesaj_goster(
            f"BAŞARILI!\nRezervasyon No: {yeni_r['id']}\nÜcret: {ucret} KP\nYeni Bakiye: {kullanici['bakiye']} KP",
            basarili=True
        )

        if self.on_rezervasyon_callback:
            self.on_rezervasyon_callback(yeni_r)

    def _mesaj_goster(self, mesaj: str, basarili: bool):
        renk = "#2ECC71" if basarili else "#E74C3C"
        self.lbl_sonuc.configure(text=mesaj, text_color=renk)

    def listeleri_guncelle(self):
        """Kullanıcı veya kaynak eklendiğinde açılır kutuları yeniler"""
        self.kullanici_listesi = [f"{k['id']} - {k['ad']} ({k['rol']})" for k in self.baslangic_veri.get("kullanicilar", [])]
        self.kaynak_listesi = [f"{k['id']} - {k['ad']} ({k['tur']})" for k in self.baslangic_veri.get("kaynaklar", [])]
        self.cmb_kullanici.configure(values=self.kullanici_listesi or ["-"])
        self.cmb_kaynak.configure(values=self.kaynak_listesi or ["-"])
