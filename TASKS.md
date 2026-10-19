# TASKS.md — Görev günlüğü

Kurallar `AGENTS.md` Bölüm 7'dedir. Özet:

- Kayıtlar **Kayıtlar** bölümünün sonuna eklenir (hemen "Adımlar" bölümünün üstüne). Eski kayıt silinmez, düzenlenmez.
- Biçim: `V0.5 | 8/10 19:23 | ne yapıldığının detaylı anlatımı | değişen: x.py, y.py`
- Tarih/saat gerçek sistem saatidir. Dil Türkçedir.
- Küçük düzeltme yeni versiyon açmaz: `V0.5 | 9/10 14:05 | düzeltme: ... | değişen: ...`
- Tasarım kararı: `V0.5 | 9/10 14:10 | karar: ... (neden)`

---

## Kayıtlar

V0.1 | 09/10 10:54 | Proje iskeleti kuruldu, dosya okuma/yazma (baslangic.json, komutlar.jsonl, JSON Lines çıktı), sabitler dosyası ve main.py şef yapısı bağlandı | değişen: json_io/dosya_okuma.py, core/sabitler.py, main.py, calistir.bat

V0.2 | 10/10 10:31 | K10 doğrulama 1–12. kontrol yazıldı (BULUNAMADI'dan ARDISIK_KULLANIM'a, PDF sırasıyla). Rezervasyon döngüleri KESISME, HAZIRLIK_IHLALI ve ARDISIK_KULLANIM için ayrı ayrı çalışır. Örnekte 4, 5, 9, 10. komutlar beklenen hata kodunu verdi. 3. ve 6. komut sahte rezervasyonla elle denendi (ARDISIK_KULLANIM, HAZIRLIK_IHLALI doğru). Her komut için bir satır üretiliyor, geçerli talepte yalnızca no, komut, durum:TAMAM döner. 13. kontrol (BAKIYE_YETERSIZ) ve ücret V0.3'e bırakıldı | değişen: core/dogrulama.py, core/yard_fonksiyonlar.py, json_io/dosya_okuma.py, main.py

V0.3 | 10/10 15:47 | K5 ücret hesaplama (15 dk dilimler, 2 saatlik bant doluluğu ve çarpanı, pik saat 10:00-16:00 ve enerji_yogun 1.5x katsayısı, yarım yukarı yuvarlama), 13. kontrol (BAKIYE_YETERSIZ), rezervasyon onayında id atama ve bakiye düşümü, fiyat sorgusu tamamlandı. Örnek senaryodaki 1-7, 9, 10. komutlar beklenen sonuçlarla birebir doğrulandı | değişen: core/yard_fonksiyonlar.py, core/dogrulama.py, json_io/dosya_okuma.py

V0.4 | 10/10 21:11 | K6 bakiye/iade/haftalık kota, K8 durum makinesi (giris penceresi -10/+15 dk, erken cikis bitiş saati güncellemesi, iptal 3 kademeli iade ve geç iptal güvenilirlik cezası) uygulandı. Hata sıralaması (BULUNAMADI, DURUM_HATASI, GIRIS_PENCERESI_DISI) ve güvenilirlik sınırları [0, 100] sağlandı. Tüm sınır durumları ve kota kuralı doğrulandı | değişen: core/durum.py, json_io/dosya_okuma.py

V0.5 | 11/10 11:58 | K11 saat ilerletme (SAAT_GERI kontrolü, Pazartesi HAFTALIK_SIFIRLAMA bakiye kota eşitlemesi, TAMAMLANDI ve GELMEDI olayları, K11 öncelik ve zaman sıralaması) ve sorgu komutu (kullanici bakiye/guvenilirlik/rezervasyon listesi ve kaynak günlük doluluk/bakım listesi) tamamlandı. Örnek senaryodaki 12, 13 ve 15. komutlar doğrulandı | değişen: core/simule.py, core/sorgu.py, json_io/dosya_okuma.py

