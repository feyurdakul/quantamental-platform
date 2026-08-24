# 🏛️ BÜTÜNLEŞİK FİNANSAL VERİ BORU HATTI MASTER REHBERİ (7 Sağlayıcı)
### Hangi Veri Nereden ve Nasıl Çekilir? (TradingView, Google Finance, FRED, yfinance, FMP, isyatirimhisse, Finnhub)

Bu doküman; **sistem_mimari.md** spesifikasyonunun tüm gereksinimlerini (%100 kapsama + Analist Hedef Fiyatları + BIST TMS-29 / USD Bilanço + EPS Sürprizleri) karşılamak üzere 7 veri sağlayıcısının (`@mathieuc/tradingview`, `Google-Finance-Api`, `fredapi`, `yfinance`, `FMP`, `isyatirimhisse`, `Finnhub`) entegrasyon mimarisini, veri sorumluluk matrisini ve kod örneklerini içerir.

---

## 1. 🎯 BÜTÜNLEŞİK VERİ SORUMLULUK MATRİSİ (Hangi Veri Nereden?)

| Veri Kategorisi | Spesifik Veri Kalemi | Birincil Kaynak | Yedek / Tamamlayıcı | Neden Bu Kaynak? |
| :--- | :--- | :--- | :--- | :--- |
| **BIST Resmi UFRS/KAP Bilanço**| Tam Bilanço, Gelir, Nakit Akış Kalemleri (TRY & USD) | `isyatirimhisse` (`fetch_financials`) | `yfinance` (`.IS`) | **KAP & İş Yatırım resmi UFRS verisi + USD bazlı bilanço desteği (TMS-29 çözümü)** |
| **BIST Banka/Sanayi Ayrımı** | Finansal Kurum (`UFRS_K`) vs Sanayi (`UFRS`) Tabloları | `isyatirimhisse` (`financial_group='3'`) | — | `sistem_mimari.md` Bölüm 8.2 banka/sanayi şablon ayrımına %100 uyum |
| **ABD Bilanço & Gelir** | 3 Standart Tablo + 100+ Oran | `FMP` (Financial Modeling Prep) | `yfinance` / `Finnhub` | Standartlaştırılmış GAAP/IFRS kalemleri ve hazır EV |
| **Analist Hedef Fiyat & Trend**| Wall Street Hedef Fiyat (`targetPrice`), Tavsiye Dağılımı | `Finnhub` (`recommendation_trends`) | `Google-Finance-Api` | **En yüksek, en düşük, medyan hedef fiyat + Analist Buy/Hold/Sell dağılımı** |
| **Kazanç Sürprizleri (Surprise)**| Açıklanan vs Beklenen EPS (Son 4 Çeyrek) | `Finnhub` (`company_earnings`) | `Google-Finance-Api` | **Kâr beklentisini aşan / altında kalan şirketlerin tespiti** |
| **Düzeltilmiş Fiyat (Adj Close)**| Bölünme / Temettü düzeltilmiş OHLCV | `yfinance` (`Adj Close`) | `isyatirimhisse` | BIST ve ABD kurumsal aksiyon düzeltmeleri |
| **Canlı Mumlar (OHLCV)** | Gerçek zamanlı Open, High, Low, Close, Volume | `@mathieuc/tradingview` | `isyatirimhisse` / `Finnhub` | Milisaniyelik canlı mumlar, MTF (1m-1D) esnekliği |
| **Pine Script & TA Konsensüs** | RSI, SuperTrend + Özel/Invite-only Pine Script | `@mathieuc/tradingview` | Yerel Python Motoru | TradingView sunucu motorunda indikatör hesaplatma |
| **Şirket Künyesi & Canlı SSE** | CEO, Sektör, 15sn SSE Canlı Fiyat, Haberler | `Google-Finance-Api` | `Finnhub` (`company_profile2`) | Hızlı, sıfır maliyetli ve API anahtarsız profil |
| **Makro & Para Politikası** | Fed Faizleri (`FEDFUNDS`), M2, Fed Bilançosu (`WALCL`)| `fredapi` | `Finnhub` (Ekonomik Takvim) | St. Louis Fed resmi altın standart 800.000+ seri |
| **Tahvil & Getiri Eğrisi** | ABD 10Y/2Y Faizleri (`DGS10`), Spread (`T10Y2Y`), HY | `fredapi` | — | Resesyon ve makro rejim analizi |
| **Tarihsel Revizyon (Vintage)**| GSYİH / İstihdam ilk açıklanan vs revize seriler | `fredapi` (ALFRED) | — | Backtest'te "Geleceği Görme Hatasını (Look-ahead)" önleme |
| **Dayanıklılık Modelleri** | Altman Z-Score & Piotroski F-Score | Yerel Motor (`engine/resilience.py`) | `FMP` | 5/5 Altman bileşeni ve 9/9 Piotroski kriteri tam veriyle |

---

## 2. 🌟 `Finnhub`'IN SİSTEME KATTIĞI YENİ GÜÇLER

`Finnhub` ücretsiz planı (60 istek/dakika) ile sisteme kurumsal düzeyde **Analist & Tahmin (Estimates)** katmanı ekler:

