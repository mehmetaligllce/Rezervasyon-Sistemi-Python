from datetime import datetime

from core.sistem import Sistem
from core.dogrulama import rezervasyon_dogrula
from core.ucret_hesapla import ucret_hesapla


def siralama(Sistem:Sistem,b:dict):
    kullanici=next(k for k in Sistem.baslangic_veri["kullanicilar"] if k.get("id")==b["kullanici"])
    return(-kullanici["guvenilirlik"],b["kayit_saati"],int(b["id"][1:]))

def bekleme_kaydet(Sistem:Sistem,komut:dict):
    b_id=f"b{Sistem.bekleme_sayac}"
    Sistem.bekleme_listesi=[b for b in Sistem.bekleme_listesi if datetime.fromisoformat(b["baslangic"])>=Sistem.saat]
    

    yeni={
        "id": b_id,
        "kullanici": komut["kullanici"],
        "kaynak": komut["kaynak"],
        "baslangic": komut["baslangic"],
        "bitis": komut["bitis"],
        "kayit_saati": Sistem.saat.isoformat()[:16]
    }
    Sistem.bekleme_listesi.append(yeni)

    kaynak_bekleyenler=[b for b in Sistem.bekleme_listesi if komut["kaynak"]==b["kaynak"]]
    kaynak_bekleyenler.sort(key=lambda b:siralama(Sistem,b))

    sira=kaynak_bekleyenler.index(yeni)+1

    return{"durum":"TAMAM","bekleme_id":b_id,"sira":sira}




def bekleme_tara(Sistem:Sistem,kaynak_id:str,gelmeme_zamani:datetime):
    liste=[r for r in Sistem.bekleme_listesi if r["kaynak"]==kaynak_id and datetime.fromisoformat(r["baslangic"])>=gelmeme_zamani]
    liste.sort(key=lambda b:siralama(Sistem,b))
    olaylar=[]

    for l in liste:
        sonuc=rezervasyon_dogrula(Sistem,l)
        if sonuc=="BASARILI":
            rez_id=f"r{len(Sistem.rezervasyonlar)+1}"
            ucret=ucret_hesapla(Sistem,l)
            kullanici=next(k for k in Sistem.baslangic_veri["kullanicilar"] if k.get("id")==l["kullanici"])
            kullanici["bakiye"]-=ucret
            Sistem.rezervasyonlar.append({
            "id": rez_id,
            "kullanici": l["kullanici"],
            "kaynak": l["kaynak"],
            "baslangic": l["baslangic"],
            "bitis": l["bitis"],
            "ucret": ucret,
            "durum": "ONAYLI"
            })
            Sistem.bekleme_listesi.remove(l)
            olaylar.append(
                {
                    "zaman": gelmeme_zamani.isoformat()[:16],
                    "tur": "OTOMATIK_ATAMA",
                    "bekleme": l["id"],
                    "rezervasyon": rez_id,
                    "kullanici": l["kullanici"],
                    "ucret": ucret,
                    "bakiye": kullanici["bakiye"]
                }
            )
    return olaylar
            
