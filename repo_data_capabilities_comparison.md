# Finansal Veri Sağlayıcı & API Repo Analizleri

Bu doküman, incelenen kütüphane ve repoların borsa, parite/sembol, zaman dilimi (TF), veri çeşitleri ve altyapı yeteneklerini detaylı karşılaştırmak için tutulmaktadır.

---

## 1. REPO 1: `@mathieuc/tradingview` (Mathieu2301/TradingView-API)

- **Tip:** Node.js Kütüphanesi (TradingView Tersine Mühendislik / WebSocket & REST Client)
- **Paket / Kaynak:** `npm i @mathieuc/tradingview` / `github:Mathieu2301/TradingView-API`

### 1.1. 🏛️ Desteklenen Borsa ve Piyasalar
TradingView üzerinde listeli **tüm küresel piyasalar**:
- **BIST (Borsa İstanbul):** Hisse senetleri (`BIST:THYAO`, `BIST:GARAN` vb.), Endeksler (`BIST:XU100`, `BIST:XU030` vb.).
- **ABD Borsaları:** NASDAQ, NYSE, AMEX, OTC (`NASDAQ:AAPL`, `NYSE:TSLA` vb.).
- **Küresel Borsalar:** LSE (Londra), XETRA (Almanya), EURONEXT, HKEX, TSE (Japonya) vb.
- **Kripto Para Borsaları:** Binance, Bybit, Coinbase, OKX, Kraken, KuCoin, Bitget, Gate.io, MEXC, Bitfinex vb. (Hem Spot hem Vadeli/Futures).
- **Forex:** FX_IDC, OANDA, FXCM, FOREX.com, ICE vb. (Tüm majör, minör, egzotik döviz çiftleri: `FX:USDTRY`, `FX:EURUSD`).
- **Emtialar:** Altın (`TVC:GOLD`, `OANDA:XAUUSD`), Gümüş (`XAGUSD`), Ham Petrol (`USOIL`, `UKOIL`), Doğalgaz, Tarım emtiaları.
- **Endeksler & Makro:** S&P 500 (`SPX`), Nasdaq 100 (`NDX`), Dow Jones (`DJI`), Dolar Endeksi (`DXY`), VIX, Tahvil Faizleri (`US10Y`, `TR10Y`).

### 1.2. 🔀 Parite ve Sembol Desteği
- **Format:** Standart TradingView `BORSA:SEMBOL` biçimi.
- **Dinamik Keşif (`searchMarket`):** TradingView arama motorunu kullanarak anahtar kelime veya piyasa filtresine göre anlık sembol arama.

### 1.3. ⏱️ Desteklenen Zaman Dilimleri (Timeframes / TF)
- **Dakikalık:** `1`, `3`, `5`, `15`, `30`, `45` (1m - 45m)
- **Saatlik:** `60` (1h), `120` (2h), `180` (3h), `240` (4h)
- **Günlük / Haftalık / Aylık:** `1D`, `1W`, `1M`, `3M`, `12M` (1Y)
- **Saniyelik (Yetkili Pro/Premium TV oturumu ile):** `1S`, `5S`, `15S`, `30S`
- **Tarih & Bar Aralığı:** Özel mum sayısı (`range: N`) veya tarih filtreleri (`from`, `to`).

### 1.4. 📦 Çekilebilen Veri Çeşitleri
1. **OHLCV & Canlı Fiyat (Market Data):**
   - Açılış, Yüksek, Düşük, Kapanış, Hacim (Open, High, Low, Close, Volume) ve Zaman Damgası (Timestamp).
   - Canlı WebSocket Fiyat Akışı (`Quote`): Anlık son fiyat, alış/satış (bid/ask), günlük net değişim, yüzde değişim, gün içi dip/tepe, anlık hacim.
   - Replay Modu: Geçmişe dönük simüle edilmiş canlı mum akışı.
2. **İndikatör Çıktıları (Pine Script Indicators & Studies):**
   - **Dahili İndikatörler:** RSI, MACD, Bollinger, EMA, SMA, ATR, SuperTrend, Ichimoku, Stochastic vb.
   - **Topluluk İndikatörleri (Public Pine Scripts):** TradingView'deki tüm açık kaynaklı göstergeler.
   - **Özel / Davetiye Usulü İndikatörler (Invite-only & Private):** Hesaba özel yetkilendirilmiş indikatör çıktılarının session cookie ile çekilmesi.
   - Sınırsız sayıda indikatörü eşzamanlı bağlama imkanı.