V0.6 | 11/10 14:14 | K7 paket rezervasyon (BULUNAMADI, PAKET_BOYUTU, GUVENILIRLIK_DUSUK, PAKET_RED bakiye hariç 1–12 kontrol, PAKET_ICI_KESISME çakışma ve hazırlık denetimi, BAKIYE_YETERSIZ) uygulandı. Onaylanan paket ve kalemler sisteme kaydedilerek yeni rezervasyon kimlikleri atandı. Örnek senaryodaki 8. komut (p1, r3–r4, ücretler [48, 8], bakiye 244) ve 14. komut (iptal r4, iade 4, bakiye 248) birebir doğrulandı | değişen: core/paket.py, core/dogrulama.py, json_io/dosya_okuma.py

V0.7 | 11/10 17:24 | K9 bekleme listesi (KESISME ve HAZIRLIK_IHLALI ile bekleme kaydı açma, BEKLEME_GEREKSIZ denetimi, güvenilirlik/kayıt saati/id sıralaması) ve otomatik atama (yer boşalınca tarama, K10 doğrulama ve OTOMATIK_ATAMA olay üretimi) uygulandı. Örnek senaryodaki 15 komutun tamamı beklenen sonuçlarla birebir doğrulandı | değişen: core/bekleme.py, core/simule.py, json_io/dosya_okuma.py, core/dogrulama.py

V0.8 | 11/10 17:40 | Parametre değişikliği kontrolü yapıldı. Kodda sabit yazılmış parametre olmadığı tarandı; temel_ucret (12 -> 24 ile ücret 36 -> 72), hazirlik_dk (20 -> 10 ile HAZIRLIK_IHLALI -> BASARILI) ve ileri_gun (7 -> 14 ile ILERI_TARIH_SINIRI -> BASARILI) olmak üzere 3 farklı parametre değişikliğinin koda dokunmadan sonuçları dinamik olarak değiştirdiği doğrulandı. V1 kilometre taşı tamamlandı | değişen: yok (kod taraması ve dinamik doğrulama yapıldı)

V0.8 | 11/10 18:16 | düzeltme: Yeni doküman ve örnekle gelen kullanici_ekle ve kaynak_ekle komutları eklendi, K10 yeni hata kontrolleri (ID_MEVCUT, TANIMSIZ_DEGER, GECERSIZ_DEGER) ve tüm sınır durumları doğrulandı. Yeni 19 komutluk senaryo 19/19 birebir başarıyla geçti | değişen: core/ekle.py, json_io/dosya_okuma.py

V0.9 | 11/10 21:09 | Takvim verisi üretme fonksiyonu yazıldı. Seçilen gün için her kaynağın tüm rezervasyonları (tüm durumlar), hazırlık aralıkları ve bakım pencereleri kronolojik olarak toplandı; çakışan durumlar (iptal/gelmedi üzerine yeni rezervasyon) için alt satır katman numaralandırması yapıldı | değişen: core/takvim.py

V0.10 | 11/10 21:20 | Masaüstü arayüzü 1 (CustomTkinter) tamamlandı: 08:00–22:00 kaynak takvimi, durum renkleri, bakım ve hazırlık kutuları, simüle saat çizgisi, takvim kutusu detay penceresi; rezervasyon talep formu (anlık fiyat önizleme, bakiye denetimi, Türkçe açıklamalı hata mesajları ve onay) bağlandı ve örneğe göre doğrulandı | değişen: ui/talep_formu.py, ui/takvim_gorunumu.py, ui/app.py, requirements.txt

---

## Adımlar ve kilometre taşları

Ajan **yalnızca** buradaki adımlar için versiyon yazar. Bir adım, "Bitti sayılır" koşulu sağlanınca tamamlanır. Adımlar sırayla yapılır, atlanmaz. Listeyi yalnızca kullanıcı değiştirir.

**Genel not (V0.1–V0.7):** `iptal`, `cikis` ve `saat` çıktısındaki `olaylar` alanı bekleme listesi bağlanana kadar (V0.7) **boş liste** döner. Ajan erken bağlamaya çalışmaz.

**Karşılaştırma:** Doğrulama için çıktı, beklenen sonuç dosyasıyla `diff` ile kıyaslanır (`tests/ornek/beklenen_sonuclar.jsonl`). Test kodu yazılmaz.

**V0.1 — İskelet ve dosya işleri**

