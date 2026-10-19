import sys
from calistir.calistir import calistir
from json_io.dosya_okuma import baslangic_json_okuma, komutlar_json_okuma

baslangic_json= baslangic_json_okuma(sys.argv[1])
komutlar_json= komutlar_json_okuma(sys.argv[2])
calistir(komutlar_json,baslangic_json)

