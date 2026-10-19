from datetime import datetime
class Sistem :
    def __init__(self,baslangic_veri:dict,komutlar:list):
        self.baslangic_veri=baslangic_veri
        self.komutlar=komutlar
        self.saat=datetime.fromisoformat(baslangic_veri["saat"])
        self.rezervasyonlar=[]
        self.paket_sayac=0
        self.bekleme_sayac=0
        self.bekleme_listesi=[]