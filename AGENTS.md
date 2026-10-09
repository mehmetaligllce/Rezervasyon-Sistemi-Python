# AGENTS.md — Kampüs Kaynak Rezervasyon Sistemi

Bu dosya, bu projede çalışan **tüm ajanlar** (Claude Code, Cursor, Copilot vb.) için bağlayıcıdır. Çalışmaya başlamadan önce baştan sona oku. Kural belirsizse **tahmin etme, sor**.

---

## 0. Altın kurallar (özet)

1. Tek doğru kaynak proje PDF'idir (ana dizindeki `Yaz_Lab_I.pdf`). Bu dosyadaki özetle PDF çelişirse **PDF kazanır**; çelişkiyi kullanıcıya bildir.
2. Kural uydurma. PDF'te yazmayan bir davranışı kendi kafandan ekleme.
3. İş kuralı kodun içine sabit yazılmaz. Her parametre `baslangic.json` dosyasından okunur.
4. Arayüzde (`ui/`) **hiç iş kuralı** olmaz.
5. `main.py` sadece şeftir, iş kuralı içermez.
6. Kullanıcı demedikçe **asla commit atma**.
7. **Sadece istenen işi yap.** Kullanıcı sana bir iş verdiyse onu yap ve orada dur; kendiliğinden sonraki işe geçme. Kullanıcı "anlat" derse sadece anlat, "soru" sorarsa sadece cevapla. **"Yap" denmeden kod yazma, dosya değiştirme, bir şeyi uygulamaya çalışma.** Anlatma veya soru cevaplama sırasında fikrin varsa söyle, ama uygulama. İstenmeyen refactor, yeniden adlandırma, dosya taşıma yapma.
8. Test yazmak şimdilik kapsam dışıdır (kullanıcı en sona bıraktı). İstenmedikçe test dosyası ekleme.
9. Yazdığın kodu teslim etmeden önce kendin kontrol et (bkz. Bölüm 9).

---

## 1. Proje özeti

- Kocaeli Üniversitesi Yazılım Laboratuvarı I, Proje I.
- Arayüzden bağımsız bir **rezervasyon modülü** + bu modülü doğrudan kullanan bir **masaüstü uygulaması**.
- Modül, bir başlangıç dosyasını (`baslangic.json`) okur, komut dosyasındaki (`komutlar.jsonl`) komutları sırayla işler, her komut için bir sonuç satırı (`sonuclar.jsonl`) yazar.
- Çalıştırma: `./calistir.sh baslangic.json komutlar.jsonl > sonuclar.jsonl` (ve `calistir.bat`).
- Dil: **Python 3.11+**.
- Hedef: örnek senaryodaki 15 komutun sonucu **birebir** beklenenle eşleşmeli. Gizli testler satır satır, alan alan karşılaştırır. Eksik veya farklı alan hatadır, fazladan alan hata değildir.

---

## 2. Klasör yapısı

Klasör adları İngilizce ve lowercase'dir. Kullanıcı ileride değiştirebilir; değiştirmeyi sadece o ister.

```
main.py              → sadece şef, iş kuralı yok
calistir.sh
calistir.bat
requirements.txt
TASKS.md             → görev günlüğü (Bölüm 7)
AGENTS.md            → bu dosya
core/                → modeller, doğrulama (K10), ücret (K5), bekleme (K9), olaylar (K11)
girdi_cikti/         → başlangıç/komut okuma, sonuç yazma
ui/                  → sadece görüntü
tests/               → (şimdilik boş, en sonda doldurulacak)
docs/                → rapor, belirsizlikler.md (proje PDF'i ana dizinde: Yaz_Lab_I.pdf)
```

Kurallar:

- Python'un standart kütüphanesindeki adlarla çakışan klasör/dosya adı kullanma (`io`, `json`, `time`, `logging` vb.). Bu yüzden klasör adı `io` değil `girdi_cikti`.
- Her görev ayrı dosyada olur. Bir dosya tek bir konuya hizmet eder.
- `core/` hiçbir zaman `ui/` içinden bir şey import etmez. Bağımlılık yönü: `ui → core`, `main → hepsi`, `girdi_cikti → core`.
- `core/` ekrana yazmaz, `print` kullanmaz, dosya okumaz. Veriyi parametre olarak alır, sonucu döndürür.