- Klasörleri aç: `core/`, `girdi_cikti/`, `ui/`, `tests/`, `docs/`.
- `calistir.sh`, `calistir.bat`, `requirements.txt`, bu dosya (`TASKS.md`).
- `docs/belirsizlikler.md` dosyasını aç (yapmadan önce kullanıcıya sor). PDF'te net olmayan yerler baştan buraya yazılır; sorular e-destek forumuna buradan gider.
- Sabitleri tek dosyada tanımla: 08:00–22:00, 15 dk adım, 2 saatlik bant, pik 10–16, min süre 30, boşluk 60, giriş penceresi (−10/+15), gelmeme eşiği 15, güvenilirlik değerleri ve eşik, paket 2–4.
- Modelleri yaz: kaynak türü, rol, kaynak, kullanıcı, rezervasyon, bakım penceresi, bekleme kaydı.
- Zaman işlemleri: `YYYY-AA-GGTSS:DD` ayrıştırma, dakika hesabı, 15 dk kontrolü.
- `baslangic.json` okuma, `komutlar.jsonl` okuma, sonuç yazma. UTF-8, stdout'a yalnızca sonuç satırı.
- `main.py` şef olarak çalışır.
- Bozuk komut satırı için `JSON_HATALI`. Bozuk `baslangic.json` için stderr'e hata ve sıfırdan farklı çıkış kodu.
- **Bitti sayılır:** `./calistir.sh baslangic.json komutlar.jsonl` her komut için `no` ve `komut` içeren bir satır üretir. İş kuralı henüz yoktur.

**V0.2 — K10 doğrulama (1–12. kontrol)**

- 12 kontrolü PDF'teki sırayla yaz (`BULUNAMADI`'dan `ARDISIK_KULLANIM`'a). İlk başarısız kod döner.
- K1, K2 (bakım), K3 (durum kuralları: `KESISME` yalnızca `ONAYLI` ve `KULLANIMDA`; `HAZIRLIK_IHLALI` ayrıca `TAMAMLANDI`), K4.
- `fiyat` komutu hata kodlarını döner. Geçerli talep için ücret henüz yoktur: bu durumda ajan değer uydurmaz, V0.1'deki gibi yalnızca `no` ve `komut` döner.
- **Bitti sayılır:** Örnekte 4, 5, 9, 10. komutlardaki talepler `fiyat` olarak gönderilince beklenen hata kodunu döner.

**V0.3 — K5 ücret, 13. kontrol, `rezervasyon` ve `fiyat`**

- Ücret: 15 dk dilimler, bant doluluğu, çarpan, pik çarpanı, yarım yukarı yuvarlama. Float yok.
- `BAKIYE_YETERSIZ` (13. kontrol).
- `rezervasyon` komutu: id (`r1`...), ücretin bakiyeden düşmesi.
- `fiyat` komutu tamamlanır: aynı fonksiyonlar, bakiye kontrolü yok, durum değişmez.
- **Bitti sayılır:** Örnekte 1–7, 9, 10. komutlar beklenen sonucu verir.

**V0.4 — K6 bakiye, K8 durum makinesi, güvenilirlik**

- K6: iade, haftalık kotayı aşmama, `iade` alanı gerçekte eklenen miktar.
- K8: `giris` (pencere −10/+15), `cikis` (erken çıkış, iade yok), `iptal` (iade oranları, aşağı yuvarlama, geç iptal −5).
- Hata sırası: `BULUNAMADI`, `DURUM_HATASI`, `GIRIS_PENCERESI_DISI`.
- Güvenilirlik 0–100 arasında kıstırılır.
- **Bitti sayılır:** Ajan kısa bir deneme komut dosyası hazırlar (giriş penceresi sınırları, erken çıkış, üç iade oranı) ve sonucu kullanıcıya gösterir; kullanıcı PDF'e göre doğrular. Örnekteki 14. komut V0.6'da paket yazılınca çıkar, çünkü `r4` pakettedir.

**V0.5 — Saat olayları ve sorgu**

