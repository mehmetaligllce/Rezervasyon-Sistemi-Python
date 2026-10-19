from core.sistem import Sistem 

def kullanici_ekle(Sistem:Sistem,komut:dict):
    if any(k["id"] == komut["id"] for k in Sistem.baslangic_veri["kullanicilar"]):
        return {"durum":"RED","kod":"ID_MEVCUT"}

    if komut["rol"] not in Sistem.baslangic_veri["roller"]:
        return {"durum":"RED","kod":"TANIMSIZ_DEGER"}

    if not (0<=komut["guvenilirlik"]<=100 and isinstance(komut["guvenilirlik"],int)):
        return {"durum":"RED","kod":"GECERSIZ_DEGER"}

    
    kota=Sistem.baslangic_veri["roller"][komut["rol"]]["haftalik_kota"]
    if not (0<=komut["bakiye"]<=kota and isinstance(komut["bakiye"],int)):
        return {"durum":"RED","kod":"GECERSIZ_DEGER"}

    
    Sistem.baslangic_veri["kullanicilar"].append({ 
        "id": komut["id"], 
        "ad": komut["ad"],    
        "rol": komut["rol"], 
        "sertifikalar": komut["sertifikalar"],   
        "bakiye": komut["bakiye"], 
        "guvenilirlik": komut["guvenilirlik"] 
    })
    return{"durum":"TAMAM"}


def kaynak_ekle(Sistem:Sistem,komut:dict):
    if any(k["id"] == komut["id"] for k in Sistem.baslangic_veri["kaynaklar"]):
        return {"durum":"RED","kod":"ID_MEVCUT"}

    if komut["tur"] not in Sistem.baslangic_veri["kaynak_turleri"]:
        return {"durum":"RED","kod":"TANIMSIZ_DEGER"}

    if any(r not in Sistem.baslangic_veri["roller"] for r in komut.get("izinli_roller", [])):
        return {"durum": "RED", "kod": "TANIMSIZ_DEGER"}

    Sistem.baslangic_veri["kaynaklar"].append({ 
        "id": komut["id"],
        "ad": komut["ad"],
        "tur": komut["tur"],
        "izinli_roller": komut["izinli_roller"] }
    )
    return{"durum":"TAMAM"}