3. **Teknik Analiz Özeti (`getTA` / `getTechnicalAnalysis`):**
   - TradingView yerleşik sinyal puanları: *Strong Buy, Buy, Neutral, Sell, Strong Sell*.
   - Osilatörler ve Hareketli Ortalamalar grup skorları.
4. **Screener & Filtreleme (`getScreenerTop`):**
   - Hisse, Kripto, Forex screener listeleri, günün en çok artan/azalanları, en aktif hacimlileri (Hotlists).
5. **Takvim & Çizimler:**
   - Ekonomik Takvim verileri (`getCalendar`).
   - Kullanıcının grafik üzerindeki manuel çizimleri (`getDrawings`).

### 1.5. 🔌 İletişim Metodu & Limitler
- **Protokol:** TradingView WebSocket (`wss://data.tradingview.com/socket.io/websocket`) + REST API.
- **Oturum:** Anonim (temel fiyat & açık indikatörler) veya Cookie tabanlı oturum (`sessionid`, `sessionid_sign`).
- **Kapsam Notu:** Fiyat, teknik analiz, indikatörler ve canlı akış için son derece güçlüdür; ancak detaylı bilanço/gelir tablosu gibi temel analiz verileri sağlamaz.

---

## 2. REPO 2: `Google-Finance-Api` (KilimcininKorOglu/Google-Finance-Api)

- **Tip:** Go REST API (Google Finance Dahili `batchexecute` RPC Sarmalayıcısı)
- **Paket / Kaynak:** `github.com/KilimcininKorOglu/Google-Finance-Api` / Demo: `https://finance.hermestech.uk`
- **Özellik:** API anahtarı gerektirmez, sıfır harici bağımlılık (Zero-dependency), yerleşik SSE canlı fiyat akışı.

### 2.1. 🏛️ Desteklenen Borsa ve Piyasalar
Google Finance üzerinde listelenen tüm global enstrümanlar:
- **Hisse Senetleri & ETF'ler:**
  - **BIST (Borsa İstanbul):** `IST` borsa kodu ile tüm Borsa İstanbul hisseleri (`THYAO:IST`, `GARAN:IST`, `ASELS:IST`, `KCHOL:IST` vb.).
  - **ABD Borsaları:** NASDAQ (`GOOGL:NASDAQ`, `AAPL:NASDAQ`), NYSE (`TSLA:NYSE`), NYSEARCA (`SPY:NYSEARCA` vb.).
  - **Global Borsalar:** LSE, XETRA, TYO, HKG, EURONEXT vb.
- **Piyasa Endeksleri:**
  - Dow Jones (`.DJI:INDEXDJX`), S&P 500 (`.INX:INDEXSP`), Nasdaq (`.IXIC:INDEXNASDAQ`), DAX, FTSE, Nikkei vb.
- **Kripto Paralar:**
  - `BTC-USD`, `ETH-USD`, `SOL-USD` vb.
- **Forex / Döviz:**
  - `USD-TRY`, `EUR-TRY`, `EUR-USD`, `GBP-USD` vb.

### 2.2. 🔀 Parite ve Ticker Formatı
- **Hisse & ETF:** `SEMBOL:BORSA` (Örn: `THYAO:IST`, `AAPL:NASDAQ`, `SPY:NYSEARCA`)
- **Endeks:** `.SEMBOL:BORSA` (Örn: `.DJI:INDEXDJX`)
- **Kripto:** `BAZ-KARŞI` (Örn: `BTC-USD`)
- **Döviz:** `BAZ-KARŞI` (Örn: `EUR-USD`, `USD-TRY`)

### 2.3. ⏱️ Desteklenen Zaman Dilimleri / Grafik Aralıkları (Timeframes / Chart Ranges)
Grafik endpoint'i (`/v1/chart/{ticker}?range=...`) için desteklenen aralıklar:
- `1D`: 1 Günlük gün içi seri
- `5D`: 5 Günlük seri
- `1M`: 1 Aylık seri (Varsayılan)
- `6M`: 6 Aylık seri
- `YTD`: Yılbaşından bugüne (Year to Date)
- `1Y`: 1 Yıllık seri
- `5Y`: 5 Yıllık seri
- `MAX`: Tüm zamanlar serisi
*Veri Yapısı:* Her nokta için `date` (ISO/Timestamp), `price` (Fiyat) ve `volume` (Hacim) döner.

### 2.4. 📦 Çekilebilen Veri Çeşitleri

