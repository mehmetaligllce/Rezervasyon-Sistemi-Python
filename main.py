import sys
from core.sistem import Sistem
from calistir.calistir import calistir
from json_io.dosya_okuma import baslangic_veri_okuma, komutlar_okuma

baslangic_veri= baslangic_veri_okuma(sys.argv[1])
komutlar= komutlar_okuma(sys.argv[2])
sistem=Sistem(baslangic_veri,komutlar)

calistir(sistem)

