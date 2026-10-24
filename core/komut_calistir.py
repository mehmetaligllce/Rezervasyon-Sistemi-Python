from datetime import datetime

from core.sistem import Sistem
from core.ekle import kaynak_ekle , kullanici_ekle
from core.ucret_hesapla import ucret_hesapla
from core.dogrulama import rezervasyon_dogrula
from core.durum import rezervasyon_durum
from core.simule import saat_ilerlet
from core.sorgu import sorgu_isle
from core.paket import paket_isle
from core.bekleme import bekleme_kaydet

def komut_calistir(Sistem:Sistem,k:dict):
    if k.get("komut")=="rezervasyon" :
        sonuc=rezervasyon_dogrula(Sistem,k)
        if sonuc!="BASARILI":
            return {"durum":"RED","kod":sonuc}
        else:
            ucret = ucret_hesapla(Sistem,k)
            kullanici=next(t for t in Sistem.baslangic_veri["kullanicilar"] if t["id"]==k["kullanici"])
            kullanici["bakiye"]-=ucret
            Sistem.rezervasyonlar.append({"id":f"r{len(Sistem.rezervasyonlar)+1}","kullanici":k["kullanici"], "kaynak":k["kaynak"], "baslangic":k["baslangic"], "bitis":k["bitis"], "ucret":ucret, "durum": "ONAYLI"})
            return ({"durum":"TAMAM","rezervasyon_id":f"r{len(Sistem.rezervasyonlar)}","ucret":ucret,"bakiye":kullanici["bakiye"]})


    elif  k.get("komut")=="fiyat" :
        sonuc=rezervasyon_dogrula(Sistem,k)
        if sonuc!="BASARILI":
            return{"durum":"RED","kod":sonuc}

        else:
            ucret = ucret_hesapla(Sistem,k)
            return ({"durum":"TAMAM","ucret":ucret})

            
    elif k.get("komut") in ["giris","cikis","iptal"]:
        sonuc=rezervasyon_durum(Sistem,k)
        return sonuc
                
    elif k.get("komut")=="saat":
        yeni_saat=datetime.fromisoformat(k["zaman"])
        sonuc=saat_ilerlet(Sistem,yeni_saat)
        if sonuc["durum"]=="TAMAM":
            Sistem.saat=yeni_saat
        return sonuc
                    
    elif k.get("komut")=="sorgu":
        sonuc=sorgu_isle(Sistem,k)
        return sonuc

    elif k.get("komut")=="paket": 
        sonuc=paket_isle(Sistem,k)
        if sonuc["durum"]=="TAMAM":
            Sistem.paket_sayac+=1
        return sonuc

    elif k.get("komut")=="bekleme":
        sonuc=rezervasyon_dogrula(Sistem,k)
        if sonuc=="BASARILI":
            return ({"durum":"RED","kod":"BEKLEME_GEREKSIZ"})

        elif sonuc in ["KESISME","HAZIRLIK_IHLALI"]:
            Sistem.bekleme_sayac+=1
            sonuc=bekleme_kaydet(Sistem,k)
            return sonuc

        else:
            return ({"durum":"RED","kod":sonuc})


    elif k.get("komut")=="kullanici_ekle":
        sonuc=kullanici_ekle(Sistem,k)
        return sonuc


    elif k.get("komut")=="kaynak_ekle":
        sonuc=kaynak_ekle(Sistem,k)
        return sonuc

                    
    else:
        return {"durum": "RED", "kod": "JSON_HATALI"}