from json_io.dosya_okuma import baslangic_json_okuma, komutlar_json_okuma , komut_yaz
import sys

baslangic_json= baslangic_json_okuma(sys.argv[1])
komutlar_json= komutlar_json_okuma(sys.argv[2])
komut_yaz(komutlar_json,baslangic_json)
    