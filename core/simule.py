import core.sabitler as sbt
from datetime import timedelta
from datetime import datetime
def saat_ilerlet(baslangic_veri:dict,rezervasyonlar:list,saat:datetime,yeni_saat:datetime):
    if yeni_saat<saat:
        return {"durum":"RED","kod":"SAAT_GERI"}

    if saat.isocalendar()[:2] != (yeni_saat - timedelta(microseconds=1)).isocalendar()[:2]:
        for k in baslangic_veri["kullanicilar"] :k["bakiye"]=baslangic_veri["roller"][k["rol"]]["haftalik_kota"]

    olaylar=[]
    for r in rezervasyonlar:
        if saat<datetime.fromisoformat(r["bitis"])<=yeni_saat:
            
            if datetime.fromisoformat(r["bitis"])<=yeni_saat and r["durum"]=="KULLANIMDA":
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



        if saat < datetime.fromisoformat(r["baslangic"])+timedelta(minutes=sbt.GEC_GIRIS) <= yeni_saat and r["durum"]=="ONAYLI":
                r["durum"]="GELMEDI"
                kullanici=next((t for t in baslangic_veri["kullanicilar"] if t["id"]==r["kullanici"]),None)
                if kullanici:
                    kullanici["guvenilirlik"]-=min(15,kullanici["guvenilirlik"])
                gelmeme_zamani = (datetime.fromisoformat(r["baslangic"]) + timedelta(minutes=sbt.GEC_GIRIS)).isoformat()[:16]
                olaylar.append({
                    "zaman":gelmeme_zamani,
                    "tur":"GELMEDI",
                    "rezervasyon":r["id"],
                    "kullanici":r["kullanici"],
                    "guvenilirlik":kullanici["guvenilirlik"]
                })
    return {"durum": "TAMAM", "olaylar": sorted(olaylar, key=lambda x: (x["zaman"],{"HAFTALIK_SIFIRLAMA":0,"TAMAMLANDI":1,"GELMEDI":2}.get(x["tur"],99),int(x["rezervasyon"][1:]) if "rezervasyon" in x else 0))}
