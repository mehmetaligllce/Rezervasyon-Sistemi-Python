def kullanici_ekle(baslangic_json:dict,komut:dict):
    if any(k["id"] == komut["id"] for k in baslangic_json["kullanicilar"]):
        return {"durum":"RED","kod":"ID_MEVCUT"}
    if komut["rol"] not in baslangic_json["roller"]:
        return {"durum":"RED","kod":"TANIMSIZ_DEGER"}

    kota=baslangic_json["roller"][komut["rol"]]["haftalik_kota"]
    if not (0<=komut["bakiye"]<=kota and isinstance(komut["bakiye"],int)):
        return {"durum":"RED","kod":"GECERSIZ_DEGER"}
    if not (0<=komut["guvenilirlik"]<=100 and isinstance(komut["guvenilirlik"],int)):
        return {"durum":"RED","kod":"GECERSIZ_DEGER"}
    baslangic_json["kullanicilar"].append({ 
        "id": komut["id"], 
        "ad": komut["ad"],    
        "rol": komut["rol"], 
        "sertifikalar": komut["sertifikalar"],   
        "bakiye": komut["bakiye"], 
        "guvenilirlik": komut["guvenilirlik"] 
    })
    return{"durum":"TAMAM"}


def kaynak_ekle(baslangic_json:dict,komut:dict):
    if any(k["id"] == komut["id"] for k in baslangic_json["kaynaklar"]):
        return {"durum":"RED","kod":"ID_MEVCUT"}
    if komut["tur"] not in baslangic_json["kaynak_turleri"]:
        return {"durum":"RED","kod":"TANIMSIZ_DEGER"}
    if any(r not in baslangic_json["roller"] for r in komut.get("izinli_roller", [])):
        return {"durum": "RED", "kod": "TANIMSIZ_DEGER"}
    baslangic_json["kaynaklar"].append({ 
        "id": komut["id"],
        "ad": komut["ad"],
        "tur": komut["tur"],
        "izinli_roller": komut["izinli_roller"] }
    )
    return{"durum":"TAMAM"}