---

## 3. İsimlendirme

- Dosya, değişken, fonksiyon adları: **snake_case**.
- Klasör adları: **lowercase**.
- Adlar Türkçe kelimelerden oluşabilir ama **Türkçe harf kullanılmaz** (ç→c, ğ→g, ı→i, ö→o, ş→s, ü→u). Örnek: `bekleme_listesi_tara`, `ucret_hesapla`.
- Yerleşmiş terimleri **çevirme**. `baslangic`, `bitis`, `kullanici`, `rezervasyon`, `kaynak`, `bakiye`, `guvenilirlik`, hata kodları, durum adları (`ONAYLI`, `GELMEDI`...) PDF'teki gibi kalır. `commit`, `main`, `request` gibi programcı terimleri de zorla Türkçeleştirilmez.
- Kullanıcı değişken ve fonksiyon adlarını kendisi yazmak istiyor. Ajan ad vermek zorunda kalırsa yukarıdaki biçime uyar ve verdiği adları raporunda belirtir.
- JSON alanları PDF'teki adlarla **birebir** aynıdır (`rezervasyon_id`, `ucret`, `bakiye`, `kalemler`...). Sonuç alanlarında ad değiştirme, ekleme-çıkarma yapma.

---

## 4. Mimari kurallar

- `main.py` yalnızca: argümanları al, girdi_cikti ile dosyaları oku, core'u çağır, sonuçları yaz. Başka hiçbir şey.
- Hiçbir kaynak türü, rol, fiyat, süre, saat sabiti kodda yazılmaz. `hazirlik_dk`, `temel_ucret`, `enerji_yogun`, `sertifika`, `haftalik_kota`, `ileri_gun`, `azami_sure_dk`, simüle saatin başlangıcı hep dosyadan gelir. `baslangic.json` değişince uygulama kod değişikliği olmadan yeni kurala göre çalışmalıdır (demoda denetlenecek).
- **Sabit kalabilen şeyler** (PDF'te sabit olarak yazılanlar): çalışma saati 08:00–22:00, 15 dakikalık adım, bant uzunluğu 2 saat, pik saat 10:00–16:00, min süre 30 dk, art arda kullanım boşluğu 60 dk, giriş penceresi (−10/+15 dk), gelmeme eşiği 15 dk, güvenilirlik eşiği 50, güvenilirlik değişimleri (−15, −5, +2), paket kalem aralığı 2–4. Bunları bile tek yerde, adlandırılmış sabit olarak tanımla; kodun içine dağıtma.
- Aynı mantığı iki yerde yazma. Fiyat önizlemesi, gerçek rezervasyon ve paket **aynı** doğrulama ve ücret fonksiyonlarını kullanır.
- Arayüz modülün sonuçlarını gösterir; kendi başına doğrulama veya hesap yapmaz.
- Bir fonksiyon tek iş yapar. Kullanıcı demoda kodunun herhangi bir satırını açıklamak zorunda; sade, okunabilir, "akıllıca" olmayan kod yaz.
- Gereksiz soyutlama, tasarım deseni, framework ekleme.
- Kod içi yorumlar **Türkçe** yazılır ama **az** yazılır. Her satıra veya her fonksiyona yorum ekleme. Yalnızca kodun neden öyle yazıldığı açık değilse yorum yaz (örneğin bir PDF kuralına veya sınır durumuna dayanan yerler: `# K3: bitiş hariç`).

---

## 5. Bağımlılıklar ve arayüz

- Standart kütüphaneyle çözülebilen şey için dış paket ekleme.
- **Yeni bir bağımlılık eklemeden önce kullanıcıya sor.**
- Arayüz kütüphanesi: **customtkinter** (Tkinter tabanlı, modern görünüm). Karar kesindir. Başka bir arayüz kütüphanesine geçme.
- Bağımlılık eklenirse `requirements.txt`'e yazılır ve `calistir.sh` / `calistir.bat` kurulumu kendisi yapar.

---

## 6. Alan kuralları: sık yapılan hatalar

Aşağısı PDF'in özetidir ve **eksiktir**. Uygulamadan önce ilgili K bölümünü PDF'ten oku.

### Zaman ve aralıklar
- Zaman biçimi `YYYY-AA-GGTSS:DD`. Aralıklar **başlangıç dahil, bitiş hariç**.
- `16:00'da biten` bir rezervasyonun yanına ODA için `16:00'da başlayan` talep geçerlidir (h=0).
- İleri tarih: başlangıç, `simüle saat + ileri_gun × 24 saat` sınırını **aşamaz** (tam sınır geçerli). Güvenilirlik 50'nin altındaysa `ileri_gun` 1 olur.

### Doğrulama sırası (K10) — ilk başarısız adımın kodu döner
1. `BULUNAMADI`
2. `ZAMAN_ADIMI_HATASI`
3. `GECMIS_ZAMAN`
4. `CALISMA_SAATI_DISI`
5. `SURE_SINIRI`
6. `ILERI_TARIH_SINIRI`
7. `ROL_IZNI_YOK`
8. `SERTIFIKA_YOK`
9. `BAKIM`
10. `KESISME`
11. `HAZIRLIK_IHLALI`
12. `ARDISIK_KULLANIM`
13. `BAKIYE_YETERSIZ`

- Giriş, çıkış, iptal sırası: `BULUNAMADI`, `DURUM_HATASI`, sonra (yalnızca giriş için) `GIRIS_PENCERESI_DISI`.
- `fiyat` komutu bakiye dışındaki tüm kontrolleri yapar, durum değiştirmez.

### Hangi durum nerede sayılır (K3, K4, K5)
- `KESISME`: yalnızca `ONAYLI` ve `KULLANIMDA`.
- `HAZIRLIK_IHLALI` ve `ARDISIK_KULLANIM`: `ONAYLI`, `KULLANIMDA`, `TAMAMLANDI`.
- `GELMEDI` ve `IPTAL` **hiçbir kontrolde** sayılmaz.
- Doluluk (K5) yalnızca `ONAYLI` ve `KULLANIMDA` sayar. Talebin kendisi ve bakım pencereleri sayılmaz.
- Bakım bittikten sonra hazırlık süresi **uygulanmaz**.

### Ücret (K5)
- 15 dakikalık dilimlerle hesaplanır. Her dilim kendi bandının çarpanını kullanır.
- Doluluk = o bantta dolu dakika / (türdeki kaynak sayısı × 120). Aynı gün ve o bant içinde kalan dakikalar toplanır.
- Bant çarpanı = `1 + 0,25 × ⌊4 × doluluk⌋` (doluluk 1 ise 2,0).
- Pik çarpanı 1,5 yalnızca `enerji_yogun` türlerde ve 10:00–16:00 diliminde.
- **Yuvarlama: yarım yukarı.** Python'un `round()` fonksiyonunu **kullanma** (banker's rounding yapar).
- **Float kullanma.** Kesirli hesabı tam sayı veya `fractions.Fraction` / `decimal` ile yap. `⌊4 × doluluk⌋` ve "tam 0,5" sınırları float hatasına duyarlıdır.

