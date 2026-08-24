# Quantamental Platform — Ürün, Veri ve Hesaplama Spesifikasyonu

## 1. Amaç

Quantamental Platform; hisse, ETF, kripto, döviz, emtia ve endeksleri aynı çerçevede izleyen bir karar-destek uygulamasıdır. Amaç, farklı veri kaynaklarından gelen piyasa ve finansal verileri standartlaştırmak; teknik görünüm, değerleme, kalite, büyüme ve bilanço dayanıklılığını açıklanabilir bir skora dönüştürmektir.

Bu sistem yatırım tavsiyesi üretmez. Ürettiği sinyal, tanımlı kuralların ve mevcut verinin kantitatif sonucudur.

```text
Varlık evreni
→ ham piyasa / finansal veri
→ standart veri modeli
→ metrik hesapları
→ kategori puanları
→ bileşik skor ve güven seviyesi
→ sinyal, sıralama ve detay analizi
```

## 2. Kapsanan varlık sınıfları

| Varlık sınıfı | Ana analiz biçimi | Finansal tablo gerekir mi? |
|---|---|---:|
| Hisse senedi | Teknik + temel analiz + bilanço dayanıklılığı | Evet |
| Banka / sigorta | Teknik + sektöre uygun temel analiz | Evet, farklı şablon |
| ETF | Teknik + fiyat/momentum + fon bağlamı | Hayır |
| Kripto | Teknik + momentum + piyasa riski | Hayır |
| Döviz | Teknik + momentum + makro bağlam | Hayır |
| Emtia | Teknik + momentum + makro bağlam | Hayır |
| Endeks | Teknik + momentum + piyasa rejimi | Hayır |

Şirket finansallarına dayanan metrikler, ETF/kripto/döviz/emtia/endeks için sıfır olarak atanmaz. Bunlar `structural_na` olarak işaretlenir; yani metrik o varlık sınıfına yapısal olarak uygulanamaz.

## 3. Veri katmanı

### 3.1 Varlık kimliği ve evren verisi

Her kayıt en az şu alanları taşımalıdır:

```text
symbol                Uygulama içi kanonik sembol
provider_symbol       Veri sağlayıcının istediği sembol
asset_class           US_STOCK, BIST_STOCK, ETF, CRYPTO vb.
exchange              NASDAQ, NYSEARCA, IST, BINANCE vb.
name                  Varlık adı
sector                Sektör; hisseler için zorunluya yakın
industry              Varsa alt sektör
currency              Fiyat ve finansal tablo para birimi
is_active             Aktif evrende olup olmadığı
```

Sembol dönüşümü sağlayıcıya özgüdür. Örnekler:

```text
Uygulama: NASDAQ:AAPL      Google Finance: AAPL:NASDAQ      TradingView: NASDAQ:AAPL
Uygulama: BIST:THYAO       Google Finance: THYAO:IST        TradingView: BIST:THYAO
Uygulama: BINANCE:BTCUSDT  Google Finance: BTC-USD          TradingView: BINANCE:BTCUSDT
Uygulama: AMEX:SPY         Google Finance: SPY:NYSEARCA     TradingView: AMEX:SPY
```

### 3.2 Piyasa verisi

Teknik analiz için gerekli kanonik OHLCV alanları:

```text
timestamp
open
high
low
close
adjusted_close        Varsa; bölünme/temettü etkisi düzeltilmiş fiyat
volume                Hisse/ETF/kripto için; yoksa null
currency
source_name
fetched_at
```

Minimum teknik hesaplar için günlük kapanış serisi gerekir. Sağlıklı SMA200 ve uzun vadeli momentum için en az 200 işlem günü, tercihen 252 işlem günü gerekir.

### 3.3 Hisse finansal tabloları

Hisse analizi için yıllık mali tablolar ve mümkünse TTM/MRQ verisi gerekir.

#### Gelir tablosu

```text
revenue
cost_of_revenue
gross_profit
operating_income / ebit
ebitda
interest_expense
pretax_income
income_tax_expense
net_income
eps_diluted
weighted_average_shares_diluted
```

#### Bilanço

```text
cash_and_short_term_investments
accounts_receivable
inventory
total_current_assets
total_assets
short_term_debt
long_term_debt
total_debt
accounts_payable
total_current_liabilities
total_liabilities
total_stockholders_equity
retained_earnings
```

