from datetime import datetime

from core.dogrulama import rezervasyon_dogrula
from core.ucret_hesapla import ucret_hesapla

def paket_isle(baslangic_json:dict,komut:dict,rezervasyonlar:list,saat:datetime,paket_sayac:int):
    
    kullanici=next((k for k in baslangic_json["kullanicilar"] if k["id"]==komut["kullanici"]),None)
    if kullanici is None:
        return {"durum":"RED","kod":"BULUNAMADI","kalemler":[]}

    kalemler=komut["kalemler"]
    if not  2<= len(kalemler)<=4:
        return {"durum":"RED","kod":"PAKET_BOYUTU","kalemler":[]} 
    if kullanici["guvenilirlik"]<50:
        return {"durum":"RED","kod":"GUVENILIRLIK_DUSUK","kalemler":[]}
    
    
    sonuclar=[]
    hataVarmi=False

    for idx,p in enumerate(kalemler,0) : 
        kalem_talep={
            "komut":"kalem",
            "kullanici":komut["kullanici"],
            "kaynak":p["kaynak"],
            "baslangic":p["baslangic"],
            "bitis":p["bitis"]
        }

        sonuc=rezervasyon_dogrula(baslangic_json,kalem_talep,rezervasyonlar,saat)
        if sonuc!="BASARILI":
            hataVarmi=True
            sonuclar.append({"sira":idx,"durum":"RED" ,"kod":sonuc})
        else:
            sonuclar.append({"sira":idx,"durum":"TAMAM"})

    if hataVarmi:
        return {"durum":"RED","kod":"PAKET_RED","kalemler":sonuclar}

    
    t_rez=rezervasyonlar+[{**kalemler[0],"durum":"ONAYLI","kullanici":kullanici["id"]}]

    for k in kalemler[1:]:
        kalem_talep={
            "komut":"kalem",
            "kullanici":komut["kullanici"],
            "kaynak":k["kaynak"],
            "baslangic":k["baslangic"],
            "bitis":k["bitis"]
        }

        sonuc=rezervasyon_dogrula(baslangic_json,kalem_talep,t_rez,saat)
        if sonuc!="BASARILI":
            return {"durum":"RED","kod":"PAKET_ICI_KESISME","kalemler":sonuclar}
        if k!=kalemler[-1]:
            t_rez=t_rez+[{**k,"durum":"ONAYLI","kullanici":kullanici["id"]}]



    ucretler=[]

    for p in kalemler:
        kalem_talep={
            "komut":"kalem",
            "kullanici":komut["kullanici"],
            "kaynak":p["kaynak"],
            "baslangic":p["baslangic"],
            "bitis":p["bitis"]
        }
        ucretler.append(ucret_hesapla(baslangic_json,kalem_talep,rezervasyonlar,saat))
    toplam_ucret=sum(ucretler)

    if toplam_ucret > kullanici["bakiye"]:
        return{"durum":"RED","kod":"BAKIYE_YETERSIZ","kalemler":sonuclar}
    
    kullanici["bakiye"]-=toplam_ucret

    paket_id=f"p{paket_sayac+1}"
    yeni_rez_idler=[]

    for i,p in enumerate(kalemler):
        rez_id=f"r{len(rezervasyonlar)+1}"

        yeni_rez_idler.append(rez_id)
        rezervasyonlar.append({
            "id":rez_id,
            "kullanici":kullanici["id"],
            "kaynak":p["kaynak"],
            "baslangic":p["baslangic"],
            "bitis":p["bitis"],
            "ucret":ucretler[i],
            "durum":"ONAYLI",
            "paket_id":paket_id
        })


    return {
        "durum": "TAMAM",
        "paket_id": paket_id,
        "rezervasyonlar": yeni_rez_idler,
        "ucretler": ucretler,
        "toplam": toplam_ucret,
        "bakiye": kullanici["bakiye"]
    }