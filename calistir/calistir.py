from core.sistem import Sistem
from json_io.dosya_okuma import sonuc_yaz
from core.komut_calistir import komut_calistir

def calistir(Sistem:Sistem):
    for idx,k in enumerate(Sistem.komutlar,1):
        try:
            if k.get("JSON_HATALI"):
                sonuc_yaz({"no":idx,"durum":"RED","kod":"JSON_HATALI"})
            else:
                sonuc=komut_calistir(Sistem,k)
                sonuc_yaz({"no":idx,"komut":k.get("komut"),**sonuc})
        except Exception as e:
            sonuc_yaz({"no": idx, "komut": k.get("komut", "bilinmeyen"), "durum": "RED", "kod": "JSON_HATALI"})
