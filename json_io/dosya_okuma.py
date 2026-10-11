from core.ekle import kaynak_ekle
from core.ekle import kullanici_ekle
from core.yard_fonksiyonlar import ucret_hesapla
from datetime import datetime
import json 
import sys
from core.dogrulama import rezervasyon_dogrula
from core.durum import rezervasyon_durum
from core.simule import saat_ilerlet
from core.sorgu import sorgu_isle
from core.paket import paket_isle
from core.bekleme import bekleme_kaydet
def baslangic_json_okuma(yol:str)->dict:
    try:
        with open(yol,"r",encoding="utf8") as b:
            return json.load(b)


    except Exception as e:
        sys.stderr.write(f"Başlangıç dosyası okunamadı : {e} \n")
        sys.exit(1)

def komutlar_json_okuma(yol:str)-> list:
    try:
        komutlar=[]
        with open(yol,"r",encoding="utf-8") as k:
            for t in k:
                t=t.strip()
                if not t:
                    continue
                try:
                    veri=json.loads(t)
                    komutlar.append(veri)
                except json.JSONDecodeError:
                    komutlar.append({"JSON_HATALI":True})
        return komutlar
    except Exception as e:
        sys.stderr.write(f"Komutlar dosyası okunamadı : {e} \n")
        sys.exit(1)


def sonuc_yaz(sonuc:dict):
    print(json.dumps(sonuc,ensure_ascii=False))


def komut_yaz(komutlar:list,baslangic_json:dict,saat:datetime=None,rezervasyonlar:list=None):
    if saat is None:
        saat=datetime.fromisoformat(baslangic_json["saat"])
    if rezervasyonlar is None:
        rezervasyonlar=[]
    paket_sayac=0
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
                    sonuc=bekleme_kaydet(baslangic_json,k,rezervasyonlar,saat,bekleme_listesi)
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
            


    
        