#### Nakit akış tablosu

```text
operating_cash_flow
capital_expenditure
free_cash_flow                 Hesaplanabiliyorsa: OCF - capex
depreciation_and_amortization
share_issuance_or_repurchase
dividends_paid
```

#### Piyasa bağlamı

```text
market_cap
enterprise_value               Varsa; yoksa türetilir
shares_outstanding
current_price
```

### 3.4 Veri dönemi ve izlenebilirlik

Her ham veya türetilmiş veri için şu metadata saklanmalıdır:

```text
period_type            annual / quarterly / ttm / mrq
period_end             Finansal dönemin bitiş tarihi
as_of_at               Piyasa fiyatı ve hesap anı
source_name            Kaynak adı
source_endpoint        Kaynağın endpoint veya veri yolu
currency
formula_version        Hesaplama sürümü
status                 valid / missing / invalid / insufficient_data / structural_na
```

Bu ayrım kritik önemdedir: gelir tablosu ve nakit akışı TTM iken bilanço MRQ olabilir. `as_of_at`, fiyat değiştikçe F/K gibi piyasa-duyarlı metriklerin hangi anda hesaplandığını kaydeder.

## 4. Veri kalitesi ve güvenlik kuralları

### 4.1 Geçerli finansal snapshot

Bir finansal snapshot en az aşağıdakileri sağlamalıdır:

- kaynak, para birimi ve `period_end` mevcut olmalı;
- en az iki anlamlı ana finansal kalem bulunmalı;
- sayısal alanlar geçerli olmalı;
- şirket ve para birimi bağlamı birbiriyle tutarlı olmalı.

Geçersiz, boş, timeout veya rate-limit sonucu gelen veri eski geçerli finansal snapshot’ı ezemez.

```text
Yeni veri geçerli → kaydet, metrikleri hesapla
Yeni veri geçersiz → eski doğrulanmış veriyi koru
İlk veri çekimi başarısız → sahte finansal kayıt yazma
```

### 4.2 Eksik veri

Eksik veri iyi puan değildir. Bir oran hesaplanamıyorsa:

```text
missing              kaynak alanı yok
invalid              matematiksel olarak anlamsız / bozuk değer
insufficient_data    trend veya model için yeterli dönem yok
structural_na        ilgili varlık sınıfına uygulanamaz
```

Skor motoru bu durumu güven seviyesinde hesaba katar.

### 4.3 Para birimi ve enflasyon

Bir oran için pay ve payda aynı para biriminde olmalıdır. Farklı para birimlerinin doğrudan bölünmesi yasaktır.

BIST şirketlerinde TMS-29 enflasyon muhasebesi sebebiyle dönemlerarası trend yorumu ayrıca işaretlenmelidir. Nominal TRY büyümesi, reel büyüme anlamına gelmeyebilir. Bu nedenle BIST trend metrikleri için seçilecek yöntem açıkça tanımlanmalıdır:

- USD’ye çevrilmiş seri; veya
- enflasyondan arındırılmış TRY seri.

Bu karar alınana kadar, uzun dönem BIST trendleri `comparability_limited` bayrağı taşımalıdır.

## 5. Teknik hesaplama motoru

Teknik metrikler, günlük OHLCV serisinden hesaplanır.

### 5.1 Basit hareketli ortalamalar

```text
SMA(n) = son n kapanış fiyatının aritmetik ortalaması
```

Kullanım:

```text
price_vs_sma50  = (close / SMA50) - 1
price_vs_sma200 = (close / SMA200) - 1
trend_regime    = SMA50 > SMA200 ise pozitif; tersi ise negatif eğilim
```

### 5.2 RSI(14)

Standart 14 dönemlik Relative Strength Index:

```text
RS = ortalama yükseliş / ortalama düşüş
RSI = 100 - 100 / (1 + RS)
```

Yorum bandı örneği:

```text
RSI < 30      aşırı satım / zayıflık bağlamı
30–70         nötr bölge
RSI > 70      aşırı alım / güçlü momentum bağlamı
```

RSI tek başına al/sat kuralı değildir; trend ve volatilite ile birlikte değerlendirilir.

### 5.3 Momentum ve getiri

