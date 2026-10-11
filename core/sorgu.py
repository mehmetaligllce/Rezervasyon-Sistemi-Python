
from datetime import datetime
def sorgu_isle(baslangic_json:dict,komut:dict,rezervasyonlar:list,saat:datetime):
    if komut["tur"] in ["kullanici"]:
        kullanici=next((k for k in baslangic_json["kullanicilar"] if k["id"]==komut["id"]),None)
        
        if kullanici:
            kullanici_rezervasyonlar=[ {
                "id":r["id"],
                "kaynak":r["kaynak"],
                "baslangic":r["baslangic"],
                "bitis":r["bitis"],
                "durum":r["durum"],
                "ucret":r["ucret"]
            } for r in rezervasyonlar if r["kullanici"]==kullanici["id"] ]
            kullanici_rezervasyonlar.sort(key=lambda x: (x["baslangic"], int(x["id"][1:])))
            return {"durum":"TAMAM","bakiye":kullanici["bakiye"],"guvenilirlik":kullanici["guvenilirlik"],"rezervasyonlar":kullanici_rezervasyonlar}

        return {"durum":"RED","kod":"BULUNAMADI"}
        


    if komut["tur"] in ["kaynak"]:
        kaynak=next((k for k in baslangic_json["kaynaklar"] if k["id"]==komut["id"]),None)
        
        if not  kaynak:
            return{"durum":"RED","kod":"BULUNAMADI"}
        doluluk=[]
        hedef_gun=komut.get("gun")
        for r in rezervasyonlar:
            if r["kaynak"]==kaynak["id"] and r["durum"] in ["ONAYLI","KULLANIMDA"] :
                if r["baslangic"].startswith(hedef_gun):
                    doluluk.append({
                        "baslangic": r["baslangic"],
                        "bitis": r["bitis"],
                        "tur": "REZERVASYON",
                        "rezervasyon": r["id"]
                    })
        for b in baslangic_json.get("bakim_pencereleri", []):
            if b["kaynak"] == kaynak["id"] and b["baslangic"].startswith(hedef_gun):
                doluluk.append({
                    "baslangic": b["baslangic"],
                    "bitis": b["bitis"],
                    "tur": "BAKIM"
                })

        doluluk.sort(key=lambda x: x["baslangic"])
        return {"durum": "TAMAM", "doluluk": doluluk}
    
        
        