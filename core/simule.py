from datetime import timedelta,datetime

from core.bekleme import bekleme_tara
import core.sabitler as sbt

def saat_ilerlet(baslangic_veri:dict,rezervasyonlar:list,saat:datetime,yeni_saat:datetime,bekleme_listesi):
    if yeni_saat<saat:
        return {"durum":"RED","kod":"SAAT_GERI"}

    if saat.isocalendar()[:2] != (yeni_saat - timedelta(microseconds=1)).isocalendar()[:2]:
        for k in baslangic_veri["kullanicilar"] :k["bakiye"]=baslangic_veri["roller"][k["rol"]]["haftalik_kota"]


    olaylar=[]

    for r in rezervasyonlar:
        if saat<datetime.fromisoformat(r["bitis"])<=yeni_saat and r["durum"]=="KULLANIMDA":
                r["durum"]="TAMAMLANDI"
                kullanici=next((t for t in baslangic_veri["kullanicilar"] if t["id"]==r["kullanici"]),None)
                if kullanici:
                    kullanici["guvenilirlik"]+=min(2,100-kullanici["guvenilirlik"])
                olaylar.append({
                    "zaman": r["bitis"],
                    "tur": "TAMAMLANDI",
                    "rezervasyon": r["id"],
                    "kullanici": r["kullanici"],
                    "guvenilirlik": kullanici["guvenilirlik"]
                })


        gelmeme_zamani = (datetime.fromisoformat(r["baslangic"]) + timedelta(minutes=sbt.GEC_GIRIS))
        
        if saat < gelmeme_zamani <= yeni_saat and r["durum"]=="ONAYLI":
                kullanici=next((t for t in baslangic_veri["kullanicilar"] if t["id"]==r["kullanici"]),None)
                
                if kullanici:
                    kullanici["guvenilirlik"]-=min(15,kullanici["guvenilirlik"])
                

                r["durum"]="GELMEDI"
                
                olaylar.append({
                    "zaman":gelmeme_zamani.isoformat()[:16],
                    "tur":"GELMEDI",
                    "rezervasyon":r["id"],
                    "kullanici":r["kullanici"],
                    "guvenilirlik":kullanici["guvenilirlik"]
                })


                atama_olay= bekleme_tara(baslangic_veri,r["kaynak"],rezervasyonlar,gelmeme_zamani,bekleme_listesi)
                olaylar.extend(atama_olay)


    return {"durum": "TAMAM", "olaylar": sorted(olaylar, key=lambda x: (x["zaman"],{"HAFTALIK_SIFIRLAMA":0,"TAMAMLANDI":1,"GELMEDI":2}.get(x["tur"],99),int(x["rezervasyon"][1:]) if "rezervasyon" in x else 0))}
