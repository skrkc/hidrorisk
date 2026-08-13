# HidroRisk

HidroRisk, yerel bir LLM (Ollama üzerinden çalışan Qwen modeli) ile geliştirilmiş, **hidroloji ve hidrolik odaklı bir tool-calling asistanıdır**.

Bu proje, ders kapsamında verilen `ollama_asistan` yapısı temel alınarak özelleştirilmiştir. Örnek medikal senaryo yerine, hidroloji ve hidrolik alanına yönelik bir senaryo tasarlanmıştır.

## Proje Amacı

Bu asistanın amacı, kullanıcının sorduğu hidroloji/hidrolik sorularında:

- gerekli ise uygun aracı (tool) çağırmak,
- sayısal hesapları uygun araçları kullanarak gerçekleştirmek,
- sonuçları Türkçe ve anlaşılır biçimde sunmak,
- gerektiğinde internet araması yapmak,
- SPI analizi ve grafik üretimi gibi işlemleri desteklemektir.

## Senaryo

Bu proje genel amaçlı bir asistan yerine, hidroloji ve hidrolik alanına odaklanan bir senaryo ile geliştirilmiştir:

**HidroRisk = Yerel Hidroloji ve Hidrolik Risk Asistanı**

Asistan özellikle şu alanlara odaklanır:

- Rasyonel Yöntem ile pik debi hesabı
- Manning denklemi ile açık kanal kapasite kontrolü
- Aylık yağış verilerinden SPI hesabı
- SPI zaman serisi grafiği oluşturma
- Gerekli durumlarda internet araması

## Kullanılan Model

- **LLM:** `qwen3:4b-instruct-2507-q4_K_M`
- **Çalıştırma ortamı:** Ollama (local)
- **Arayüz:** Terminal / CLI

## Özellikler / Tool'lar

Projede aşağıdaki araçlar bulunmaktadır:

1. **calculate_peak_runoff**
   - Rasyonel Yöntem ile pik yüzey akış debisi hesaplar.

2. **check_channel_capacity**
   - Manning denklemi ile dikdörtgen açık kanalın tasarım debisini taşıyıp taşıyamayacağını kontrol eder.

3. **calculate_spi**
   - Aylık yağış verisi içeren CSV dosyasından SPI hesaplar.

4. **plot_spi_series**
   - SPI zaman serisi grafiği üretir ve PNG olarak kaydeder.

5. **internet_search**
   - Gerekli durumlarda internet araması yapar.

## Proje Yapısı

```text
hidrorisk/
│
├── assets/
│   ├── hidrorisk_terminal.png
│   └── spi12_example.png
│
├── data/
│   └── yagis_ornek.csv
│
├── outputs/
│   └── (program calistikca olusan grafik dosyalari)
│
├── chat.py
├── tools.py
├── ollama_client.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Kurulum
1) Repoyu klonlayın

```text
git clone https://github.com/skrkc/hidrorisk.git
cd hidrorisk
```

2) Sanal ortam oluşturun ve aktif edin

Windows PowerShell veya VS Code içindeki PowerShell terminali:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

3) Gerekli paketleri kurun

```powershell
python -m pip install -r requirements.txt
```

4) Ollama’yı açın

Ollama uygulamasının açık olması gerekir.

5) Gerekli modeli indirin

```powershell
ollama pull qwen3:4b-instruct-2507-q4_K_M
```

## Çalıştırma

```powershell
python chat.py
```

### Örnek Terminal Arayüzü

Program açıldığında aşağıdaki gibi bir ekran görülür:

```text
============================================================
                         HIDRORISK
          Yerel Hidroloji ve Hidrolik Risk Asistani
============================================================

Model : qwen3:4b-instruct-2507-q4_K_M

Araclar:
  [1] Pik Debi Hesabi
  [2] Acik Kanal Kapasitesi
  [3] SPI Kuraklik Analizi
  [4] SPI Grafik Olusturma
  [5] Internet Aramasi

