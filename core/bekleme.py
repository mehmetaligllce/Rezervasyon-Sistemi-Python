from core.yard_fonksiyonlar import ucret_hesapla
from datetime import datetime
from core.dogrulama import rezervasyon_dogrula
def siralama(baslangic_json:dict,b:dict):
    kullanici=next(k for k in baslangic_json["kullanicilar"] if k.get("id")==b["kullanici"])
    return(-kullanici["guvenilirlik"],b["kayit_saati"],int(b["id"][1:]))
def bekleme_kaydet(baslangic_json:dict,komut:dict,rezervasyonlar:list,saat:datetime,bekleme_listesi:list):
    b_id=f"b{len(bekleme_listesi)+1}"
    yeni={
        "id": b_id,
        "kullanici": komut["kullanici"],
        "kaynak": komut["kaynak"],
        "baslangic": komut["baslangic"],
        "bitis": komut["bitis"],
        "kayit_saati": saat.isoformat()[:16]
    }
    bekleme_listesi.append(yeni)

    kaynak_bekleyenler=[b for b in bekleme_listesi if komut["kaynak"]==b["kaynak"]]
    kaynak_bekleyenler.sort(key=lambda b:siralama(baslangic_json,b))

    sira=kaynak_bekleyenler.index(yeni)+1

    return{"durum":"TAMAM","bekleme_id":b_id,"sira":sira}




def bekleme_tara(baslangic_json:dict,kaynak_id:str,rezervasyonlar:list,saat:datetime,bekleme_listesi:list):
    liste=[r for r in bekleme_listesi if r["kaynak"]==kaynak_id and datetime.fromisoformat(r["baslangic"])>=saat]
    liste.sort(key=lambda b:siralama(baslangic_json,b))
    olaylar=[]
    for l in liste:
        sonuc=rezervasyon_dogrula(baslangic_json,l,rezervasyonlar,saat)
        if sonuc=="BASARILI":
            rez_id=f"r{len(rezervasyonlar)+1}"
            ucret=ucret_hesapla(baslangic_json,l,rezervasyonlar,saat)
            kullanici=next(k for k in baslangic_json["kullanicilar"] if k.get("id")==l["kullanici"])
            kullanici["bakiye"]-=ucret
            rezervasyonlar.append({
            "id": rez_id,
            "kullanici": l["kullanici"],
            "kaynak": l["kaynak"],
            "baslangic": l["baslangic"],
            "bitis": l["bitis"],
            "ucret": ucret,
            "durum": "ONAYLI"
            })
            bekleme_listesi.remove(l)
            olaylar.append(
                {
                    "zaman": saat.isoformat()[:16],
                    "tur": "OTOMATIK_ATAMA",
                    "bekleme": l["id"],
                    "rezervasyon": rez_id,
                    "kullanici": l["kullanici"],
                    "ucret": ucret,
                    "bakiye": kullanici["bakiye"]
                }
            )
    return olaylar
            
