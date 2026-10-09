import json 
import sys


def baslangic_json_okuma(yol:str)->dict:
    try:
        with open(yol,"r",encoding="utf8") as b:
            return json.load(b)


    except Exception as e:
        sys.stderr.write(f"Başlangıç dosyası okunamadı : {e} \n")
        sys.exit(1)

def komutlar_json_okuma(yol:str)-> list:
    try:
        komutlar=[]
        with open(yol,"r",encoding="utf-8") as k:
            for t in k:
                t=t.strip()
                if not t:
                    continue
                try:
                    veri=json.loads(t)
                    komutlar.append(veri)
                except json.JSONDecodeError:
                    komutlar.append({"JSON_HATALI":True})
        return komutlar
    except Exception as e:
        sys.stderr.write(f"Komutlar dosyası okunamadı : {e} \n")
        sys.exit(1)


def sonuc_yaz(sonuc:dict):
    print(json.dumps(sonuc,ensure_ascii=False))


def komut_yaz(komutlar:list):
    for idx,k in enumerate(komutlar,1):
        if k.get("JSON_HATALI"):
            sonuc_yaz({"no":idx,"durum":"RED","kod":"JSON_HATALI"})
        else:
            sonuc_yaz({"no":idx,"komut":k.get("komut")})
        