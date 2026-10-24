from datetime import timedelta,datetime

from core.sistem import Sistem
from core.bekleme import bekleme_tara
import core.sabitler as sbt

def saat_ilerlet(Sistem:Sistem,yeni_saat:datetime):
    if yeni_saat<Sistem.saat:
        return {"durum":"RED","kod":"SAAT_GERI"}
    
    
    pazartesi= Sistem.saat.replace(hour=0,minute=0,second=0,microsecond=0) + timedelta(days=(7 - Sistem.saat.weekday()) % 7)
    if pazartesi<=Sistem.saat: 
        pazartesi+=timedelta(days=7)

    olaylar=[]

    if Sistem.saat<pazartesi<=yeni_saat:
        for k in Sistem.baslangic_veri["kullanicilar"] :k["bakiye"]=Sistem.baslangic_veri["roller"][k["rol"]]["haftalik_kota"]
        while pazartesi<=yeni_saat:
            olaylar.append({"zaman":pazartesi.isoformat()[:16],"tur":"HAFTALIK_SIFIRLAMA"})
            pazartesi+=timedelta(days=7)
        

    tamamlar=[]
    gelmeyenler = []
    bosalanlar=[]



    for r in Sistem.rezervasyonlar:
        if Sistem.saat<datetime.fromisoformat(r["bitis"])<=yeni_saat and r["durum"]=="KULLANIMDA":
                r["durum"]="TAMAMLANDI"
                kullanici=next((t for t in Sistem.baslangic_veri["kullanicilar"] if t["id"]==r["kullanici"]),None)
                if kullanici:
                    kullanici["guvenilirlik"]+=min(2,100-kullanici["guvenilirlik"])
                tamamlar.append({
                    "zaman": r["bitis"],
                    "tur": "TAMAMLANDI",
                    "rezervasyon": r["id"],
                    "kullanici": r["kullanici"],
                    "guvenilirlik": kullanici["guvenilirlik"]
                })
            
        elif r["durum"]=="ONAYLI":

            gelmeme_zamani = (datetime.fromisoformat(r["baslangic"]) + timedelta(minutes=sbt.GEC_GIRIS))

            if Sistem.saat < gelmeme_zamani <= yeni_saat :
                kullanici=next((t for t in Sistem.baslangic_veri["kullanicilar"] if t["id"]==r["kullanici"]),None)
                
                if kullanici:
                    kullanici["guvenilirlik"]-=min(15,kullanici["guvenilirlik"])
                

                r["durum"]="GELMEDI"
                gelmeyenler.append({
                    "zaman":gelmeme_zamani.isoformat()[:16],
                    "tur":"GELMEDI",
                    "rezervasyon":r["id"],
                    "kullanici":r["kullanici"],
                    "guvenilirlik":kullanici["guvenilirlik"]
                })
                
                bosalanlar.append((r["kaynak"],gelmeme_zamani))

    olaylar.extend(tamamlar)
    olaylar.extend(gelmeyenler)
    
    for id,zaman in bosalanlar:
        atama_olay= bekleme_tara(Sistem,id,zaman)
        olaylar.extend(atama_olay)




    Sistem.bekleme_listesi = [b for b in Sistem.bekleme_listesi if datetime.fromisoformat(b["baslangic"]) >= yeni_saat]
    return {"durum": "TAMAM", "olaylar": sorted(olaylar, key=lambda x: (x["zaman"],{"HAFTALIK_SIFIRLAMA":0,"TAMAMLANDI":1,"GELMEDI":2}.get(x["tur"],99),int(x["rezervasyon"][1:]) if "rezervasyon" in x else 0))}