```text
return_n = (close_t / close_(t-n)) - 1
```

Örnek dönemler: 1 ay, 3 ay, 6 ay, 12 ay. Hesap için ilgili kadar geçmiş kapanış verisi gerekir.

### 5.4 Volatilite

Günlük getirilerin standart sapması yıllıklaştırılır:

```text
daily_return_t = (close_t / close_(t-1)) - 1
annualized_volatility = std(daily_return) × sqrt(252)
```

Kripto gibi 7/24 piyasalar için yıllıklaştırma katsayısı ayrıca belirlenmelidir.

### 5.5 Teknik veri ihtiyacı

| Hesap | Minimum geçmiş veri |
|---|---:|
| Günlük değişim | 2 bar |
| RSI(14) | 15–28 bar |
| SMA50 | 50 bar |
| SMA200 | 200 bar |
| 12 aylık momentum | Yaklaşık 252 işlem günü |
| Yıllık volatilite | Tercihen 252 günlük getiri |

## 6. Temel analiz ve oran hesapları

### 6.1 Değerleme

| Metrik | Formül | Gerekli veri |
|---|---|---|
| F/K | `market_cap / net_income` veya `price / EPS` | piyasa değeri, net kâr veya EPS |
| PD/DD | `market_cap / equity` veya `price / book_value_per_share` | piyasa değeri, özsermaye |
| FD/FAVÖK | `enterprise_value / EBITDA` | EV, EBITDA |
| FCF verimi | `free_cash_flow / market_cap` | OCF, capex, piyasa değeri |
| Kazanç verimi | `net_income / market_cap` | net kâr, piyasa değeri |

```text
enterprise_value = market_cap + total_debt - cash_and_short_term_investments
free_cash_flow = operating_cash_flow - capital_expenditure
```

Negatif kâr veya negatif EBITDA’da F/K ve FD/FAVÖK doğrudan “ucuz” yorumlanmaz; `invalid_for_valuation` veya ayrı bir risk bağlamı kullanılır.

### 6.2 Kârlılık ve kalite

| Metrik | Formül |
|---|---|
| ROE | `net_income / average_equity` |
| ROA | `net_income / average_total_assets` |
| Faaliyet marjı | `EBIT / revenue` |
| Net kâr marjı | `net_income / revenue` |
| Brüt marj | `gross_profit / revenue` |
| ROIC | `NOPAT / invested_capital` |

```text
NOPAT = EBIT × (1 - effective_tax_rate)
invested_capital ≈ total_debt + total_equity - cash
```

Ortalama bilanço kalemleri için ideal yöntem cari ve önceki yıl değerinin ortalamasını kullanmaktır.

### 6.3 Büyüme

| Metrik | Formül |
|---|---|
| Gelir büyümesi | `(revenue_t / revenue_(t-1)) - 1` |
| Net kâr büyümesi | `(net_income_t / net_income_(t-1)) - 1` |
| EPS büyümesi | `(eps_t / eps_(t-1)) - 1` |
| FCF büyümesi | `(fcf_t / fcf_(t-1)) - 1` |
| 3/5 yıllık CAGR | `(value_t / value_(t-n))^(1/n) - 1` |

Negatiften pozitife veya sıfıra yakın değerlerde büyüme yüzdesi yanıltıcı olabilir; sistem bu örnekleri `base_effect_warning` ile işaretlemelidir.

### 6.4 Likidite

| Metrik | Formül |
|---|---|
| Cari oran | `total_current_assets / total_current_liabilities` |
| Asit-test oranı | `(cash + short_term_investments + receivables) / current_liabilities` |
| Net işletme sermayesi | `current_assets - current_liabilities` |

Bankalar ve sigortalar için cari oran, nakit dönüşüm döngüsü ve faiz karşılama metrikleri çoğu zaman yapısal olarak uygun değildir.

### 6.5 Borçluluk ve finansal risk

Ana skorlanan kaldıraç ölçümü:

```text
net_debt = total_debt - cash_and_short_term_investments
net_debt_to_equity = net_debt / total_stockholders_equity
```

Puan bandı:

| Puan | Net borç / özsermaye |
|---:|---|
| 5 | `x ≤ 0.25` |
| 4 | `0.25 ≤ x < 0.50` |
| 3 | `0.50 ≤ x < 1.00` |
| 2 | `1.00 ≤ x < 2.00` |
| 1 | `x ≥ 2.00` veya özsermaye `≤ 0` |