#### A. Fiyat & Kotasyon Verileri (`/v1/quote/{ticker}`)
- Anlık Fiyat (`price`), Net Değişim (`change`), Yüzde Değişim (`changePercent`), Önceki Gün Kapanışı (`previousClose`).
- Para Birimi (`currency`), Zaman Dilimi (`timezone`), Enstrüman Türü (`type`: stock, index, crypto, etf, unknown).
- **Seans Dışı / Piyasa Sonrası Veri (`afterHours`):** `price`, `change`, `changePercent`.

#### B. Şirket Profili & Temel İstatistikler (`/v1/company/{ticker}`)
- Şirket Faaliyet Açıklaması (`description`), CEO Adı (`ceo`), Çalışan Sayısı (`employees`), Sektör (`sector`).
- Piyasa Değeri (`marketCap`), Gün Açılışı (`open`), Gün İçi En Yüksek (`high`), Gün İçi En Düşük (`low`).
- 52 Haftalık Zirve (`fiftyTwoWeekHigh`), 52 Haftalık Dip (`fiftyTwoWeekLow`).
- Fiyat/Kazanç Oranı (`peRatio`), Günlük İşlem Hacmi (`volume`).

#### C. Finansal Tablolar & Temel Bilanço Kalemleri (`/v1/financials/{ticker}?type=quarterly|annual|all`)
- Dönem Sonu Tarihi (`fiscalEnd`), Yıllık/Çeyreklik Bilgisi (`isAnnual`), Para Birimi (`currency`).
- Toplam Gelir / Hasılat (`revenue`).
- Net Dönem Kârı (`netIncome`).
- Hisse Başına Kâr (`eps`) & Seyreltilmiş HBK (`epsDiluted`).
- Faaliyet Kâr Marjı (`operatingMargin`).
- F/K Oranı (`peRatio`).

#### D. Haberler, Analist Kapsamı ve Manşetler
- **Şirket Haberleri (`/v1/news/{ticker}`):** İlgili hisseye özel son haberler (`title`, `source`, `url`, `timestamp`).
- **Analist Kapsamı (`/v1/analyst/{ticker}`):** Google Finance tarafından derlenmiş analiz ve makaleler.
- **Piyasa Manşeti (`/v1/market/headlines`):** Küresel piyasaların en önemli güncel manşet haberi.

#### E. Piyasa Geneli, Taramalar ve Takvim
- **Küresel Endeksler (`/v1/market/indices`):** Dünya endekslerinin anlık durumları.
- **Piyasa Hareketlileri (`/v1/market/movers?category=most-active|gainers|losers&count=10&offset=0`):** En çok kazandıranlar, en çok kaybedenler ve en aktif hacimli hisseler (sayfalama destekli).
- **Trend Hisseler (`/v1/market/trending`):** Google Finance'da öne çıkan/en çok aranan popüler hisseler.
- **Bilanço/Kazanç Takvimi (`/v1/market/earnings`):** Yaklaşan finansal rapor/bilanço açıklama tarihleri (`ticker`, `name`, `date`, `exchange`).

#### F. Çapraz Listelemeler, İlişkili Şirketler & Sınıflandırma
- **Çapraz Listeleme (`/v1/context/{ticker}`):** Aynı hissenin farklı borsalardaki işlem fiyatları ve para birimleri (`CrossListing`).
- **Sektördaş / İlişkili Hisseler (`/v1/related/{ticker}`):** Benzer ve rakip şirketlerin anlık fiyat ve değişimleri.
- **Sınıflandırma Etiketleri (`/v1/classification/{ticker}`):** Varlık sınıfı ve işlem durumu etiketleri ("Most active", "US listed security" vb.).

#### G. Canlı Veri Yayını (SSE) ve Toplu Veri (Full Endpoint)
- **SSE Canlı Akış (`/v1/live`):** 15 saniyede bir Server-Sent Events ile canlı fiyat itme yayını.
- **Canlı Snapshot (`/v1/live/snapshot`):** Takip edilen canlı listedeki son fiyatların JSON snapshot'ı.
- **Birleşik Endpoint (`/v1/full/{ticker}?range=1M`):** Tek HTTP isteğinde Quote + Company + Chart + News verilerinin tümünü getiren paket servis.

### 2.5. 🔌 İletişim Metodu & Limitler
- **Protokol:** Go HTTP REST API (Google Finance dahili `batchexecute` RPC endpoint'ini deserialize eder).
- **Kimlik Doğrulama:** Tamamen API anahtarsız ve ücretsiz.
- **Güçlü Yönü:** BIST ve ABD hisseleri için **hem Fiyat + Grafik hem de Temel Analiz (Bilanço/Gelir/F-K/Marjlar/Piyasa Değeri)** ve **Şirket Bilgilerini** tek elden çok hafif şekilde sunması.

---