- `saat` komutu: `GELMEDI`, `TAMAMLANDI`, `HAFTALIK_SIFIRLAMA` olayları, K11 sıralaması, `SAAT_GERI`.
- `sorgu` komutu: kullanıcı ve kaynak (günlük doluluk) çıktıları.
- Belirsizlik defterini gözden geçir, kullanıcıya sorulacakları listele.
- **Bitti sayılır:** Örnekte 12. komutun iki `GELMEDI` olayı doğru çıkar (üçüncü olay `OTOMATIK_ATAMA` V0.7'de). 13. komut çıkar. 15. komut V0.7'de çıkar, çünkü `r5` bekleme listesinden gelir.

**V0.6 — K7 paket**

- Paket denetim sırası, `PAKET_RED` ve `kalemler` çıktıları, ya hepsi ya hiçbiri.
- Doğrulama ve ücret paket öncesi duruma göre yapılır, kalemler birbirinin doluluğuna katılmaz.
- **Bitti sayılır:** Örnekte 8. komut (p1, [r3, r4], toplam 56, bakiye 244) ve 14. komut (iptal r4, iade 4, bakiye 248) çıkar.

**V0.7 — K9 bekleme listesi**

- `bekleme` komutu, `BEKLEME_GEREKSIZ`, sıralama (güvenilirlik, kayıt zamanı, numara sayısal), `OTOMATIK_ATAMA`.
- Tetikleyiciler: iptal, gelmeme, çıkış. `olaylar` alanları artık gerçek bağlanır.
- Başlangıcı simüle saatten önceye düşen bekleme kayıtlarını sil.
- **Bitti sayılır:** 15 komutun tamamı beklenen sonuçla birebir eşleşir.

**V0.8 — Parametre değişikliği kontrolü**

- `baslangic.json` içinde bir parametre değiştirilir (örneğin `YAZICI` hazırlığı 30, bir fiyat, bir rol sınırı) ve sonucun **koda dokunmadan** değiştiği doğrulanır.
- Kodda sabit yazılmış iş kuralı kalmadığını tarama.
- **Bitti sayılır:** Üç farklı parametre değişikliği koda dokunmadan beklenen yönde sonuç değiştirir.

> **V1 kilometre taşı:** V0.1–V0.8 tamam. Motor çalışıyor, örnek senaryo birebir geçiyor, parametreler dosyadan geliyor.

**V0.9 — Takvim verisi (core)**

- `core/` içinde ayrı bir fonksiyon: seçilen gün için her kaynağın tüm rezervasyonları (her durum), hazırlık aralıkları ve bakım pencereleri.
- Bu veri `sorgu` çıktı biçimini değiştirmez; arayüz içindir ve arayüzde hesap yapılmaz.
- **Bitti sayılır:** Örnek senaryo sonrası bir gün için fonksiyon doğru kutuları, hazırlık ve bakım aralıklarını döner.

**V0.10 — Arayüz 1**

- customtkinter. Kaynak takvimi: 08–22 ekseni, durum renkleri, bakım ve hazırlık gösterimi. Talep formu: fiyat önizleme, hata kodu ve açıklama.
- **Bitti sayılır:** Takvimde örnek senaryonun rezervasyonları görünür, formdan fiyat önizlemesi ve red mesajı alınır.

**V0.11 — Arayüz 2**

- Kullanıcı paneli, eylem düğmeleri (giriş, çıkış, iptal, bekleme), simüle saat denetimi ve olay günlüğü.
- **Bitti sayılır:** Örnek senaryo arayüzden elle yürütülebilir; arayüz ve komut satırı aynı sonucu verir.

> **V2 kilometre taşı:** V0.9–V0.11 tamam. Masaüstü uygulaması çalışıyor.

**V0.12 — Test senaryoları ve beklenen sonuçlar** (en sonda)

- Kendi komut dosyaların ve beklenen sonuçları `tests/` içinde.

**V0.13 — Rapor ve teslim hazırlığı**

- `docs/` içinde IEEE formatında 4 sayfalık rapor. `TASKS.md` içindeki `karar:` satırları "tasarım kararları" bölümüne kaynaktır.
- Çalıştırma adımlarının açıklaması.

> **V3 kilometre taşı:** V0.12–V0.13 tamam. Teslim edilebilir. Son tarih 25 Ekim 2026.