Brüt borç koruması:

```text
if total_debt / total_stockholders_equity > 4.0:
    net_debt_to_equity_score = min(net_debt_to_equity_score, 2)
```

`liabilities_to_equity` skorlanan metrik değildir. Ticari borçlar, ertelenmiş gelirler ve operasyonel yükümlülükler şirketin gerçek finansal kaldıracını doğru temsil etmeyebilir. Ancak sanayi/ticaret şirketlerinde `liabilities_to_equity > 5.0` ise `HIGH_TOTAL_LIABILITIES` teşhis bayrağı oluşturulur.

IFRS 16 kira borçları, sabit ödeme ve temerrüt riski taşıdığı için `total_debt` kapsamına dahil edilmelidir. Veri sağlayıcının bu kalemi içerip içermediği kaynak sözleşmesinde doğrulanmalıdır.

### 6.6 Faiz karşılama

```text
interest_coverage = EBIT / abs(interest_expense)
```

Faiz gideri sıfır, negatif veya eksikse oran güvenilir kabul edilmez. Banka/sigorta gibi finansal şirketlerde bu oran dışlanmalıdır.

### 6.7 Nakit dönüşüm döngüsü

```text
DSO = average_accounts_receivable / revenue × 365
DIO = average_inventory / cost_of_revenue × 365
DPO = average_accounts_payable / cost_of_revenue × 365
CCC = DSO + DIO - DPO
```

Bu metrik ticari şirketler için anlamlıdır. Banka, sigorta, ETF, kripto ve makro varlıklarda `structural_na` olmalıdır.

## 7. Finansal dayanıklılık modelleri

### 7.1 Altman Z-Score

Klasik halka açık üretim şirketi formu:

```text
Z = 1.2A + 1.4B + 3.3C + 0.6D + 1.0E

A = working_capital / total_assets
B = retained_earnings / total_assets
C = EBIT / total_assets
D = market_cap / total_liabilities
E = revenue / total_assets
```

Gerekli veriler: cari varlıklar, cari yükümlülükler, toplam varlıklar, geçmiş yıl kârları, EBIT, piyasa değeri, toplam yükümlülükler ve gelir.

Altman Z her sektör için evrensel bir iflas tahmini değildir. Banka, sigorta ve finansal olmayan tüzel kişiliği olmayan varlıklarda hesaplanmaz veya uygun model sürümü açıkça yazılır.

### 7.2 Piotroski F-Score

Piotroski F dokuz ölçütten oluşur; her kriter 0/1 puandır:

```text
Kârlılık
1. Pozitif ROA
2. Pozitif faaliyet nakit akışı
3. ROA artışı
4. Faaliyet nakit akışının net kârdan güçlü olması

Kaldıraç / likidite
5. Uzun vadeli kaldıraç azalması
6. Cari oranın iyileşmesi
7. Yeni hisse ihracı olmaması

Operasyonel verimlilik
8. Brüt marj iyileşmesi
9. Aktif devir hızının iyileşmesi
```

Gerekli veri, en az iki ardışık yıllık finansal dönemdir. Veri eksikse puan sıfıra zorlanmaz; kullanılabilir kriter sayısı ve `insufficient_data` durumu döndürülür.

## 8. Skor motoru

### 8.1 Kategori yapısı

Hisse senetleri için model beş ana kategori kullanır:

```text
Değerleme
Kalite / kârlılık
Finansal dayanıklılık
Büyüme
Teknik görünüm
```

Her alt metrik tanımlı bantlara göre 1–5 puan alır. Kategori puanı, yalnız geçerli alt metriklerin ağırlıklı ortalamasıdır. Ardından kategori ağırlıklarıyla `composite_score` üretilir.

```text
category_score = Σ(metric_score × metric_weight) / Σ(valid_metric_weight)
composite_score = Σ(category_score × category_weight) / Σ(effective_category_weight)
```

`effective_category_weight`, yapısal olarak uygulanmayan kategoriler çıkarıldıktan sonraki ağırlıktır. Böylece ETF veya kripto, şirket finansalı yok diye otomatik düşük skor almaz.

### 8.2 Varlık sınıfına göre şablon

