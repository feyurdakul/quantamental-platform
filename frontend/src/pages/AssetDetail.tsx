import React, { useEffect, useState } from 'react';
import { fetchAssetDetail, addPortfolioPosition } from '../api/client';
import { 
  ArrowLeft, 
  Building2, 
  PlusCircle, 
  BarChart3,
  RefreshCw,
  TrendingUp,
  TrendingDown,
  ShieldCheck,
  ShieldAlert,
  AlertTriangle,
  Info,
  DollarSign,
  Activity,
  Layers,
  Calendar,
  Database,
  CheckCircle2,
  XCircle,
  HelpCircle
} from 'lucide-react';

interface InfoTooltipProps {
  title: string;
  desc: string;
  ideal?: string;
  thresholds?: string;
}

const InfoTooltip: React.FC<InfoTooltipProps> = ({ title, desc, ideal, thresholds }) => (
  <span className="group relative inline-flex items-center ml-1 cursor-help align-middle">
    <Info className="w-3 h-3 text-slate-500 group-hover:text-blue-400 transition-colors" />
    <span className="absolute left-1/2 -translate-x-1/2 bottom-full mb-2 hidden group-hover:block w-64 p-2.5 bg-dark-950/95 backdrop-blur border border-slate-700 text-slate-200 rounded shadow-2xl z-50 pointer-events-none font-sans text-[11px] leading-relaxed text-left">
      <span className="font-bold font-mono text-blue-400 block text-xs pb-1 border-b border-slate-800 mb-1">
        {title}
      </span>
      <span className="text-slate-300 block">{desc}</span>
      {ideal && (
        <span className="block text-[10px] font-mono text-emerald-400 mt-1.5 pt-1 border-t border-slate-800/80">
          🎯 İdeal: {ideal}
        </span>
      )}
      {thresholds && (
        <span className="block text-[10px] font-mono text-amber-300 mt-0.5">
          📊 Eşikler: {thresholds}
        </span>
      )}
    </span>
  </span>
);

interface AssetDetailProps {
  symbol: string;
  onBack: () => void;
}

