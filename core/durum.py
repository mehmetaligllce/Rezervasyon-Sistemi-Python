import math
from datetime import timedelta
from datetime import datetime
import core.sabitler as sbt

def rezervasyon_durum(baslangic_json:dict,komut:dict,rezervasyonlar:list,saat:datetime)->str:
    rezervasyon= next((r for r in rezervasyonlar if komut.get("rezervasyon")==r["id"]),None)

    if rezervasyon is None :
        return {"durum":"RED","kod":"BULUNAMADI"}

    if komut.get("komut") in ["giris"]:
        if rezervasyon["durum"]!="ONAYLI":
            return {"durum": "RED", "kod": "DURUM_HATASI"}
        baslangic=datetime.fromisoformat(rezervasyon["baslangic"])
        if baslangic - timedelta(minutes=sbt.ERKEN_GIRIS) <= saat and saat<=baslangic + timedelta(minutes=sbt.GEC_GIRIS):
            rezervasyon["durum"]="KULLANIMDA"
            return {"durum":"TAMAM"}
        else:
            return {"durum":"RED","kod":"GIRIS_PENCERESI_DISI"}


    elif komut.get("komut") in ["cikis"]:
        if rezervasyon["durum"]!="KULLANIMDA":
            return {"durum": "RED", "kod": "DURUM_HATASI"}
        bitis=datetime.fromisoformat(rezervasyon["bitis"])
        if saat<bitis:
            rezervasyon["bitis"]=saat.isoformat()[:16]
        rezervasyon["durum"]="TAMAMLANDI"
        return {"durum":"TAMAM","olaylar":[]}


    elif komut.get("komut") in ["iptal"]:
        if rezervasyon["durum"]!="ONAYLI":
            return {"durum": "RED", "kod": "DURUM_HATASI"}
        baslangic=datetime.fromisoformat(rezervasyon["baslangic"])
        kalan_zaman=(baslangic-saat).total_seconds() / 3600
        kullanici=next((t for t in baslangic_json["kullanicilar"] if rezervasyon["kullanici"]==t["id"]),None)
        
        if kalan_zaman >= 24:
            iade=rezervasyon["ucret"]
            
        elif kalan_zaman >=2:
            iade=math.floor(rezervasyon["ucret"]/2)
        else :
            iade=0
            kullanici["guvenilirlik"]=max(kullanici["guvenilirlik"]+sbt.GUVENILIRLIK_PUANLAMA["GEC_IPTAL"],0)
        
        kota=baslangic_json["roller"][kullanici["rol"]]["haftalik_kota"]
        iade = min(iade,kota-kullanici["bakiye"])
        kullanici["bakiye"]+=iade
        rezervasyon["durum"]="IPTAL"
        return {"durum": "TAMAM", "iade": iade, "bakiye": kullanici["bakiye"], "guvenilirlik": kullanici["guvenilirlik"], "olaylar": []}
 