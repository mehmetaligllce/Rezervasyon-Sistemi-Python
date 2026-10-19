import math
from fractions import Fraction
from datetime import datetime,timedelta

from core.sistem import Sistem
import core.sabitler as sbt

def ucret_hesapla(Sistem:Sistem,komut:dict)->int:

    bas = datetime.fromisoformat(komut["baslangic"]) 
    bit = datetime.fromisoformat(komut["bitis"]) 
    toplam_dakika = int((bit - bas).total_seconds() // 60)

    dilimler = [
        (bas + timedelta(minutes=i), bas + timedelta(minutes=i + sbt.ADIM_DK))
        for i in range(0, toplam_dakika, sbt.ADIM_DK)
    ]

    
    tur = next(k["tur"] for k in Sistem.baslangic_veri["kaynaklar"] if k["id"] == komut["kaynak"])   
    temel_ucret = Sistem.baslangic_veri["kaynak_turleri"][tur]["temel_ucret"] 
    enerji_yogun_mu = Sistem.baslangic_veri["kaynak_turleri"][tur]["enerji_yogun"]
    toplam_kaynak = len([r for r in Sistem.baslangic_veri["kaynaklar"] if r["tur"] == tur])
    net_ucret = Fraction(0) 

    for dilim_bas, dilim_son in dilimler:
        if enerji_yogun_mu and (sbt.PIK_SAAT_BASLANGIC <= dilim_bas.hour < sbt.PIK_SAAT_BITIS):
            enerji_carpan = Fraction(3,2) 
        else: 
            enerji_carpan = Fraction(1)  

        bant_baslangic = dilim_bas.replace(hour=(dilim_bas.hour // 2) * 2, minute=0, second=0)
        bant_bitis = bant_baslangic + timedelta(hours=2)
        toplam_sure = 0


        for r in Sistem.rezervasyonlar:
            if r["durum"] in ["ONAYLI", "KULLANIMDA"]:
                r_tur = next(k["tur"] for k in Sistem.baslangic_veri["kaynaklar"] if k["id"] == r["kaynak"])
                if r_tur == tur:
                    r_bas = datetime.fromisoformat(r["baslangic"])
                    r_bit = datetime.fromisoformat(r["bitis"])

                    if r_bas.date() == dilim_bas.date():
                        kesisim_bas = max(r_bas, bant_baslangic)
                        kesisim_bit = min(r_bit, bant_bitis)

                        if kesisim_bas < kesisim_bit:
                            toplam_sure += int((kesisim_bit - kesisim_bas).total_seconds() // 60)

        if toplam_kaynak == 0:
            bant_carpan = 1

        else:
            doluluk = Fraction(toplam_sure,toplam_kaynak *120)

            if doluluk<Fraction(1,4):
                bant_carpan=1
            elif doluluk<Fraction(1,2):
                bant_carpan=Fraction(5,4)
            elif doluluk<Fraction(3,4):
                bant_carpan=Fraction(3,2)
            elif doluluk<1:
                bant_carpan=Fraction(7,4)
            else:
                bant_carpan =  2
 

        dilim_ucreti = temel_ucret * Fraction(1,4) * bant_carpan * enerji_carpan
        net_ucret += dilim_ucreti

    return math.floor(net_ucret + Fraction(1,2))