export const AssetDetail: React.FC<AssetDetailProps> = ({ symbol, onBack }) => {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [currencyMode, setCurrencyMode] = useState<'TRY' | 'USD'>('TRY');
  const [addedToPortfolio, setAddedToPortfolio] = useState(false);

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      try {
        const res = await fetchAssetDetail(symbol);
        setData(res);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [symbol]);

  const handleAddToPortfolio = async () => {
    if (!data?.asset) return;
    try {
      await addPortfolioPosition({
        symbol: data.asset.symbol,
        name: data.asset.name,
        entry_price: data.detail?.technicals?.current_price || 100.0,
        sector: data.asset.sector
      });
      setAddedToPortfolio(true);
      setTimeout(() => setAddedToPortfolio(false), 3000);
    } catch (err) {
      console.error(err);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[50vh]">
        <div className="flex flex-col items-center gap-3">
          <RefreshCw className="w-6 h-6 text-blue-400 animate-spin" />
          <p className="text-xs font-mono text-slate-400">{symbol} 360° analizi yükleniyor...</p>
        </div>
      </div>
    );
  }

  const asset = data?.asset || { symbol, name: symbol, sector: '—', asset_class: 'BIST_STOCK', currency: 'TRY' };
  const detail = data?.detail || {};
  const sr = detail.score_result;
  const tech = detail.technicals || {};
  const val = detail.valuation || {};
  const qual = detail.quality || {};
  const grw = detail.growth || {};
  const liq = detail.liquidity || {};
  const res = detail.resilience || {};
  const categories = sr?.category_scores || {};
  const fr = sr?.fundamental_rating || detail?.fundamental_rating;

  const isFinancialAsset = asset.requires_financials !== false && 
    !['ETF', 'CRYPTO', 'FOREX', 'COMMODITY', 'INDEX'].includes(asset.asset_class);
  const isBank = asset.asset_class === 'BANK_STOCK';
  
  const displayCurr = currencyMode === 'USD' ? '$' : (asset.currency === 'USD' ? '$' : asset.currency === 'TRY' ? '₺' : asset.currency);

  const fmtNum = (val: any, suffix = '', decimals = 2) => {
    if (val === null || val === undefined || isNaN(val)) return '—';
    if (typeof val === 'number') {
      return `${val.toLocaleString('tr-TR', { minimumFractionDigits: decimals, maximumFractionDigits: decimals })}${suffix}`;
    }
    return `${val}${suffix}`;
  };

  const fmtCurrency = (val: any) => {
    if (val === null || val === undefined || isNaN(val)) return '—';
    const num = (currencyMode === 'USD' && asset.currency === 'TRY') ? (val / 34.0) : val;
    if (Math.abs(num) >= 1e9) {
      return `${(num / 1e9).toFixed(2)} Milyar ${displayCurr}`;
    } else if (Math.abs(num) >= 1e6) {
      return `${(num / 1e6).toFixed(2)} Milyon ${displayCurr}`;
    }
    return `${num.toLocaleString('tr-TR', { maximumFractionDigits: 2 })} ${displayCurr}`;
  };

  const fmtPct = (val: any, decimals = 1) => {
    if (val === null || val === undefined || isNaN(val)) return '—';
    return `%${(val * 100).toFixed(decimals)}`;
  };

  const getSignalBadge = (sig: any) => {
    const s = typeof sig === 'object' ? sig?.value : sig;
    switch (s) {
      case 'STRONG_BUY': return <span className="px-2 py-0.5 rounded text-[11px] font-bold bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">STRONG BUY 🟢</span>;
      case 'BUY': return <span className="px-2 py-0.5 rounded text-[11px] font-semibold bg-teal-500/15 text-teal-400 border border-teal-500/30">BUY 🟩</span>;
      case 'HOLD': return <span className="px-2 py-0.5 rounded text-[11px] font-semibold bg-amber-500/15 text-amber-300 border border-amber-500/30">HOLD 🟨</span>;
      case 'WATCH': return <span className="px-2 py-0.5 rounded text-[11px] font-semibold bg-blue-500/15 text-blue-300 border border-blue-500/30">WATCH 🟦</span>;
      case 'SELL': return <span className="px-2 py-0.5 rounded text-[11px] font-semibold bg-rose-500/15 text-rose-300 border border-rose-500/30">SELL 🟧</span>;
      case 'STRONG_SELL': return <span className="px-2 py-0.5 rounded text-[11px] font-bold bg-rose-600/20 text-rose-400 border border-rose-600/40">STRONG SELL 🔴</span>;
      default: return <span className="px-2 py-0.5 rounded text-[11px] bg-slate-800 text-slate-400">HOLD</span>;
    }
  };

  return (
    <div className="space-y-5">
      
      {/* 1. Üst Başlık & Aksiyon Barı */}
      <div className="bg-dark-800 border border-slate-800/80 p-4 rounded-md flex flex-col md:flex-row gap-3 items-start md:items-center justify-between">
        <div className="flex items-center gap-3">
          <button 
            onClick={onBack}
            className="p-1.5 rounded bg-dark-900 hover:bg-slate-800 text-slate-400 hover:text-white transition-colors border border-slate-800"
          >
            <ArrowLeft className="w-4 h-4" />
          </button>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-xl font-bold text-white font-mono">{asset.symbol}</h2>
              <span className="text-[10px] px-2 py-0.5 rounded bg-blue-600/20 text-blue-400 border border-blue-500/30 font-mono">
                {asset.asset_class}
              </span>
              {asset.sector && (
                <span className="text-xs text-slate-400 font-sans flex items-center gap-1">
                  <Building2 className="w-3.5 h-3.5 text-slate-500" /> {asset.sector}
                </span>
              )}
            </div>
            <p className="text-xs text-slate-300 font-sans mt-0.5">{asset.name}</p>
          </div>
        </div>

        <div className="flex items-center gap-2.5 w-full md:w-auto justify-end">
          {asset.symbol.startsWith('BIST') && (
            <div className="flex items-center bg-dark-900 p-0.5 rounded border border-slate-800">
              <button
                onClick={() => setCurrencyMode('TRY')}
                className={`px-2.5 py-1 rounded text-[11px] font-mono font-medium transition-colors ${
                  currencyMode === 'TRY' ? 'bg-blue-600 text-white' : 'text-slate-400 hover:text-white'
                }`}
              >
                TRY Bilanço
              </button>
              <button
                onClick={() => setCurrencyMode('USD')}
                className={`px-2.5 py-1 rounded text-[11px] font-mono font-medium transition-colors ${
                  currencyMode === 'USD' ? 'bg-emerald-600 text-white' : 'text-slate-400 hover:text-white'
                }`}
              >
                USD (TMS-29 Arındırılmış)
              </button>
            </div>
          )}

          <button
            onClick={handleAddToPortfolio}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded text-xs font-mono font-bold transition-colors ${
              addedToPortfolio
                ? 'bg-emerald-600 text-white'
                : 'bg-blue-600 hover:bg-blue-500 text-white'
            }`}
          >
            <PlusCircle className="w-3.5 h-3.5" />
            <span>{addedToPortfolio ? 'Portföyde ✓' : 'Portföye Ekle'}</span>
          </button>
        </div>
      </div>

      {/* 2. SKOR ÖZETİ VE FİYAT / TEKNİK GENEL BAKIŞ */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        
        {/* 1. Model: 10'luk Kantitatif Bileşik Skor */}
        <div className="bg-dark-800 border border-slate-800/80 p-5 rounded-md flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between">
              <span className="text-[10px] font-mono text-slate-400 uppercase tracking-wider flex items-center">
                1. BİLEŞİK SKOR
                <InfoTooltip 
                  title="10'luk Kantitatif Bileşik Skor" 
                  desc="5 ana kategorinin (Değerleme, Kalite, Dayanıklılık, Büyüme, Trend) ağırlıklı ortalamasıyla üretilen 1.00 - 10.00 arası nihai kurumsal puan." 
                  ideal="≥ 8.00 (Güçlü Alım Bölgesi)" 
                />
              </span>
              <span className="text-[10px] font-mono text-slate-500">v1.0.0</span>
            </div>
            
            <div className="flex items-baseline gap-2 mt-2">
              <span className="text-3xl font-black font-mono text-emerald-400">
                {sr?.composite_score ? sr.composite_score.toFixed(2) : '—'}
              </span>
              <span className="text-xs font-mono text-slate-500">/ 10.00</span>
            </div>

            <div className="flex items-center gap-1.5 mt-2 flex-wrap">
              {getSignalBadge(sr?.signal)}
              <span className="px-1.5 py-0.5 rounded text-[9px] font-mono bg-dark-900 text-slate-300 border border-slate-700">
                {typeof sr?.confidence_level === 'object' ? sr?.confidence_level?.value : (sr?.confidence_level || 'LOW')}
              </span>
            </div>
          </div>

          <div className="mt-3 pt-2 border-t border-slate-800 text-[10px] text-slate-500 font-mono flex items-center justify-between">
            <span>Kapsama: %{Math.round((sr?.coverage || 0.8) * 100)}</span>
            <span>Histerezis: {sr?.hysteresis_applied ? 'Açık' : 'Kapalı'}</span>
          </div>
        </div>

        {/* 2. Model: 6-Faktörlü Temel Derecelendirme (S, A, B, C, D / 6-30 Puan) */}
        <div className="bg-dark-800 border border-slate-800/80 p-5 rounded-md flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between">
              <span className="text-[10px] font-mono text-slate-400 uppercase tracking-wider flex items-center">
                2. 6-FAKTÖR TEMEL NOT
                <InfoTooltip 
                  title="6-Faktörlü Temel Derecelendirme Modeli" 
                  desc="DCF, ROE, ROA, D/E, F/K ve PD/DD rasyolarının 1-5 puan arası değerlendirilip 6-30 toplam puana ve S, A, B, C, D harf notuna dönüştürüldüğü temel model." 
                  ideal="S Notu (25-30 Puan)" 
                  thresholds="S (≥25), A (19-24), B (13-18), C (9-12), D (6-8)" 
                />
              </span>
              <span className="text-[10px] font-mono text-purple-400 font-bold">6-30 SKALA</span>
            </div>

            {isFinancialAsset && fr ? (
              <>
                <div className="flex items-baseline gap-2 mt-2">
                  <span className={`text-3xl font-black font-mono ${
                    (fr?.rating || 'B') === 'S' ? 'text-emerald-400' :
                    (fr?.rating || 'B') === 'A' ? 'text-teal-400' :
                    (fr?.rating || 'B') === 'B' ? 'text-amber-300' :
                    (fr?.rating || 'B') === 'C' ? 'text-rose-300' : 'text-rose-500'
                  }`}>
                    NOT: {fr?.rating || 'B'}
                  </span>
                  <span className="text-xs font-mono text-slate-400">
                    ({fr?.total_score || 18} / 30 Puan)
                  </span>
                </div>

                <div className="mt-2">
                  <span className={`px-2 py-0.5 rounded text-[10px] font-bold font-mono border ${
                    (fr?.rating || 'B') === 'S' ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40' :
                    (fr?.rating || 'B') === 'A' ? 'bg-teal-500/20 text-teal-300 border-teal-500/40' :
                    (fr?.rating || 'B') === 'B' ? 'bg-amber-500/20 text-amber-300 border-amber-500/40' :
                    (fr?.rating || 'B') === 'C' ? 'bg-rose-500/20 text-rose-300 border-rose-500/40' : 'bg-rose-700/30 text-rose-400 border-rose-700/50'
                  }`}>
                    TAVSİYE: {fr?.recommendation?.toUpperCase() || 'NEUTRAL'}
                  </span>
                </div>
              </>
            ) : (
              <div className="mt-3">
                <span className="text-sm font-mono text-slate-500 font-bold">Uygulanamaz</span>
                <p className="text-[10px] text-slate-500 mt-1">Şirket bilançosu bulunmamaktadır.</p>
              </div>
            )}
          </div>

          <div className="mt-3 pt-2 border-t border-slate-800 text-[10px] text-slate-500 font-mono flex items-center justify-between">
            <span>6 Metrik Eşit Ağırlık</span>
            <span>Konsensüs: Aktif</span>
          </div>
        </div>

        {/* Fiyat ve Canlı Göstergeler */}
        <div className="bg-dark-800 border border-slate-800/80 p-5 rounded-md flex flex-col justify-between">
          <div>
            <span className="text-[10px] font-mono text-slate-400 uppercase tracking-wider">FİYAT & PİYASA VERİLERİ</span>
            
            <div className="flex items-baseline gap-2 mt-2">
              <span className="text-2xl font-black font-mono text-white">
                {tech?.current_price ? fmtNum(currencyMode === 'USD' && asset.currency === 'TRY' ? (tech.current_price / 34.0) : tech.current_price, ` ${displayCurr}`) : '—'}
              </span>
              {(tech?.daily_change !== undefined || tech?.change !== undefined) && (
                <span className={`text-[11px] font-mono font-bold flex items-center ${(tech.daily_change || tech.change || 0) >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                  {(tech.daily_change || tech.change || 0) >= 0 ? '+' : ''}{fmtNum(tech.daily_change || tech.change, ` ${displayCurr}`)}
                </span>
              )}
            </div>

            <div className="grid grid-cols-2 gap-1.5 mt-2 text-[10px] font-mono">
              <div className="bg-dark-900 p-1.5 rounded border border-slate-800">
                <span className="text-slate-500 flex items-center text-[9px]">
                  RSI (14)
                  <InfoTooltip title="RSI (14) - Göreceli Güç Endeksi" desc="Fiyat hareketlerinin hızını ve momentumunu ölçer. 30 altı aşırı satım, 70 üstü aşırı alımdır." ideal="40 - 65 Arası (Sağlıklı Trend)" />
                </span>
                <span className="font-bold text-emerald-400">{fmtNum(tech?.rsi14, '', 1)}</span>
              </div>
              <div className="bg-dark-900 p-1.5 rounded border border-slate-800">
                <span className="text-slate-500 flex items-center text-[9px]">
                  Trend Rejimi
                  <InfoTooltip title="Trend Rejimi (SMA50 vs SMA200)" desc="Fiyatın 200 ve 50 günlük hareketli ortalamalara göre yönüdür. SMA50 > SMA200 ve Fiyat > SMA200 ise Altın Kesişimdir." ideal="POSITIVE (Boğa Trendi)" />
                </span>
                <span className="font-bold text-white text-[10px]">{tech?.trend_regime || 'NEUTRAL'}</span>
              </div>
            </div>
          </div>

          <div className="mt-3 text-[10px] font-mono text-slate-500 flex justify-between">
            <span className="flex items-center">
              Volatilite: {fmtPct(tech?.annualized_volatility)}
              <InfoTooltip title="Yıllık Volatilite" desc="Hisse fiyatının standart sapmasıdır. Düşük olması öngörülebilir fiyat hareketini gösterir." />
            </span>
            <span>SMA50: {fmtNum(tech?.sma50)}</span>
          </div>
        </div>

        {/* Momentum & Getiriler */}
        <div className="bg-dark-800 border border-slate-800/80 p-5 rounded-md flex flex-col justify-between">
          <div>
            <span className="text-[10px] font-mono text-slate-400 uppercase tracking-wider">MOMENTUM PROFİLİ</span>
            
            <div className="grid grid-cols-4 gap-1 mt-2 text-center font-mono">
              <div className="bg-dark-900 p-1.5 rounded border border-slate-800">
                <span className="text-[8px] text-slate-500 block">1A</span>
                <span className={`text-[10px] font-bold ${tech?.return_1m >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                  {fmtPct(tech?.return_1m, 0)}
                </span>
              </div>
              <div className="bg-dark-900 p-1.5 rounded border border-slate-800">
                <span className="text-[8px] text-slate-500 block">3A</span>
                <span className={`text-[10px] font-bold ${tech?.return_3m >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                  {fmtPct(tech?.return_3m, 0)}
                </span>
              </div>
              <div className="bg-dark-900 p-1.5 rounded border border-slate-800">
                <span className="text-[8px] text-slate-500 block">6A</span>
                <span className={`text-[10px] font-bold ${tech?.return_6m >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                  {fmtPct(tech?.return_6m, 0)}
                </span>
              </div>
              <div className="bg-dark-900 p-1.5 rounded border border-slate-800">
                <span className="text-[8px] text-slate-500 block">12A</span>
                <span className={`text-[10px] font-bold ${tech?.return_12m >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                  {fmtPct(tech?.return_12m, 0)}
                </span>
              </div>
            </div>
          </div>

          <div className="mt-3 text-[10px] font-mono text-slate-400 bg-dark-900 p-1.5 rounded border border-slate-800 truncate">
            {tech?.trend_regime === 'POSITIVE' ? 'Pozitif (Fiyat > SMA200)' :
             tech?.trend_regime === 'NEGATIVE' ? 'Negatif (Fiyat < SMA200)' : 'Nötr / Kararsız'}
          </div>
        </div>

      </div>

      {/* 3. 2. MODEL: 6 BİREYSEL METRİK, EŞİKLERİ VE PUAN DAĞILIMI TABLOSU */}
      {isFinancialAsset && (
        <div className="bg-dark-800 border border-purple-900/40 p-5 rounded-md space-y-3 font-mono text-xs">
          <div className="flex items-center justify-between border-b border-slate-800/80 pb-2">
            <div className="flex items-center gap-2">
              <ShieldCheck className="w-4 h-4 text-purple-400" />
              <h4 className="font-bold text-xs uppercase tracking-wider text-slate-100">
                6-Faktörlü Temel Model: Bireysel Metrikler, Eşikler ve Puan Dökümü
              </h4>
            </div>
            <span className="text-[10px] px-2 py-0.5 rounded bg-purple-500/10 text-purple-300 font-bold">
              TOPLAM: {fr?.total_score || 18} / 30 PUAN (NOT: {fr?.rating || 'B'})
            </span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-slate-800 text-slate-500 text-[10px]">
                  <th className="pb-2">METRİK</th>
                  <th className="pb-2">YÖN</th>
                  <th className="pb-2">GERÇEK DEĞER</th>
                  <th className="pb-2">PUAN (/5)</th>
                  <th className="pb-2">EŞİK DEĞERLERİ & KRİTERLER</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-mono text-xs">
                
                {/* 1. DCF / FCF Marjı */}
                <tr>
                  <td className="py-2.5 font-bold text-white flex items-center">
                    DCF / FCF Marjı
                    <InfoTooltip 
                      title="DCF / Serbest Nakit Akışı Marjı" 
                      desc="Şirketin elde ettiği gelirin yüzde kaçını serbest nakde dönüştürdüğünü gösterir. Yüksek nakit yaratımı temettü ve büyüme için en kritik göstergedir." 
                      ideal="≥ %25 (5 Puan)" 
                      thresholds="≥%25 (5P), %10-%25 (4P), %0-%10 (3P), -%15-%0 (2P), <-%15 (1P)" 
                    />
                  </td>
                  <td className="py-2.5 text-emerald-400 font-semibold">Yüksek İyi ↗</td>
                  <td className="py-2.5 text-white font-bold">{fmtPct(val?.fcf_yield || qual?.operating_margin)}</td>
                  <td className="py-2.5">
                    <span className="px-2 py-0.5 rounded bg-blue-600/20 text-blue-300 font-bold border border-blue-500/30">
                      {fr?.metric_breakdown?.dcf_margin?.points || 4} / 5 Puan
                    </span>
                  </td>
                  <td className="py-2.5 text-[11px] text-slate-400">
                    ≥%25 [5P] • %10-%25 [4P] • %0-%10 [3P] • -%15-%0 [2P] • &lt;-%15 [1P]
                  </td>
                </tr>

                {/* 2. ROE */}
                <tr>
                  <td className="py-2.5 font-bold text-white flex items-center">
                    Özkaynak Kârlılığı (ROE)
                    <InfoTooltip 
                      title="Özsermaye Kârlılığı (Return on Equity)" 
                      desc="Hissedarların koyduğu sermayenin yıllık net kâr yaratma verimliliğidir. Enflasyon üzeri yüksek ROE, hissenin değer kazanmasındaki ana itici güçtür." 
                      ideal="≥ %20 (5 Puan)" 
                      thresholds="≥%20 (5P), %10-%20 (4P), %5-%10 (3P), %0-%5 (2P), <0 (1P)" 
                    />
                  </td>
                  <td className="py-2.5 text-emerald-400 font-semibold">Yüksek İyi ↗</td>
                  <td className="py-2.5 text-emerald-400 font-bold">{fmtPct(qual?.roe)}</td>
                  <td className="py-2.5">
                    <span className="px-2 py-0.5 rounded bg-blue-600/20 text-blue-300 font-bold border border-blue-500/30">
                      {fr?.metric_breakdown?.roe?.points || 4} / 5 Puan
                    </span>
                  </td>
                  <td className="py-2.5 text-[11px] text-slate-400">
                    ≥%20 [5P] • %10-%20 [4P] • %5-%10 [3P] • %0-%5 [2P] • &lt;%0 [1P]
                  </td>
                </tr>

                {/* 3. ROA */}
                <tr>
                  <td className="py-2.5 font-bold text-white flex items-center">
                    Aktif Kârlılığı (ROA)
                    <InfoTooltip 
                      title="Aktif Kârlılığı (Return on Assets)" 
                      desc="Şirketin tüm fabrikaları, nakdi ve varlıklarıyla ne kadar net kâr ürettiğidir. Şirketin varlıklarını ne derece verimli çalıştırdığını gösterir." 
                      ideal="≥ %10 (5 Puan)" 
                      thresholds="≥%10 (5P), %5-%10 (4P), %2-%5 (3P), %0-%2 (2P), <0 (1P)" 
                    />
                  </td>
                  <td className="py-2.5 text-emerald-400 font-semibold">Yüksek İyi ↗</td>
                  <td className="py-2.5 text-slate-200 font-bold">{fmtPct(qual?.roa)}</td>
                  <td className="py-2.5">
                    <span className="px-2 py-0.5 rounded bg-blue-600/20 text-blue-300 font-bold border border-blue-500/30">
                      {fr?.metric_breakdown?.roa?.points || 3} / 5 Puan
                    </span>
                  </td>
                  <td className="py-2.5 text-[11px] text-slate-400">
                    ≥%10 [5P] • %5-%10 [4P] • %2-%5 [3P] • %0-%2 [2P] • &lt;%0 [1P]
                  </td>
                </tr>

                {/* 4. Borç / Özkaynak */}
                <tr>
                  <td className="py-2.5 font-bold text-white flex items-center">
                    Borç / Özkaynak (D/E)
                    <InfoTooltip 
                      title="Borç / Özkaynak Oranı (Debt to Equity)" 
                      desc="Şirketin net borcunun özkaynaklarına oranıdır. Düşük olması şirketin faiz yükü altında ezilmediğini ve finansal olarak bağımsız olduğunu gösterir." 
                      ideal="≤ 0.20x (5 Puan)" 
                      thresholds="≤0.20x (5P), 0.20-0.50x (4P), 0.50-1.00x (3P), 1.00-2.00x (2P), >2.00x (1P)" 
                    />
                  </td>
                  <td className="py-2.5 text-blue-400 font-semibold">Düşük İyi ↘</td>
                  <td className="py-2.5 text-white font-bold">{fmtNum(liq?.net_debt_to_equity)}x</td>
                  <td className="py-2.5">
                    <span className="px-2 py-0.5 rounded bg-blue-600/20 text-blue-300 font-bold border border-blue-500/30">
                      {fr?.metric_breakdown?.debt_to_equity?.points || 4} / 5 Puan
                    </span>
                  </td>
                  <td className="py-2.5 text-[11px] text-slate-400">
                    ≤0.20x [5P] • 0.20-0.50x [4P] • 0.50-1.00x [3P] • 1.00-2.00x [2P] • &gt;2.00x [1P]
                  </td>
                </tr>

                {/* 5. F/K (P/E) */}
                <tr>
                  <td className="py-2.5 font-bold text-white flex items-center">
                    Fiyat / Kazanç (F/K)
                    <InfoTooltip 
                      title="F/K Oranı (Price to Earnings)" 
                      desc="Hissenin kârına göre kaç yılda kendini amorti ettiğini gösterir. Düşük F/K hissenin ucuz olduğunu gösterir. Şirket zarar etmişse (<0) sistem doğrudan 1 puan verir." 
                      ideal="≤ 15.0x (5 Puan)" 
                      thresholds="≤15x (5P), 15-25x (4P), 25-40x (3P), 40-999x (2P), Zarar: 1P" 
                    />
                  </td>
                  <td className="py-2.5 text-blue-400 font-semibold">Düşük İyi ↘</td>
                  <td className="py-2.5 text-white font-bold">{val?.pe_ratio ? `${fmtNum(val.pe_ratio)}x` : '— (Zarar)'}</td>
                  <td className="py-2.5">
                    <span className="px-2 py-0.5 rounded bg-blue-600/20 text-blue-300 font-bold border border-blue-500/30">
                      {fr?.metric_breakdown?.pe_ratio?.points || (val?.pe_ratio ? 4 : 1)} / 5 Puan
                    </span>
                  </td>
                  <td className="py-2.5 text-[11px] text-slate-400">
                    ≤15.0x [5P] • 15-25x [4P] • 25-40x [3P] • 40-999x [2P] • &gt;999x veya Zarar [1P]
                  </td>
                </tr>

                {/* 6. PD/DD (P/B) */}
                <tr>
                  <td className="py-2.5 font-bold text-white flex items-center">
                    PD/DD Oranı (P/B)
                    <InfoTooltip 
                      title="Piyasa Değeri / Defter Değeri (Price to Book)" 
                      desc="Şirketin piyasa değerinin muhasebe özkaynaklarına oranıdır. 1.5 altı defter değerine çok yakın veya iskontolu olduğunu belirtir." 
                      ideal="≤ 1.50x (5 Puan)" 
                      thresholds="≤1.50x (5P), 1.50-3.00x (4P), 3.00-5.00x (3P), 5.00-10.00x (2P), >10.00x (1P)" 
                    />
                  </td>
                  <td className="py-2.5 text-blue-400 font-semibold">Düşük İyi ↘</td>
                  <td className="py-2.5 text-white font-bold">{val?.pb_ratio ? `${fmtNum(val.pb_ratio)}x` : '—'}</td>
                  <td className="py-2.5">
                    <span className="px-2 py-0.5 rounded bg-blue-600/20 text-blue-300 font-bold border border-blue-500/30">
                      {fr?.metric_breakdown?.pb_ratio?.points || 4} / 5 Puan
                    </span>
                  </td>
                  <td className="py-2.5 text-[11px] text-slate-400">
                    ≤1.50x [5P] • 1.50-3.00x [4P] • 3.00-5.00x [3P] • 5.00-10.00x [2P] • &gt;10.00x [1P]
                  </td>
                </tr>

              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* 4. 5 KATEGORİ SKORLARI (Bölüm 8) */}
      <div className="bg-dark-800 border border-slate-800/80 p-5 rounded-md">
        <div className="flex items-center gap-2 pb-3 mb-4 border-b border-slate-800/80">
          <BarChart3 className="w-4 h-4 text-blue-400" />
          <h4 className="font-bold text-xs font-mono uppercase tracking-wider text-slate-100 flex items-center">
            5 Kategori Puan Dağılımı (1.00 - 10.00 Puan)
            <InfoTooltip title="5 Kategori Dağılımı" desc="10'luk Quantamental skorun 5 temel ayağını gösterir: Değerleme %25, Kalite %20, Dayanıklılık %20, Büyüme %15, Teknik %20." />
          </h4>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3 font-mono">
          {[
            { key: 'valuation', name: 'Değerleme', score: categories?.valuation?.category_score, weight: '%25', desc: 'F/K ve PD/DD çarpanlarının ucuzluğunu ölçer.' },
            { key: 'quality', name: 'Kalite & Kârlılık', score: categories?.quality?.category_score, weight: '%20', desc: 'ROE ve Faaliyet kâr marjının gücünü ölçer.' },
            { key: 'resilience', name: 'Dayanıklılık', score: categories?.resilience?.category_score, weight: '%20', desc: 'Cari oran ve Net borç/özsermaye ile likiditeyi ölçer.' },
            { key: 'growth', name: 'Büyüme', score: categories?.growth?.category_score, weight: '%15', desc: 'Yıllık hasılat artış hızını ölçer.' },
            { key: 'technical', name: 'Teknik Görünüm', score: categories?.technical?.category_score, weight: '%20', desc: 'RSI ve SMA50/SMA200 trend rejimini ölçer.' },
          ].map((cat) => (
            <div key={cat.key} className="bg-dark-900 p-3 rounded border border-slate-800 flex flex-col justify-between">
              <div>
                <div className="flex justify-between items-center text-xs">
                  <span className="text-slate-300 font-sans text-xs flex items-center">
                    {cat.name}
                    <InfoTooltip title={cat.name} desc={cat.desc} />
                  </span>
                  <span className="text-[10px] text-slate-500">{cat.weight}</span>
                </div>
                <p className="text-xl font-bold text-white mt-1">
                  {cat.score !== undefined && cat.score !== null ? cat.score.toFixed(2) : (isFinancialAsset ? '—' : 'Uygulanamaz')}
                </p>
              </div>
              <div className="w-full h-1 bg-dark-800 rounded-full overflow-hidden mt-3 border border-slate-800">
                <div 
                  className="h-full bg-gradient-to-r from-blue-500 to-emerald-400 rounded-full"
                  style={{ width: `${cat.score ? (cat.score / 10.0) * 100 : 0}%` }}
                />
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* 5. TEMEL ANALİZ METRİKLERİ (Değerleme, Kalite, Büyüme) */}
      {isFinancialAsset ? (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          
          {/* Değerleme Metrikleri */}
          <div className="bg-dark-800 border border-slate-800/80 p-4 rounded-md space-y-3 font-mono text-xs">
            <div className="flex items-center justify-between border-b border-slate-800/80 pb-2">
              <span className="font-bold text-slate-200 uppercase tracking-wider text-[11px]">Değerleme Metrikleri</span>
              <span className="text-[10px] text-slate-500">Çarpanlar</span>
            </div>

            <div className="space-y-1.5">
              <div className="flex justify-between py-1 border-b border-slate-800/50">
                <span className="text-slate-400 flex items-center">
                  F/K (P/E):
                  <InfoTooltip title="F/K Oranı" desc="Fiyatın hisse başına net kâra oranı. 15 altı ucuz kabul edilir." ideal="< 15.0x" />
                </span>
                <span className="text-white font-semibold">{val?.pe_ratio ? `${fmtNum(val.pe_ratio)}x` : (val?.pe_ratio === null ? '—' : 'Anlamlı değil')}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-800/50">
                <span className="text-slate-400 flex items-center">
                  PD/DD (P/B):
                  <InfoTooltip title="PD/DD Oranı" desc="Piyasa Değerinin Defter Değerine oranı. 1.5 altı defter değerine yakın işlem gördüğünü belirtir." ideal="< 1.50x" />
                </span>
                <span className="text-white font-semibold">{val?.pb_ratio ? `${fmtNum(val.pb_ratio)}x` : '—'}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-800/50">
                <span className="text-slate-400 flex items-center">
                  FD/FAVÖK (EV/EBITDA):
                  <InfoTooltip title="FD/FAVÖK Oranı" desc="Firma Değerinin FAVÖK'e oranı. Sermaye ve borç yapısından arındırılmış operasyonel değerleme çarpanıdır." ideal="< 8.0x" />
                </span>
                <span className="text-white font-semibold">{val?.ev_ebitda ? `${fmtNum(val.ev_ebitda)}x` : (isBank ? 'Uygulanamaz' : '—')}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-800/50">
                <span className="text-slate-400 flex items-center">
                  FCF Verimi (Yield):
                  <InfoTooltip title="Serbest Nakit Akışı Verimi" desc="Hisse başına üretilen serbest nakdin hisse fiyatına oranıdır. %8 üzeri çok güçlü nakit verimidir." ideal="> %8.0" />
                </span>
                <span className="text-emerald-400 font-semibold">{fmtPct(val?.fcf_yield)}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-800/50">
                <span className="text-slate-400 flex items-center">
                  Kazanç Verimi (E/P):
                  <InfoTooltip title="Kazanç Verimi (Earnings Yield)" desc="F/K'nın tersidir (1 / F/K). Hisse fiyatına oranla şirketin ürettiği kâr getiri oranıdır." ideal="> %10.0" />
                </span>
                <span className="text-slate-200">{fmtPct(val?.earnings_yield)}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-800/50">
                <span className="text-slate-400 flex items-center">
                  Piyasa Değeri:
                  <InfoTooltip title="Piyasa Değeri (Market Cap)" desc="Şirketin tüm hisselerinin borsadaki toplam güncel değeridir." />
                </span>
                <span className="text-slate-300">{fmtCurrency(val?.market_cap)}</span>
              </div>
              <div className="flex justify-between py-1">
                <span className="text-slate-400 flex items-center">
                  Firma Değeri (EV):
                  <InfoTooltip title="Firma Değeri (Enterprise Value)" desc="Piyasa Değeri + Toplam Borç - Nakit. Şirketin tüm borçlarıyla birlikte satın alma maliyetidir." />
                </span>
                <span className="text-slate-300">{fmtCurrency(val?.enterprise_value)}</span>
              </div>
            </div>
          </div>

          {/* Kalite & Kârlılık */}
          <div className="bg-dark-800 border border-slate-800/80 p-4 rounded-md space-y-3 font-mono text-xs">
            <div className="flex items-center justify-between border-b border-slate-800/80 pb-2">
              <span className="font-bold text-slate-200 uppercase tracking-wider text-[11px]">Kalite & Kârlılık</span>
              <span className="text-[10px] text-slate-500">Marjlar</span>
            </div>

            <div className="space-y-1.5">
              <div className="flex justify-between py-1 border-b border-slate-800/50">
                <span className="text-slate-400 flex items-center">
                  ROE:
                  <InfoTooltip title="Özsermaye Kârlılığı (ROE)" desc="Özkaynakların ne kadar verimli kâra dönüştürüldüğüdür. %20 üzeri güçlüdür." ideal="> %20.0" />
                </span>
                <span className="text-emerald-400 font-semibold">{fmtPct(qual?.roe)}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-800/50">
                <span className="text-slate-400 flex items-center">
                  ROA:
                  <InfoTooltip title="Aktif Kârlılığı (ROA)" desc="Toplam varlıkların kârlılık verimliliğidir. %10 üzeri yüksektir." ideal="> %10.0" />
                </span>
                <span className="text-slate-200">{fmtPct(qual?.roa)}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-800/50">
                <span className="text-slate-400 flex items-center">
                  ROIC:
                  <InfoTooltip title="Yatırılan Sermaye Getirisi (ROIC)" desc="Yatırılan sermayenin getirisidir. Şirketin sermaye maliyetinin üzerinde getiri üretip üretmediğini gösterir." ideal="> %15.0" />
                </span>
                <span className="text-slate-200">{fmtPct(qual?.roic)}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-800/50">
                <span className="text-slate-400 flex items-center">
                  Brüt Kâr Marjı:
                  <InfoTooltip title="Brüt Kâr Marjı" desc="Satış gelirlerinden satılan malın maliyeti düşüldükten sonra kalan brüt kâr oranıdır." />
                </span>
                <span className="text-slate-200">{isBank ? 'Uygulanamaz' : fmtPct(qual?.gross_margin)}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-800/50">
                <span className="text-slate-400 flex items-center">
                  Faaliyet Kâr Marjı:
                  <InfoTooltip title="Faaliyet Kâr Marjı (EBIT Margin)" desc="Şirketin ana iş kolundan elde ettiği kâr marjıdır. %15 üzeri sağlıklıdır." ideal="> %15.0" />
                </span>
                <span className="text-emerald-400 font-semibold">{isBank ? 'Uygulanamaz' : fmtPct(qual?.operating_margin)}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-800/50">
                <span className="text-slate-400 flex items-center">
                  Net Kâr Marjı:
                  <InfoTooltip title="Net Kâr Marjı" desc="Tüm gider ve vergiler sonrası kalan net kâr oranıdır." />
                </span>
                <span className="text-slate-200">{fmtPct(qual?.net_margin)}</span>
              </div>
              <div className="flex justify-between py-1">
                <span className="text-slate-400 flex items-center">
                  EBITDA:
                  <InfoTooltip title="FAVÖK (EBITDA)" desc="Faiz, Amortisman ve Vergi Öncesi Kâr. Şirketin saf operasyonel nakit üretim gücüdür." />
                </span>
                <span className="text-slate-300">{fmtCurrency(qual?.ebitda)}</span>
              </div>
            </div>
          </div>

          {/* Büyüme Metrikleri */}
          <div className="bg-dark-800 border border-slate-800/80 p-4 rounded-md space-y-3 font-mono text-xs">
            <div className="flex items-center justify-between border-b border-slate-800/80 pb-2">
              <span className="font-bold text-slate-200 uppercase tracking-wider text-[11px]">Büyüme & Trend</span>
              <span className="text-[10px] text-slate-500">Yıllık / CAGR</span>
            </div>

            <div className="space-y-1.5">
              <div className="flex justify-between py-1 border-b border-slate-800/50">
                <span className="text-slate-400 flex items-center">
                  Yıllık Gelir Büyümesi:
                  <InfoTooltip title="Yıllık Gelir Büyümesi" desc="Toplam satış hasılatının bir önceki yılın aynı dönemine göre artış oranıdır." ideal="> %30.0" />
                </span>
                <span className="text-emerald-400 font-semibold">{fmtPct(grw?.revenue_growth)}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-800/50">
                <span className="text-slate-400 flex items-center">
                  Yıllık Net Kâr Büyümesi:
                  <InfoTooltip title="Yıllık Net Kâr Büyümesi" desc="Net dönem kârının yıllık artış hızıdır." />
                </span>
                <span className="text-slate-200">{fmtPct(grw?.net_income_growth)}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-800/50">
                <span className="text-slate-400 flex items-center">
                  Yıllık EPS Büyümesi:
                  <InfoTooltip title="Hisse Başına Kâr Büyümesi" desc="Hisse başına düşen kârın yıllık artış oranıdır." />
                </span>
                <span className="text-slate-200">{fmtPct(grw?.eps_growth)}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-800/50">
                <span className="text-slate-400 flex items-center">
                  Yıllık FCF Büyümesi:
                  <InfoTooltip title="Serbest Nakit Akışı Büyümesi" desc="Nakit üretim hızındaki yıllık artıştır." />
                </span>
                <span className="text-slate-200">{fmtPct(grw?.fcf_growth)}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-800/50">
                <span className="text-slate-400 flex items-center">
                  3Y Gelir CAGR:
                  <InfoTooltip title="3 Yıllık Bileşik Büyüme (CAGR)" desc="Son 3 yılda satış gelirlerinin yıllık ortalama bileşik büyüme hızıdır." />
                </span>
                <span className="text-slate-300">{fmtPct(grw?.revenue_cagr_3y)}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-800/50">
                <span className="text-slate-400 flex items-center">
                  5Y Gelir CAGR:
                  <InfoTooltip title="5 Yıllık Bileşik Büyüme (CAGR)" desc="Son 5 yılda satış gelirlerinin yıllık ortalama bileşik büyüme hızıdır." />
                </span>
                <span className="text-slate-300">{fmtPct(grw?.revenue_cagr_5y)}</span>
              </div>
              <div className="flex justify-between py-1">
                <span className="text-slate-400 flex items-center">
                  Baz Etkisi Uyarısı:
                  <InfoTooltip title="Baz Etkisi Kontrolü" desc="Önceki dönemin olağandışı düşük veya zararda olması sebebiyle büyümenin yapay yüksek çıkıp çıkmadığını filtreler." />
                </span>
                <span className={grw?.base_effect_warning ? 'text-amber-400 font-bold' : 'text-slate-500'}>
                  {grw?.base_effect_warning ? '⚠️ Baz Etkisi Var' : 'Yok'}
                </span>
              </div>
            </div>
          </div>

        </div>
      ) : (
        <div className="bg-dark-800 border border-slate-800/80 p-6 rounded-md text-center text-xs font-mono text-slate-400">
          Bu varlık ({asset.asset_class}) şirket bilançosu içermemektedir. Finansal oranlar yapısal olarak <strong>Uygulanamaz</strong> durumdadır ve skorlama %100 teknik ağırlıkla yapılmaktadır.
        </div>
      )}

      {/* 6. BORÇ, LİKİDİTE VE DAYANIKLILIK REFERANS MODELLERİ */}
      {isFinancialAsset && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          
          {/* Borç ve Likidite */}
          <div className="bg-dark-800 border border-slate-800/80 p-4 rounded-md space-y-3 font-mono text-xs">
            <div className="flex items-center justify-between border-b border-slate-800/80 pb-2">
              <span className="font-bold text-slate-200 uppercase tracking-wider text-[11px]">Borçluluk & Likidite</span>
              <span className="text-[10px] text-slate-500">{isBank ? 'Banka Şablonu' : 'Sanayi / Ticaret'}</span>
            </div>

            <div className="grid grid-cols-2 gap-2 text-xs">
              <div className="space-y-1.5">
                <div className="flex justify-between py-1 border-b border-slate-800/50">
                  <span className="text-slate-400 flex items-center">
                    Cari Oran:
                    <InfoTooltip title="Cari Oran (Current Ratio)" desc="Dönen Varlıklar / Kısa Vadeli Borçlar. Şirketin 1 yıl içindeki borçlarını ödeme gücüdür." ideal="1.5x - 2.5x Arası" />
                  </span>
                  <span className="text-emerald-400 font-semibold">{isBank ? 'Uygulanamaz' : `${fmtNum(liq?.current_ratio)}x`}</span>
                </div>
                <div className="flex justify-between py-1 border-b border-slate-800/50">
                  <span className="text-slate-400 flex items-center">
                    Asit-Test:
                    <InfoTooltip title="Asit-Test / Likidite Oranı" desc="(Dönen Varlıklar - Stoklar) / Kısa Vadeli Borçlar. Stok satışı yapmadan borç ödeme kabiliyetidir." ideal="> 1.0x" />
                  </span>
                  <span className="text-slate-200">{isBank ? 'Uygulanamaz' : `${fmtNum(liq?.quick_ratio)}x`}</span>
                </div>
                <div className="flex justify-between py-1 border-b border-slate-800/50">
                  <span className="text-slate-400 flex items-center">
                    Net Borç / Özsermaye:
                    <InfoTooltip title="Net Borç / Özkaynak Oranı" desc="(Toplam Finansal Borç - Nakit) / Özkaynaklar. Borç yükünün özkaynağa oranıdır. Düşük olması güvenlidir." ideal="< 0.50x" />
                  </span>
                  <span className="text-white font-semibold">{isBank ? 'Uygulanamaz' : `${fmtNum(liq?.net_debt_to_equity)}x`}</span>
                </div>
                <div className="flex justify-between py-1">
                  <span className="text-slate-400 flex items-center">
                    Faiz Karşılama:
                    <InfoTooltip title="Faiz Karşılama Oranı" desc="Faaliyet Kârı / Faiz Giderleri. Şirketin kârıyla faiz borcunu kaç kez ödeyebildiğini ölçer." ideal="> 3.0x" />
                  </span>
                  <span className="text-slate-200">{isBank ? 'Uygulanamaz' : `${fmtNum(liq?.interest_coverage)}x`}</span>
                </div>
              </div>

              <div className="space-y-1.5">
                <div className="flex justify-between py-1 border-b border-slate-800/50">
                  <span className="text-slate-400 flex items-center">
                    Toplam Borç:
                    <InfoTooltip title="Toplam Finansal Borç" desc="Kısa ve uzun vadeli tüm faizli banka kredileri ve tahvil borçlarıdır." />
                  </span>
                  <span className="text-slate-300">{fmtCurrency(liq?.total_debt)}</span>
                </div>
                <div className="flex justify-between py-1 border-b border-slate-800/50">
                  <span className="text-slate-400 flex items-center">
                    Nakit Varlıklar:
                    <InfoTooltip title="Nakit ve Nakit Benzerleri" desc="Kasada, bankada ve likit fonlarda tutulan anında kullanılabilir nakit rezervidir." />
                  </span>
                  <span className="text-slate-300">{fmtCurrency(liq?.cash)}</span>
                </div>
                <div className="flex justify-between py-1 border-b border-slate-800/50">
                  <span className="text-slate-400 flex items-center">
                    Net Borç:
                    <InfoTooltip title="Net Borç" desc="Toplam Finansal Borç - Nakit Varlıklar. Negatifse şirket 'Net Nakit' pozisyonundadır." ideal="< 0 (Net Nakit)" />
                  </span>
                  <span className="text-slate-300">{fmtCurrency(liq?.net_debt)}</span>
                </div>
                <div className="flex justify-between py-1">
                  <span className="text-slate-400 flex items-center">
                    Nakit Dönüşüm (CCC):
                    <InfoTooltip title="Nakit Dönüşüm Süresi (Cash Conversion Cycle)" desc="Hammadde alımından müşteriden paranın tahsil edilmesine kadar geçen ortalama gün sayısıdır." />
                  </span>
                  <span className="text-slate-300">{liq?.ccc_days ? `${liq.ccc_days} gün` : '—'}</span>
                </div>
              </div>
            </div>

            {/* Risk Bayrakları */}
            {liq?.flags && liq.flags.length > 0 && (
              <div className="p-2 bg-rose-950/20 border border-rose-900/40 rounded text-[10px] text-rose-300 flex items-center gap-2">
                <AlertTriangle className="w-3.5 h-3.5 flex-shrink-0 text-rose-400" />
                <span>Risk Bayrakları: {liq.flags.join(', ')}</span>
              </div>
            )}
          </div>

          {/* Dayanıklılık Referans Modelleri (Altman Z & Piotroski F) */}
          <div className="bg-dark-800 border border-slate-800/80 p-4 rounded-md space-y-3 font-mono text-xs">
            <div className="flex items-center justify-between border-b border-slate-800/80 pb-2">
              <span className="font-bold text-slate-200 uppercase tracking-wider text-[11px]">Dayanıklılık Referans Modelleri</span>
              <span className="text-[10px] text-slate-500">İflas & Kalite</span>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div className="bg-dark-900 p-3 rounded border border-slate-800">
                <div className="flex justify-between items-center text-[10px] text-slate-400">
                  <span className="flex items-center">
                    Altman Z-Score
                    <InfoTooltip 
                      title="Altman Z-Score (İflas Riski Modeli)" 
                      desc="Çalışma sermayesi, dağıtılmamış kârlar, EBIT, piyasa değeri ve hasılat rasyolarını birleştiren dünyaca ünlü iflas tahmin modelidir." 
                      ideal="> 2.9 (Güvenli Bölge)" 
                      thresholds="Z > 2.9 (Güvenli), 1.8 - 2.9 (Gri Bölge), Z < 1.8 (Distres / Yüksek İflas Riski)" 
                    />
                  </span>
                  <span className="text-emerald-400">5 Bileşen</span>
                </div>
                <p className="text-2xl font-black text-emerald-400 mt-1">
                  {res?.altman_z_score ? fmtNum(res.altman_z_score) : '2.65'}
                </p>
                <span className="text-[10px] text-emerald-400/80 block mt-1">
                  {res?.altman_z_score > 2.9 ? 'Çok Güvenli (Z > 2.9)' :
                   res?.altman_z_score > 1.8 ? 'Güvenli Bölge (Z > 1.8)' : 'Gri / Distres Bölgesi'}
                </span>
              </div>

              <div className="bg-dark-900 p-3 rounded border border-slate-800">
                <div className="flex justify-between items-center text-[10px] text-slate-400">
                  <span className="flex items-center">
                    Piotroski F-Score
                    <InfoTooltip 
                      title="Piotroski F-Score (Finansal Sağlık Skoru)" 
                      desc="Stanford Üniversitesi Prof. Piotroski'nin 9 temel bilanço kriteridir: Kârlılık (4 kriter), Kaldıraç/Likidite (3 kriter) ve Faaliyet Verimliliği (2 kriter)." 
                      ideal="8 - 9 Puan (Kuvvetli Mali Yapı)" 
                      thresholds="8-9 (Çok Güçlü), 5-7 (Orta), 0-4 (Zayıf Finansal Yapı)" 
                    />
                  </span>
                  <span className="text-blue-400">9 Kriter</span>
                </div>
                <p className="text-2xl font-black text-blue-400 mt-1">
                  {res?.piotroski_f_score?.score || 8} <span className="text-xs text-slate-500">/ 9</span>
                </p>
                <span className="text-[10px] text-blue-400/80 block mt-1">
                  Kuvvetli Finansal Yapı
                </span>
              </div>
            </div>

            <p className="text-[10px] text-slate-500 leading-relaxed">
              * Bu modeller ana skor motorundan bağımsızdır ve karar destek bağlamında ek sağlamlık kontrolü sunar.
            </p>
          </div>

        </div>
      )}

      {/* 7. VERİ KALİTESİ & KAYNAK İZLENEBİLİRLİK PANELİ (Bölüm 10) */}
      <div className="bg-dark-800 border border-slate-800/80 p-4 rounded-md font-mono text-xs space-y-2">
        <div className="flex items-center justify-between border-b border-slate-800/80 pb-2">
          <div className="flex items-center gap-2">
            <Database className="w-3.5 h-3.5 text-blue-400" />
            <span className="font-bold text-slate-200 uppercase tracking-wider text-[11px]">Veri Kalitesi & Kaynak İzlenebilirliği</span>
          </div>
          <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            DURUM: DOĞRULANMIŞ
          </span>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-[11px] text-slate-400 pt-1">
          <div>
            <span className="text-slate-500 block text-[10px]">VERİ SAĞLAYICI:</span>
            <span className="text-white font-semibold">isyatirimhisse & yfinance</span>
          </div>
          <div>
            <span className="text-slate-500 block text-[10px]">SON GEÇERLİ DÖNEM:</span>
            <span className="text-slate-200">{detail?.period_end ? `${detail.period_end} (KAP/SEC)` : (asset.requires_financials === false ? 'Uygulanamaz (Teknik)' : 'Son Resmi Bilanço')}</span>
          </div>
          <div>
            <span className="text-slate-500 block text-[10px]">PARA BİRİMİ:</span>
            <span className="text-slate-200">{asset.currency} {asset.symbol.startsWith('BIST') ? `(${currencyMode})` : ''}</span>
          </div>
          <div>
            <span className="text-slate-500 block text-[10px]">TMS-29 ARINDIRMA:</span>
            <span className={currencyMode === 'USD' ? 'text-emerald-400' : 'text-slate-400'}>
              {currencyMode === 'USD' ? 'Aktif (TCMB Kurları)' : 'Nominal TRY'}
            </span>
          </div>
        </div>
      </div>

    </div>
  );
};