### Bakiye ve kota (K6)
- Ücret rezervasyon anında düşer. İade bakiyeye eklenir.
- Bakiye haftalık kotayı **aşamaz**; aşan kısım iade edilmez. Sonuçtaki `iade` alanı bakiyeye **gerçekten eklenen** miktardır.
- Simüle saat bir Pazartesi 00:00'ı geçince bakiye rolün kotasına **eşitlenir** (üstüne eklenmez, aktarma yok).

### Paket (K7)
- Denetim sırası: `BULUNAMADI`, `PAKET_BOYUTU`, `GUVENILIRLIK_DUSUK`, `PAKET_RED`, `PAKET_ICI_KESISME`, `BAKIYE_YETERSIZ`.
- Doğrulama ve ücret, paket istenmeden **önceki** duruma göre yapılır. Paketteki kalemler birbirinin doluluğuna katılmaz.
- Ya hepsi alınır ya hiçbiri. Hata biçimleri (`kalemler` alanı) PDF Bölüm 5'teki gibidir.

### Durum makinesi ve güvenilirlik (K8)
- Giriş penceresi: başlangıçtan 10 dk önce ile 15 dk sonra.
- İade: 24 saat ve üzeri %100; 2 saat ve üzeri, 24 saatten az %50 (**aşağı yuvarla**); 2 saatten az %0 ve güvenilirlik −5.
- `GELMEDI` −15, bitiş saatinde tamamlanan +2, erken çıkışta değişmez, erken çıkışta iade yok. Değer 0–100 arasında kıstırılır.

