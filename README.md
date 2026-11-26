# Takip Sistemi

Laboratuvar, cihaz, yazıcı ve oda gibi kaynakların rezervasyon, kullanım, ücretlendirme, kota ve bekleme listesi süreçlerini yöneten takip sistemi. Komut satırı (JSON/JSONL tabanlı) ve masaüstü arayüzü ile çalışır.

## Gereksinimler

- Python 3.13+
- Arayüz için:
  ```bash
  pip install -r requirements.txt
  ```

## Kullanım

### Komut Satırı (CLI)

Başlangıç verisi (`baslangic.json`) ve komut dosyasını (`komutlar.jsonl`) vererek çalıştırabilirsiniz:

```bash
python main.py ornek/baslangic.json ornek/komutlar.jsonl
```

Veya :

```bash
# Windows
calistir.bat ornek/baslangic.json ornek/komutlar.jsonl

# Linux / macOS
./calistir.sh ornek/baslangic.json ornek/komutlar.jsonl
```

Çıktılar standart çıktıya JSONL formatında yazılır.

### Grafik Arayüz (UI)

```bash
python ui/app.py
```

Windows üzerinde doğrudan `app.exe` dosyası da çalıştırılabilir.

## Desteklenen Komutlar

- `kullanici_ekle` / `kaynak_ekle`: Sisteme yeni kullanıcı veya kaynak ekler.
- `rezervasyon` / `fiyat`: Rezervasyon oluşturur veya ön fiyat hesaplar.
- `giris` / `cikis` / `iptal`: Rezervasyon durumunu günceller.
- `paket`: Birden fazla kaynağı tek seferde rezerve eder.
- `bekleme`: Çakışma durumunda bekleme listesine kayıt ekler.
- `saat`: Sistem saatini ileri alır.
- `sorgu`: Sistem durumunu sorgular.

## Klasör Yapısı

- `main.py`: Komut satırı giriş noktası.
- `core/`: Rezervasyon doğrulama, ücret, takvim, paket, bekleme ve simülasyon mantığı.
- `json_io/`: JSON ve JSONL dosya okuma/yazma işlemleri.
- `calistir/`: Komut yürütme döngüsü.
- `ui/`: `customtkinter` tabanlı masaüstü arayüzü.
- `ornek/` ve `test/`: Örnek senaryolar ve çıktı karşılaştırma (`test/karsilastir.py`) aracı.

## Test Çıktısı Karşılaştırma

Üretilen bir çıktı dosyasını beklenen sonuçla karşılaştırmak için:

```bash
python main.py test/1/baslangic.json test/1/komutlar.jsonl > cikti.jsonl
python test/karsilastir.py cikti.jsonl test/1/sonuclar.jsonl
```