| Şablon | Kullanılan kategori yaklaşımı |
|---|---|
| Sanayi / ticaret hissesi | Değerleme, kalite, borçluluk, büyüme, teknik |
| Banka / sigorta | PD/DD, ROE ve finansal kuruma uygun kalite oranları; sanayi oranları dışlanır |
| ETF | Teknik, momentum, volatilite, fiyat davranışı |
| Kripto | Teknik, momentum, volatilite, piyasa hareketi |
| Döviz / emtia / endeks | Teknik, momentum, volatilite |

### 8.3 Güven seviyesi

Güven seviyesi, skora kaç geçerli metrikin katkıda bulunduğunu yansıtır:

```text
coverage = kullanılan geçerli ağırlık / teorik uygulanabilir ağırlık
```

Örnek yorum:

```text
HIGH     kritik metriklerin büyük bölümü geçerli
MEDIUM   anlamlı ama eksik veri var
LOW      karar için yetersiz kapsama
```

### 8.4 Sinyal

Sinyal, bileşik skor ile güven seviyesinin birlikte yorumlanmasıdır:

```text
STRONG_BUY / BUY
HOLD / WATCH
SELL / STRONG_SELL
```

Eşikler uygulama sürümünde sabit ve test edilebilir olmalıdır. Yeni referans metrikleri — örneğin Altman Z veya Piotroski F — ana skor ağırlıklarına açık bir sürüm değişikliği olmadan dahil edilmez.

### 8.5 Skor kararlılığı

Fiyat her gün değiştiği için F/K, PD/DD ve FCF verimi sınır bandında zıplayabilir. Kullanıcıya her küçük dalgalanmayı not değişimi olarak göstermemek için histerezis uygulanabilir:

```text
Yeni notun kalıcı olması için skor yeni banda en az 1.5 puan girmelidir.
```

## 9. Tarama döngüsü

Bir tam tarama aşağıdaki mantıkla çalışır:

```text
1. Aktif varlık evrenini oku
2. OHLCV ve güncel fiyat verisini al
3. Şirketler için finansalları al
4. Veriyi standart kanonik modele dönüştür
5. Geçerlilik kontrolünü uygula
6. Teknik ve temel metrikleri hesapla
7. Skor, sinyal ve güven seviyesini üret
8. Varlık sonucunu kalıcı yaz
9. Tüm varlıklar bitince sektör benchmarkları ve liderlik listelerini üret
```

Varlık bazındaki doğru işlem sırası:

```text
provider verisi alındı
→ teknik metrikler hesaplandı
→ uygunsa finansallar standardize edildi
→ geçerlilik kapısı geçti
→ türetilmiş metrikler ve dayanıklılık skorları hesaplandı
→ skor/sinyal hesaplandı
→ varlık sonucu kaydedildi
→ varlık tamamlandı sayıldı
```

Bir varlık hata verirse, diğer varlıkların taraması devam eder. Hata sınıflandırılır; eski geçerli finansal snapshot korunur.

## 10. Sayfalar ve kullanıcı özellikleri

### 10.1 Terminal özeti / Dashboard

Amaç: tüm evrenin hızlı görünümü.

- aktif tarama durumu;
- toplam varlık, tamamlanan ve hata sayısı;
- en güçlü potansiyel listesi;
- en riskli / aşırı değerli listesi;
- varlık sınıfına göre filtre;
- son güncelleme zamanı ve veri tazeliği.

Liderlik listeleri, tarama boyunca ara sonuç gösterebilir; nihai sıralama global hesap tamamlandığında üretilir.

### 10.2 Varlık evreni

Amaç: tüm izleme listesini filtrelenebilir ve sıralanabilir biçimde göstermek.

- varlık sınıfı, borsa, sektör ve sinyal filtreleri;
- fiyat, günlük değişim, skor, sinyal ve güven seviyesi;
- sıralama: skor, momentum, değerleme, risk;
- veri tazeliği ve son işlem zamanı;
- bir satırdan Asset Detail açılışı.

### 10.3 Asset Detail

Amaç: tek varlığın puanının nedenini açıklamak.

Gösterilecek bölümler:

