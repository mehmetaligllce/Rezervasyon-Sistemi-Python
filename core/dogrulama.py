from datetime import datetime,timedelta
import core.sabitler as sbt
from core.yard_fonksiyonlar import ucret_hesapla
def rezervasyon_dogrula(baslangic_veri:dict ,komut:dict,rezervasyonlar:list[dict],saat:datetime)->str:

    kullanici = next((k for k in baslangic_veri["kullanicilar"] if k["id"]==komut["kullanici"]),None) 
    kullanici_yok= kullanici is None
    kaynak = next((k for k in baslangic_veri["kaynaklar"] if k["id"]==komut["kaynak"]),None) 
    
    kaynak_yok=kaynak is None
    if kullanici_yok or kaynak_yok:
        return "BULUNAMADI"

    baslangic=datetime.fromisoformat(komut["baslangic"])
    bitis=datetime.fromisoformat(komut["bitis"])
    dilim_yanlis = baslangic.minute % sbt.ADIM_DK != 0 or bitis.minute % sbt.ADIM_DK != 0
    if dilim_yanlis or bitis<=baslangic:
        return "ZAMAN_ADIMI_HATASI"
    if baslangic<saat:
        return "GECMIS_ZAMAN"
    if baslangic.day != bitis.day or baslangic.hour<sbt.REZERVASYON_BASLANGIC  or bitis.hour>sbt.REZERVASYON_BITIS or( bitis.hour==sbt.REZERVASYON_BITIS and bitis.minute>0) :
        return "CALISMA_SAATI_DISI"
    kullanici_rol=kullanici["rol"]
    max_sure=baslangic_veri["roller"][kullanici_rol]["azami_sure_dk"]
    if (bitis-baslangic).total_seconds()/60<sbt.REZERVASYON_MIN_DK or (bitis-baslangic).total_seconds()/60>max_sure:
        return "SURE_SINIRI"
    if kullanici["guvenilirlik"]<sbt.GUVENILIRLIK_ESIK:
        tarih_sinir=1
    else:
        tarih_sinir=baslangic_veri["roller"][kullanici_rol]["ileri_gun"]
        
    if baslangic>saat + timedelta(days=tarih_sinir):
        return "ILERI_TARIH_SINIRI"



    erisim_izni_yok = kullanici_rol not in kaynak["izinli_roller"]
    if erisim_izni_yok:
        return "ROL_IZNI_YOK"

    gerekli_sertifika = baslangic_veri["kaynak_turleri"][kaynak["tur"]]["sertifika"]
    sertifika_yok= gerekli_sertifika is not None and gerekli_sertifika not in kullanici["sertifikalar"]
    if sertifika_yok:
        return "SERTIFIKA_YOK"

    bakim_pencereleri=baslangic_veri["bakim_pencereleri"]
    for b in bakim_pencereleri:
        if b["kaynak"]==kaynak["id"]:
            bakim_baslangic=datetime.fromisoformat(b["baslangic"])
            bakim_bitis=datetime.fromisoformat(b["bitis"])
            bakim_mi =(bakim_baslangic<bitis and baslangic<bakim_bitis) 
            if bakim_mi:
                return "BAKIM"

 
    for r in [t for t in rezervasyonlar if t["durum"] in ["ONAYLI", "KULLANIMDA"]]:
        son_rezervasyon_bitis=datetime.fromisoformat(r["bitis"])
        son_rezervasyon_baslangic=datetime.fromisoformat(r["baslangic"])
        
        kesisme_var_mi = (baslangic < son_rezervasyon_bitis) and (bitis > son_rezervasyon_baslangic) and r["kaynak"]==kaynak["id"]
        if kesisme_var_mi:
            return "KESISME"

    hazirlik_suresi = timedelta(minutes=baslangic_veri["kaynak_turleri"][kaynak["tur"]]["hazirlik_dk"])

    for r in [t for t in rezervasyonlar if t["durum"] in  ["ONAYLI", "KULLANIMDA", "TAMAMLANDI"]]:
        if r["kaynak"] == kaynak["id"]:
            r_bas = datetime.fromisoformat(r["baslangic"])
            r_bit = datetime.fromisoformat(r["bitis"])
     
            if baslangic < (r_bit + hazirlik_suresi) and (bitis + hazirlik_suresi) > r_bas:
                return "HAZIRLIK_IHLALI"
    
    sinir = timedelta(minutes=sbt.REZERVASYON_ARDISIK_BEKLEME)
    for r in [t for t in rezervasyonlar if t["durum"] in  ["ONAYLI", "KULLANIMDA", "TAMAMLANDI"]]:
        if r["kaynak"]==kaynak["id"] and r["kullanici"]==kullanici["id"] :
            r_bas = datetime.fromisoformat(r["baslangic"])
            r_bit = datetime.fromisoformat(r["bitis"])
            if baslangic < r_bit + sinir and bitis +  sinir > r_bas:
                return "ARDISIK_KULLANIM"
            
    bakiye= kullanici["bakiye"]
    if komut.get("komut")!="fiyat":
        ucret = ucret_hesapla(baslangic_veri,komut,rezervasyonlar,saat)  
        if  bakiye<ucret:
            return "BAKIYE_YETERSIZ"
    return "BASARILI"