Cikmak icin: cik
------------------------------------------------------------
```

#### Terminal Görünümü

![HidroRisk Terminal Arayüzü](assets/hidrorisk_terminal.png)

### Örnek Konuşmalar

#### 1) Kavramsal Soru

Kullanıcı:

```text
Manning denklemi ne icin kullanilir? Kisa cevap ver.
```

Asistan:

```text
Manning denklemi, acik kanallarda akis hizi ve debinin hesaplanmasinda kullanilir.
```

#### 2) Pik Debi Hesabı (Rasyonel Yöntem)

Kullanıcı:

```text
Akim katsayisi 0.6, yagis siddeti 50 mm/saat ve havza alani 10 hektar. Rasyonel Yontem ile pik debiyi hesapla.
```

Tool çağrısı:

```text
[TOOL] calculate_peak_runoff({'runoff_coefficient': 0.6, 'rainfall_intensity_mm_h': 50, 'catchment_area_ha': 10})
```

Asistan:

```text
Rasyonel Yontem ile hesaplanan pik debi 0.8333 m3/s (833.33 L/s) olarak bulundu.
```

#### 3) Açık Kanal Kapasite Kontrolü

Kullanıcı:

```text
Tasarim debisi 2 m3/s olan dikdortgen bir kanalin genisligi 2 m, su derinligi 1 m, Manning n katsayisi 0.015 ve taban egimi 0.001. Kanal bu debiyi tasiyabilir mi?
```

Tool çağrısı:

```text
[TOOL] check_channel_capacity({'design_discharge_m3_s': 2, 'width_m': 2, 'water_depth_m': 1, 'manning_n': 0.015, 'bed_slope': 0.001})
```

Asistan:

```text
Evet. Kanal kapasitesi 2.656 m3/s olarak hesaplandi. Tasarim debisi 2.000 m3/s oldugu icin kanal verilen hesap kosullarinda YETERLI.
```
#### Multi-turn örneği

Kullanıcı:

```text
Peki tasarim debisi 3 m3/s olsaydi?
```

Tool çağrısı:

```text
[TOOL] check_channel_capacity({'design_discharge_m3_s': 3, 'width_m': 2, 'water_depth_m': 1, 'manning_n': 0.015, 'bed_slope': 0.001})
```

Asistan:

```text
Hayir. Kanal kapasitesi 2.656 m3/s oldugu icin 3.000 m3/s tasarim debisini karsilayamiyor. Sonuc: YETERSIZ.
```

#### 4) SPI Hesabı ve Grafik Oluşturma

Kullanıcı:

```text
data/yagis_ornek.csv dosyasi icin SPI-12 hesapla ve grafigini olustur.
```

Tool çağrıları:

```text
[TOOL] calculate_spi({'file_path': 'data/yagis_ornek.csv', 'scale': 12})

[TOOL] plot_spi_series({'file_path': 'data/yagis_ornek.csv', 'scale': 12})
```

Asistan:

```text
Yagis verisi icin SPI-12 hesabi tamamlandi ve grafigi olusturuldu.

- Son tarih: 2020-12
- Son SPI-12 degeri: 0.187
- SPI-12 sinifi: normale yakin
- Yorum: Bu SPI-12 sinifi yalnizca 2020-12 donemini temsil eder; tum veri serisinin genel durumunu temsil etmez.

Grafik ve hesap sonucunu destekleyen dosyalar:
- SPI-12 hesap sonucu dosyasi
- SPI-12 zaman serisi grafigi
```

#### Örnek SPI Grafiği

![SPI-12 Örnek Grafiği](assets/spi12_example.png)

#### 5) İnternet Araması

Kullanıcı:

```text
Internetten DSI'nin taskin yonetimiyle ilgili 3 kaynak bul.
```

Tool çağrısı:

```text
[TOOL] internet_search({'query': "DSI'nin taskin yonetimi", 'max_results': 3})
```

Asistan:

```text
1. Devlet Su Isleri Genel Mudurlugu - DSI
   https://dsi.gov.tr/Sayfa/Detay/1872

2. Devlet Su Isleri Genel Mudurlugu - DSI
   https://dsi.gov.tr/Sayfa/Detay/1870

3. Devlet Su Isleri Teknik Arastirma ve Kalite Kontrol Dairesi Baskanligi
   https://takk.dsi.gov.tr/
```

## Önemli Notlar

- HidroRisk bir ön değerlendirme asistanıdır.
- Sonuçlar, nihai mühendislik projesi veya resmi onay yerine kullanılmamalıdır.
- Asistanın raporladığı "Son SPI-X" değeri ve sınıfı yalnızca belirtilen son dönemi temsil eder; tüm veri serisinin genel durumu gibi yorumlanmamalıdır.
- İnternet araması sonuçlarında araçtan dönmeyen kaynaklar/URL’ler eklenmez.

## Kullanılan Veri

Projede örnek amaçlı sentetik bir aylık yağış verisi kullanılmıştır:

- `data/yagis_ornek.csv`

Bu dosya, SPI analizi ve grafik üretimi için örnek veri sağlamaktadır.

## Geliştirme Özeti

Bu projede, verilen örnek `ollama_asistan` yapısı korunarak:

- medikal senaryo kaldırılmış,
- yerine hidroloji/hidrolik odaklı bir senaryo eklenmiş,
- özel tool’lar geliştirilmiş,
- terminal arayüzü düzenlenmiş,
- SPI grafiği üreten ek bir görselleştirme aracı eklenmiştir.

## Kullanım Notu

Bu proje eğitim amaçlı hazırlanmıştır.