```text
Kimlik ve güncel fiyat
Teknik görünüm ve grafik
Composite score, sinyal, güven seviyesi
Kategori puanları ve alt metrik açıklamaları
Temel finansallar ve dönem bilgisi
Değerleme, kalite, büyüme ve borçluluk oranları
Altman Z ve Piotroski F
Veri kaynağı, formül sürümü, as_of_at ve last_updated_at
Eksik veri / karşılaştırılabilirlik / risk bayrakları
```

Asset Detail, ham kaynağı gizlemez; kullanıcı hangi dönemin, hangi kaynakla ve hangi formülle kullanıldığını görebilmelidir.

### 10.4 Model portföyü

Amaç: seçilmiş sinyalleri ve portföy bağlamını izlemek.

- seçilen varlıklar;
- giriş anı / mevcut değer;
- skor ve sinyal değişimi;
- ağırlık, risk ve performans;
- portföy düzeyi çeşitlendirme görünümü.

Bu sayfa, geçmiş performansı backtest edilmiş strateji gibi sunmamalıdır; gerçek araştırma/backtest katmanı ayrı üründür.

### 10.5 Ayarlar ve sistem yönetimi

Amaç: veri güncelleme sürecini dürüstçe görünür kılmak.

- tam taramayı başlatma;
- gerçek zamanlı aşama, başarı ve hata sayısı;
- son doğrulanmış ilerleme zamanı;
- ekranı yalnız veritabanından yeniden yükleme;
- kaynakların yapılandırılmış olup olmadığını değerlerini açıklamadan gösterme.

Tarama başladıktan sonra `0/Y işlendi` uzun süre gösterilmez. Hazırlık aşaması ayrı ifade edilir; tamamlanan sayı yalnız ilgili varlık başarıyla işlenip kalıcı kaydedildiğinde artar.

## 11. Veri sağlayıcı sorumlulukları

Veri sağlayıcılar değişebilir; uygulama sağlayıcıya değil kanonik veri sözleşmesine bağımlı olmalıdır.

| Veri türü | Birincil gereksinim |
|---|---|
| Güncel fiyat / günlük OHLCV | güvenilir, sembol-borsa eşleşmesi doğru seri |
| Teknik analiz | en az 200 günlük kapanış; tercihen hacim |
| ABD / ETF şirket-fon bağlamı | fiyat, piyasa değeri, mümkünse finansallar |
| BIST finansalları | dönem, para birimi, TMS-29 bağlamı |
| Kripto | fiyat, hacim, yeterli OHLCV |
| Makro seri | seri kimliği, yayın/revizyon tarihi |

FRED/ALFRED gibi makro kaynaklarda ayrıca `vintage_date`, `realtime_start` ve `realtime_end` saklanmalıdır. Böylece bir backtestte o tarihte gerçekten bilinen veri kullanılabilir.

## 12. Backtest ve araştırma için gerekli ek katman

Operasyonel tarama ile araştırma/backtest ayrı tutulmalıdır.

Gerçekçi bir backtest için gerekir:

```text
Point-in-time fiyat ve finansal veri
Restatement / vintage bilgisi
Delist edilmiş şirketler dahil evren
Kurumsal aksiyon düzeltmeleri
İşlem maliyeti, spread ve likidite varsayımları
Rebalance kuralları
Out-of-sample ve walk-forward doğrulama
```

Bu veriler olmadan geçmiş skor performansı, yeniden düzenlenmiş finansallar ve hayatta kalma yanlılığı nedeniyle iyimser görünebilir.

## 13. Değişmez ilkeler

1. Ham veri ile türetilmiş metrik ayrıdır.
2. Her hesap dönemi, kaynak ve formül sürümüyle izlenebilir olmalıdır.
3. Eksik veri iyi skor üretmez.
4. Yeni boş/hatalı veri, son geçerli finansal snapshot’ı ezmez.
5. ETF, kripto ve makro varlıklar şirket finansalıyla skorlanmaz.
6. Banka/sigorta, sanayi şirketi oranlarıyla değerlendirilmez.
7. Referans risk modelleri ana skorla karıştırılmaz.
8. Skor formülü değişirse sürümlenir ve parite testi yapılır.
9. Kullanıcıya sahte ilerleme, sahte tamamlanma veya sahte veri tazeliği gösterilmez.
10. Araştırma/backtest sonucu ile canlı tarama sonucu aynı şey değildir.
