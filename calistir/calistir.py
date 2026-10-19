from datetime import datetime

from json_io.dosya_okuma import sonuc_yaz
from core.ekle import kaynak_ekle , kullanici_ekle
from core.ucret_hesapla import ucret_hesapla
from core.dogrulama import rezervasyon_dogrula
from core.durum import rezervasyon_durum
from core.simule import saat_ilerlet
from core.sorgu import sorgu_isle
from core.paket import paket_isle
from core.bekleme import bekleme_kaydet


def calistir(komutlar:list,baslangic_json:dict,saat:datetime=None,rezervasyonlar:list=None):
    if saat is None:
        saat=datetime.fromisoformat(baslangic_json["saat"])
    if rezervasyonlar is None:
        rezervasyonlar=[]


    paket_sayac=0
    bekleme_sayac=0
    bekleme_listesi=[]

    for idx,k in enumerate(komutlar,1):
        if k.get("JSON_HATALI"):
            sonuc_yaz({"no":idx,"durum":"RED","kod":"JSON_HATALI"})
        else:
            if k.get("komut")=="rezervasyon" :
                durum=rezervasyon_dogrula(baslangic_json,k,rezervasyonlar,saat)
                if durum!="BASARILI":
                    sonuc_yaz({"no":idx,"komut":k.get("komut"),"durum":"RED","kod":durum})
                else:
                    ucret = ucret_hesapla(baslangic_json, k, rezervasyonlar, saat)
                    kullanici=next(t for t in baslangic_json["kullanicilar"] if t["id"]==k["kullanici"])
                    kullanici["bakiye"]-=ucret
                    rezervasyonlar.append({"id":f"r{len(rezervasyonlar)+1}","kullanici":k["kullanici"], "kaynak":k["kaynak"], "baslangic":k["baslangic"], "bitis":k["bitis"], "ucret":ucret, "durum": "ONAYLI"})
                    sonuc_yaz({"no":idx,"komut":k.get("komut"),"durum":"TAMAM","rezervasyon_id":f"r{len(rezervasyonlar)}","ucret":ucret,"bakiye":kullanici["bakiye"]})


            elif  k.get("komut")=="fiyat" :
                durum=rezervasyon_dogrula(baslangic_json,k,rezervasyonlar,saat)
                if durum!="BASARILI":
                    sonuc_yaz({"no": idx, "komut": "fiyat", "durum": "RED", "kod": durum})
                else:
                    ucret = ucret_hesapla(baslangic_json, k, rezervasyonlar, saat)
                    sonuc_yaz({"no": idx, "komut": "fiyat", "durum": "TAMAM", "ucret": ucret})
            elif k.get("komut") in ["giris","cikis","iptal"]:
                durum=rezervasyon_durum(baslangic_json,k,rezervasyonlar,saat)
                sonuc_yaz({"no":idx,"komut":k.get("komut"),**durum})
            
            elif k.get("komut")=="saat":
                yeni_saat=datetime.fromisoformat(k["zaman"])
                sonuc=saat_ilerlet(baslangic_json,rezervasyonlar,saat,yeni_saat,bekleme_listesi)
                if sonuc["durum"]=="TAMAM":
                    saat=yeni_saat
                sonuc_yaz({"no":idx,"komut":"saat",**sonuc})
                
            elif k.get("komut")=="sorgu":
                sonuc=sorgu_isle(baslangic_json,k,rezervasyonlar,saat)
                sonuc_yaz({"no":idx,"komut":"sorgu",**sonuc})

            elif k.get("komut")=="paket": 
                sonuc=paket_isle(baslangic_json,k,rezervasyonlar,saat,paket_sayac)
                if sonuc["durum"]=="TAMAM":
                    paket_sayac+=1
                sonuc_yaz({"no":idx,"komut":"paket",**sonuc})

            elif k.get("komut")=="bekleme":
                sonuc=rezervasyon_dogrula(baslangic_json,k,rezervasyonlar,saat)
                if sonuc=="BASARILI":
                    sonuc_yaz({"no":idx,"komut":k.get("komut"),"durum":"RED","kod":"BEKLEME_GEREKSIZ"})
                elif sonuc in ["KESISME","HAZIRLIK_IHLALI"]:
                    bekleme_sayac+=1
                    sonuc=bekleme_kaydet(baslangic_json,k,saat,bekleme_listesi,bekleme_sayac)
                    sonuc_yaz({"no":idx,"komut":k.get("komut"),**sonuc})
                else:
                    sonuc_yaz({"no":idx,"komut":k.get("komut"),"durum":"RED","kod":sonuc})
            elif k.get("komut")=="kullanici_ekle":
                sonuc=kullanici_ekle(baslangic_json,k)
                sonuc_yaz({"no":idx,"komut":k.get("komut"),**sonuc})


            elif k.get("komut")=="kaynak_ekle":
                sonuc=kaynak_ekle(baslangic_json,k)
                sonuc_yaz({"no":idx,"komut":k.get("komut"),**sonuc})

                
            else:
                sonuc_yaz({"no":idx,"komut":k.get("komut"),"durum":"TAMAM"})
            