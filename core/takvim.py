from datetime import timedelta
from datetime import datetime
def takvim_verisi_uret(baslangic_json:dict,rezervasyonlar:list,secilen_gun:datetime):
    takvim= {k["id"]:[] for k in baslangic_json["kaynaklar"]}
    hazirlik_sureler={ k["id"]: baslangic_json["kaynak_turleri"][k["tur"]]["hazirlik_dk"] for k in baslangic_json["kaynaklar"]}
    gun=secilen_gun.strftime("%Y-%m-%d")if isinstance(secilen_gun,datetime) else str(secilen_gun)[:10]
    for r in rezervasyonlar:
        if r["baslangic"].startswith(gun):
            takvim[r["kaynak"]].append({"tur":"REZERVASYON",**r})
            haz_dk=hazirlik_sureler.get(r["kaynak"],0)
            if haz_dk>0 and r["durum"] in ["ONAYLI","KULLANIMDA","TAMAMLANDI"]:
                r_bit=datetime.fromisoformat(r["bitis"])
                haz_bit=r_bit+timedelta(minutes=haz_dk)
                takvim[r["kaynak"]].append({
                    "tur":"HAZIRLIK",
                    "baslangic":r["bitis"],
                    "bitis":haz_bit.strftime("%Y-%m-%dT%H:%M"),
                    "rezervasyon_id":r["id"]
                })
    for b in baslangic_json.get("bakim_pencereleri",[]): 
        if b["baslangic"].startswith(gun):
            takvim[b["kaynak"]].append({"tur":"BAKIM","baslangic":b["baslangic"],"bitis":b["bitis"]})
    
    for ogeler in takvim.values():
        ogeler.sort(key=lambda x: x["baslangic"])
        alt_satirlar = []
        for oge in ogeler:
            yerlesti = False
            for idx, son_bit in enumerate(alt_satirlar):
                if oge["baslangic"] >= son_bit:
                    oge["alt_satir"] = idx
                    alt_satirlar[idx] = oge["bitis"]
                    yerlesti = True
                    break
            if not yerlesti:
                oge["alt_satir"] = len(alt_satirlar)
                alt_satirlar.append(oge["bitis"])
    return takvim