### Bekleme listesi (K9)
- Bekleme kaydı yalnızca başka bir rezervasyon yüzünden `KESISME` / `HAZIRLIK_IHLALI` alan talep için açılır. Başka hata varsa o kod döner; talep geçerliyse `BEKLEME_GEREKSIZ`. Açılırken bakiye kontrol edilmez.
- Sıralama: güvenilirlik **yüksek** önce; eşitse **önce kaydolan**; o da eşitse **numara sayısal** küçük olan (b2, b10'dan önce gelir; metin olarak sıralama).
- Her kayıt o anki saat ve bakiyeyle tüm K10 kontrollerinden geçer. Geçmeyen kayıt listede kalır, tarama listenin sonuna kadar sürer.
- Başlangıcı simüle saatten önceye düşen kayıtlar silinir.

### Saat ve olaylar (K11)
- Eski saatten sonraki ve yeni saate **kadar (yeni saat dahil)** tüm olaylar zaman sırasıyla işlenir.
- Aynı anda olay varsa sıra: `HAFTALIK_SIFIRLAMA`, tüm `TAMAMLANDI` (numara sırası), tüm `GELMEDI` (numara sırası), boşalan kaynaklar için bekleme taraması (`OTOMATIK_ATAMA`).
- Yeni saat eskiden önceyse `SAAT_GERI`.

### Kimlikler
- Rezervasyon `r1, r2, ...` (oluşturulma sırasıyla), paket `p1, ...`, bekleme `b1, ...`.

---

## 7. Görev günlüğü: `TASKS.md`

- Metin dosyasıdır, **sadece en alta ekleme** yapılır (append-only). Eski kayıtları silme, düzenleme, yeniden sıralama.
- Kayıtlar **Türkçe** yazılır.
- Kayıt biçimi:
  `V0.5 | 8/10 19:23 | k9 bekleme listesi eklendi | değişen: bekleme.py, olaylar.py`
  Yani: versiyon, gün/ay saat:dakika, ne yapıldığının **detaylı** anlatımı, değişen dosyalar.
- Tarih ve saat **gerçek sistem saatidir** (simüle saat değil). Tahmin etme; sistem saatini komutla oku (`date`).
- Versiyonlama: `V0.1, V0.2, ... V0.9, V0.10, V0.11 ...` (0.9'dan sonra **0.10** gelir, 1.0 değil). `V1`, `V2` ancak kullanıcının belirlediği kilometre taşlarına gelindiğinde yazılır.
- **Versiyon her küçük değişiklikte artmaz.** Dosyanın en altındaki "Adımlar" listesine göre yazılır: bir adım tamamlanınca o adımın versiyonu kaydedilir.
- Adım listesi tanımlı değilse versiyon **uydurma**; durup kullanıcıya "adım listesi tanımlı değil" de.
- Küçük düzeltme (hata/yazım) yeni versiyon açmaz; aynı versiyonun altına `düzeltme:` ile başlayan kısa bir satır olarak eklenir:
  `V0.5 | 9/10 14:05 | düzeltme: bekleme sıralaması ters çıkıyordu | değişen: bekleme.py`
- Kilometre taşları ve adım listesi `TASKS.md`'nin **en altında** durur. Kullanıcı belirler; ajan kendi başına değiştirmez.

---

## 8. Git

- **Kullanıcı açıkça "commit et" demeden veya sana sorup onay vermeden asla `commit` atma.**
- Bir adım bitince "commit atayım mı?" diye sorabilirsin; cevabı bekle.
- Onay gelirse mesaj biçimi: `v0.5: k9 bekleme listesi`. Çalışmayan kodu commitleme.
- `push`, `reset --hard`, `rebase`, `force`, branch silme gibi işlemleri kullanıcı istemeden yapma.
- Git kurulu değilse commit atmaya çalışma, sadece uyar.
- Etiket (`tag`) yalnızca kullanıcı bir kilometre taşını kapattığında ve istediğinde atılır.

---

## 9. Kendi kontrolün (bitirmeden önce)

Her işte "bitti" demeden önce:

1. Yazdığın kodu ilgili PDF bölümüyle (K numarası) satır satır karşılaştır.
2. Sınır durumlarına bak: bitiş hariç aralıklar, tam sınırdaki değerler (doluluk 0,25 / 0,5 / 0,75 / 1; tam 0,5 yuvarlama; 16:20 gibi hazırlık sınırları), boş liste, olmayan kullanıcı/kaynak.
3. Sonuç alanlarının adı, türü (sayı mı metin mi) ve sırası PDF'tekiyle uyuşuyor mu?
4. İş kuralı kodun içine sabit yazıldı mı? `ui/` içine iş mantığı sızdı mı?
5. Çalıştırabiliyorsan örnek senaryoyu (15 komut) koş ve beklenenle karşılaştır. Çalıştıramıyorsan bunu açıkça söyle; "geçti" deme.

**Önceki kodda gözünden kaçan bir hata fark edersen:** sessizce düzeltip geçme. Kullanıcıya hatayı ve düzeltmeyi söyle, `TASKS.md`'ye `düzeltme:` satırı olarak yaz.

---

## 10. Yapma listesi

- Kullanıcı açıkça "yap" demeden bir şeyi yapmaya başlama. Soru, açıklama veya fikir isteyen mesaja kod değişikliğiyle cevap verme.
- Bir işi bitirince kendiliğinden bir sonraki işe, "bir de şunu yapayım" diye geçme. Bitti de, sonraki adımı kullanıcıya bırak.
- Beklenen sonucu, örnek senaryoyu veya komut dosyasını "geçsin diye" değiştirme.
- Hata veya sapma varsa gizleme; açıkça raporla.
- Varsayım yaptıysan **açıkça belirt**, sessizce uygulama.
- İstenmeyen dosya, klasör, özellik ekleme.
- Mevcut kodu sormadan silme veya baştan yazma.
- PDF'te yazmayan hata kodu, durum veya alan icat etme.
- Test dosyası ekleme (kullanıcı en sonda yapacak).
- Türkçe harfli dosya/değişken/fonksiyon adı kullanma.

---

## 11. Teslim edilecekler (hatırlatma)

- Modül + masaüstü uygulaması kaynak kodu, `calistir.sh`, `calistir.bat`, çalıştırma adımlarının açıklaması.
- Kendi test senaryoları (komut dosyaları + beklenen sonuçlar). *En sonda.*
- Rapor: IEEE formatında 4 sayfa (özet, giriş, yöntem, deneysel sonuçlar, tasarım kararları, sonuç, kaynakça). *En sonda.*
- Teslim tarihi: **25 Ekim 2026**.
- Demo yüz yüzedir; kullanıcı kodunun herhangi bir satırını açıklamak zorunda kalabilir. Bu yüzden kod **sade ve açıklanabilir** olmalı.

---

## 12. Hatalı girdi: modül çökmez

- Komut dosyasındaki bir satır bozuksa modül **çökmez**. O satır için `RED` sonuç satırı yazılır, sonraki satırlara devam edilir. Çıktıda komut sırası (`no`) kaymaz: bozuk satır da bir sıra numarası alır.
- PDF bu durumu tanımlamıyor; projeye özel **tek bir** kod kullanılır: `JSON_HATALI`. Satır geçerli JSON değilse, `komut` alanı yoksa veya tanınmayan bir değerse, zorunlu bir alan eksik veya türü yanlışsa hep bu kod döner. Başka hata kodu icat etme.
- Bu kod PDF'teki hata kodlarının yerine geçmez. PDF'te tanımlı bir hata varsa onun kodu kullanılır (örneğin bilinmeyen kullanıcı için `BULUNAMADI`).
- `baslangic.json` bozuksa işlem yapılamaz: stderr'e açık bir hata mesajı yaz ve sıfırdan farklı çıkış koduyla bitir. Sessizce devam etme.
- Hata mesajı ve ayrıntısı stderr'e gider, stdout'a değil (Bölüm 13, madde 1).

---

## 13. Çalışma disiplini

**Gizli testleri doğrudan etkileyenler**

1. **stdout'a yalnızca sonuç satırları yazılır.** Çalıştırma `> sonuclar.jsonl` ile yönlendirildiği için tek bir hata ayıklama `print`'i tüm dosyayı bozar. Log ve debug çıktısı stderr'e gider. Dosyaları ve çıktıyı açıkça **UTF-8** ile oku/yaz (Windows'ta Türkçe karakterlerde sorun çıkarır).
2. **`core/` içinde gerçek saat yasak.** `datetime.now()` ve benzeri çağrılar yalnızca `TASKS.md` kaydı için kullanılır. Modül yalnızca simüle saati bilir. Aksi halde sonuçlar çalıştırıldığı güne göre değişir.
3. **Bekleme taraması tetikleyicileri.** PDF'e göre yer boşalması iptal, gelmeme ve çıkış olaylarıdır. Rezervasyonun bitiş saatinde kendiliğinden tamamlanmasını tetikleyici sayma. Emin değilsen belirsizlik defterine yaz (madde 7).
4. **Birden çok banda yayılan rezervasyon.** Doluluk hesabında bir rezervasyonun yalnızca o banda düşen dakikaları sayılır; tüm süreyi tek banda yazma.
5. **Girdi dosyaları değişmez.** `baslangic.json` ve komut dosyaları salt okunurdur. Modül belleğe kopya alır, dosyaya yazmaz.

**Çalışma düzeni**

6. **Oturum başı rutini.** İşe başlamadan önce `AGENTS.md`'yi ve `TASKS.md`'nin son kayıtlarını oku. Projeyi hafızadan veya tahminle sürdürme.
7. **Belirsizlik defteri.** PDF'te net olmayan bir yer bulursan tahmin etme: `docs/belirsizlikler.md` dosyasına yaz (hangi K bölümü, neyin belirsiz olduğu, hangi yorumlar mümkün) ve kullanıcıya sor. Dosya yoksa oluşturmadan önce sor.
8. **Tasarım kararı kaydı.** Önemli bir tasarım seçimi yapıldığında `TASKS.md`'ye `karar:` ile başlayan bir satır ekle (ne seçildi, neden). Rapordaki "tasarım kararları" bölümü bunlardan beslenir.
9. **Yıkıcı komutlar önce sorulur.** `rm`, toplu taşıma/yeniden adlandırma, `baslangic.json` veya mevcut kaynak dosyaları ezme gibi geri alınamaz işlemlerden önce kullanıcıdan onay al.
10. **Durum tek yerde.** Rezervasyonlar, bakiyeler, bekleme listesi, simüle saat tek bir sistem nesnesinde tutulur. Global değişken kullanma. Komut satırı ve arayüz **aynı** nesne yapısını kullanır; iki tarafın sonucu farklı çıkmamalıdır.
11. **Ajan kullanıcıyla Türkçe konuşur.** Teknik terimleri (`commit`, `import`, `push` vb.) çevirmez.

---

## Adımlar ve kilometre taşları

> Bu bölümü kullanıcı dolduracak. Doldurulana kadar ajan versiyon numarası uydurmaz.