1. **Wall Street Hedef Fiyatları (`Price Target`):**
   * Analistlerin hisse için belirlediği ortalama, medyan, en yüksek ve en düşük hedef fiyatlar ve mevcut fiyata göre getiri potansiyeli.
2. **Tavsiye Trendleri (`Recommendation Trends`):**
   * Kaç analist "Strong Buy", "Buy", "Hold", "Sell", "Strong Sell" vermiş zaman içindeki değişimi.
3. **EPS Kâr Sürprizleri (`Earnings Surprises`):**
   * Şirketin son 4 çeyrekteki kâr açıklamasında beklentiyi ne kadar aştığı (Beat %) veya altında kaldığı (Miss %).
4. **Resmi SEC Filings:**
   * ABD hisseleri için 10-K yıllık ve 10-Q çeyreklik resmi SEC raporlarının doğrudan PDF/HTML linkleri.

---

## 3. 🛠️ `Finnhub` KOD ÖRNEKLERİ

```python
import finnhub

# Finnhub istemcisi başlatma (Ücretsiz API Key: 60 call/min)
finnhub_client = finnhub.Client(api_key="YOUR_FINNHUB_API_KEY")

symbol = "AAPL"

# 1. Analist Hedef Fiyatları (High, Low, Mean, Median)
price_target = finnhub_client.price_target(symbol)
# Çıktı: {'current': 311.38, 'targetHigh': 350.0, 'targetLow': 240.0, 'targetMean': 315.5, 'targetMedian': 320.0}

# 2. Analist Tavsiye Dağılımı (Strong Buy, Buy, Hold, Sell, Strong Sell)
recommendations = finnhub_client.recommendation_trends(symbol)
# Çıktı: [{'strongBuy': 18, 'buy': 22, 'hold': 10, 'sell': 2, 'strongSell': 0, 'period': '2026-08-01'}]

# 3. EPS Bilanço Kâr Sürprizleri (Son 4 Çeyrek)
earnings_surprises = finnhub_client.company_earnings(symbol, limit=4)
# Çıktı: [{'actual': 1.64, 'estimate': 1.60, 'surprise': 0.04, 'surprisePercent': 2.5, 'period': '2026-06-30'}]

# 4. Şirket Profili (v2)
profile = finnhub_client.company_profile2(symbol=symbol)
# Çıktı: {'country': 'US', 'currency': 'USD', 'exchange': 'NASDAQ', 'marketCapitalization': 4750000, 'shareOutstanding': 15200}
```

---

## 4. 🔄 ÇAPRAZ SEMBOL TABLOSU (7 Sağlayıcı)

| Varlık | Kanonik Sembol | `Finnhub` | `isyatirimhisse` | `yfinance` | `FMP` | `Google-Finance` | `TradingView` | `fredapi` |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **THY (BIST)** | `BIST:THYAO` | N/A | `THYAO` | `THYAO.IS` | `THYAO.IS` | `THYAO:IST` | `BIST:THYAO` | N/A |
| **Garanti BBVA** | `BIST:GARAN` | N/A | `GARAN` | `GARAN.IS` | `GARAN.IS` | `GARAN:IST` | `BIST:GARAN` | N/A |
| **Apple** | `NASDAQ:AAPL` | `AAPL` | N/A | `AAPL` | `AAPL` | `AAPL:NASDAQ` | `NASDAQ:AAPL` | N/A |
| **Tesla** | `NYSE:TSLA` | `TSLA` | N/A | `TSLA` | `TSLA` | `TSLA:NYSE` | `NYSE:TSLA` | N/A |
| **SPDR S&P 500 ETF**| `AMEX:SPY` | `SPY` | N/A | `SPY` | `SPY` | `SPY:NYSEARCA` | `AMEX:SPY` | `SP500` |
| **Bitcoin** | `BINANCE:BTCUSDT`| `BINANCE:BTCUSDT`| N/A | `BTC-USD` | `BTCUSD` | `BTC-USD` | `BINANCE:BTCUSDT` | `CBBTCUSD` |
| **Dolar / TL** | `FX:USDTRY` | `OANDA:USD_TRY` | N/A | `TRY=X` | `USDTRY` | `USD-TRY` | `FX:USDTRY` | `DEXKOUS` |

---

## 5. 🏆 NİHAİ 7 SAĞLAYICILI MİMARİ HARİTASI

```text
1. BIST Finansalları & TMS-29 USD: isyatirimhisse (Resmi KAP/İş Yatırım UFRS + USD Bilanço)
2. BIST/US Düzeltilmiş Fiyat:       yfinance (Adj Close, Splits, Dividends)
3. ABD Standart Finansalları & EV: FMP (Standardized GAAP Statements, Enterprise Value)
4. Analist Hedef Fiyat & Sürpriz:  Finnhub (Price Targets, Recommendation Trends, EPS Surprise)
5. Şirket Künyesi & Canlı SSE:      Google-Finance-Api (CEO, Sektör, 15sn SSE Akışı)
6. Canlı Mumlar & Pine Script:      @mathieuc/tradingview (Canlı WebSocket, TV Konsensüs)
7. Makro & Likidite:               fredapi (Fed Faizleri, M2, ALFRED Point-in-Time)
```
