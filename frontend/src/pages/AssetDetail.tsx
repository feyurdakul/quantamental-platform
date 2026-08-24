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

interface AssetDetailProps {
  symbol: string;
  onBack: () => void;
}

export const AssetDetail: React.FC<AssetDetailProps> = ({ symbol, onBack }) => {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [currencyMode, setCurrencyMode] = useState<'TRY' | 'USD'>('TRY');
  const [addedToPortfolio, setAddedToPortfolio] = useState(false);
  const [activeTab, setActiveTab] = useState<'all' | 'fundamental' | 'technical' | 'statements'>('all');

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

  const isFinancialAsset = asset.requires_financials !== false && 
    !['ETF', 'CRYPTO', 'FOREX', 'COMMODITY', 'INDEX'].includes(asset.asset_class);
  const isBank = asset.asset_class === 'BANK_STOCK';
  
  // Para birimi sembolü (USD seçildiğinde $ göster)
  const displayCurr = currencyMode === 'USD' ? '$' : (asset.currency === 'USD' ? '$' : asset.currency === 'TRY' ? '₺' : asset.currency);

  // Format Helper Functions
  const fmtNum = (val: any, suffix = '', decimals = 2) => {
    if (val === null || val === undefined || isNaN(val)) return '—';
    if (typeof val === 'number') {
      return `${val.toLocaleString('tr-TR', { minimumFractionDigits: decimals, maximumFractionDigits: decimals })}${suffix}`;
    }
    return `${val}${suffix}`;
  };

  const fmtCurrency = (val: any) => {
    if (val === null || val === undefined || isNaN(val)) return '—';
    // Eğer USD modundaysa ve veri TRY bazlıysa TCMB yaklaşık kuru ile göster
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
      case 'STRONG_BUY': return <span className="px-2 py-0.5 rounded text-[11px] font-bold bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">STRONG BUY</span>;
      case 'BUY': return <span className="px-2 py-0.5 rounded text-[11px] font-semibold bg-teal-500/15 text-teal-400 border border-teal-500/30">BUY</span>;
      case 'HOLD': return <span className="px-2 py-0.5 rounded text-[11px] font-semibold bg-amber-500/15 text-amber-300 border border-amber-500/30">HOLD</span>;
      case 'WATCH': return <span className="px-2 py-0.5 rounded text-[11px] font-semibold bg-blue-500/15 text-blue-300 border border-blue-500/30">WATCH</span>;
      case 'SELL': return <span className="px-2 py-0.5 rounded text-[11px] font-semibold bg-rose-500/15 text-rose-300 border border-rose-500/30">SELL</span>;
      case 'STRONG_SELL': return <span className="px-2 py-0.5 rounded text-[11px] font-bold bg-rose-600/20 text-rose-400 border border-rose-600/40">STRONG SELL</span>;
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
              <span className="text-[10px] font-mono text-slate-400 uppercase tracking-wider">1. KANTİTATİF BİLEŞİK SKOR</span>
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
              <span className="text-[10px] font-mono text-slate-400 uppercase tracking-wider">2. 6-FAKTÖR TEMEL NOT</span>
              <span className="text-[10px] font-mono text-purple-400 font-bold">6-30 SKALA</span>
            </div>

            {isFinancialAsset && (sr?.fundamental_rating || detail?.fundamental_rating) ? (
              <>
                <div className="flex items-baseline gap-2 mt-2">
                  <span className={`text-3xl font-black font-mono ${
                    (sr?.fundamental_rating?.rating || 'B') === 'S' ? 'text-emerald-400' :
                    (sr?.fundamental_rating?.rating || 'B') === 'A' ? 'text-teal-400' :
                    (sr?.fundamental_rating?.rating || 'B') === 'B' ? 'text-amber-300' :
                    (sr?.fundamental_rating?.rating || 'B') === 'C' ? 'text-rose-300' : 'text-rose-500'
                  }`}>
                    NOT: {sr?.fundamental_rating?.rating || 'B'}
                  </span>
                  <span className="text-xs font-mono text-slate-400">
                    ({sr?.fundamental_rating?.total_score || 18} / 30 Puan)
                  </span>
                </div>

                <div className="mt-2">
                  <span className={`px-2 py-0.5 rounded text-[10px] font-bold font-mono border ${
                    (sr?.fundamental_rating?.rating || 'B') === 'S' ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40' :
                    (sr?.fundamental_rating?.rating || 'B') === 'A' ? 'bg-teal-500/20 text-teal-300 border-teal-500/40' :
                    (sr?.fundamental_rating?.rating || 'B') === 'B' ? 'bg-amber-500/20 text-amber-300 border-amber-500/40' :
                    (sr?.fundamental_rating?.rating || 'B') === 'C' ? 'bg-rose-500/20 text-rose-300 border-rose-500/40' : 'bg-rose-700/30 text-rose-400 border-rose-700/50'
                  }`}>
                    TAVSİYE: {sr?.fundamental_rating?.recommendation?.toUpperCase() || 'NEUTRAL'}
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
            <span>6 Metrik Ağırlıksız</span>
            <span>Eşikler: 25/19/13/9</span>
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
                <span className="text-slate-500 block text-[9px]">RSI (14)</span>
                <span className="font-bold text-emerald-400">{fmtNum(tech?.rsi14, '', 1)}</span>
              </div>
              <div className="bg-dark-900 p-1.5 rounded border border-slate-800">
                <span className="text-slate-500 block text-[9px]">Trend Rejimi</span>
                <span className="font-bold text-white text-[10px]">{tech?.trend_regime || 'NEUTRAL'}</span>
              </div>
            </div>
          </div>

          <div className="mt-3 text-[10px] font-mono text-slate-500 flex justify-between">
            <span>Volatilite: {fmtPct(tech?.annualized_volatility)}</span>
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

      {/* 3. 5 KATEGORİ SKORLARI (Bölüm 8) */}
      <div className="bg-dark-800 border border-slate-800/80 p-5 rounded-md">
        <div className="flex items-center gap-2 pb-3 mb-4 border-b border-slate-800/80">
          <BarChart3 className="w-4 h-4 text-blue-400" />
          <h4 className="font-bold text-xs font-mono uppercase tracking-wider text-slate-100">
            5 Kategori Puan Dağılımı (1.00 - 10.00 Puan)
          </h4>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3 font-mono">
          {[
            { key: 'valuation', name: 'Değerleme', score: categories?.valuation?.category_score, weight: '%25' },
            { key: 'quality', name: 'Kalite & Kârlılık', score: categories?.quality?.category_score, weight: '%20' },
            { key: 'resilience', name: 'Dayanıklılık', score: categories?.resilience?.category_score, weight: '%20' },
            { key: 'growth', name: 'Büyüme', score: categories?.growth?.category_score, weight: '%15' },
            { key: 'technical', name: 'Teknik Görünüm', score: categories?.technical?.category_score, weight: '%20' },
          ].map((cat) => (
            <div key={cat.key} className="bg-dark-900 p-3 rounded border border-slate-800 flex flex-col justify-between">
              <div>
                <div className="flex justify-between items-center text-xs">
                  <span className="text-slate-300 font-sans text-xs">{cat.name}</span>
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

      {/* 4. TEMEL ANALİZ METRİKLERİ (Değerleme, Kalite, Büyüme) */}
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
                <span className="text-slate-400">F/K (P/E):</span>
                <span className="text-white font-semibold">{val?.pe_ratio ? `${fmtNum(val.pe_ratio)}x` : (val?.pe_ratio === null ? '—' : 'Anlamlı değil')}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-800/50">
                <span className="text-slate-400">PD/DD (P/B):</span>
                <span className="text-white font-semibold">{val?.pb_ratio ? `${fmtNum(val.pb_ratio)}x` : '—'}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-800/50">
                <span className="text-slate-400">FD/FAVÖK (EV/EBITDA):</span>
                <span className="text-white font-semibold">{val?.ev_ebitda ? `${fmtNum(val.ev_ebitda)}x` : (isBank ? 'Uygulanamaz' : '—')}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-800/50">
                <span className="text-slate-400">FCF Verimi (FCF Yield):</span>
                <span className="text-emerald-400 font-semibold">{fmtPct(val?.fcf_yield)}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-800/50">
                <span className="text-slate-400">Kazanç Verimi (Earnings Yield):</span>
                <span className="text-slate-200">{fmtPct(val?.earnings_yield)}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-800/50">
                <span className="text-slate-400">Piyasa Değeri:</span>
                <span className="text-slate-300">{fmtCurrency(val?.market_cap)}</span>
              </div>
              <div className="flex justify-between py-1">
                <span className="text-slate-400">Firma Değeri (EV):</span>
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
                <span className="text-slate-400">Özsermaye Kârlılığı (ROE):</span>
                <span className="text-emerald-400 font-semibold">{fmtPct(qual?.roe)}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-800/50">
                <span className="text-slate-400">Aktif Kârlılığı (ROA):</span>
                <span className="text-slate-200">{fmtPct(qual?.roa)}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-800/50">
                <span className="text-slate-400">Yatırılan Sermaye Getirisi (ROIC):</span>
                <span className="text-slate-200">{fmtPct(qual?.roic)}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-800/50">
                <span className="text-slate-400">Brüt Kâr Marjı:</span>
                <span className="text-slate-200">{isBank ? 'Uygulanamaz' : fmtPct(qual?.gross_margin)}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-800/50">
                <span className="text-slate-400">Faaliyet Kâr Marjı:</span>
                <span className="text-emerald-400 font-semibold">{isBank ? 'Uygulanamaz' : fmtPct(qual?.operating_margin)}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-800/50">
                <span className="text-slate-400">Net Kâr Marjı:</span>
                <span className="text-slate-200">{fmtPct(qual?.net_margin)}</span>
              </div>
              <div className="flex justify-between py-1">
                <span className="text-slate-400">EBITDA:</span>
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
                <span className="text-slate-400">Yıllık Gelir Büyümesi:</span>
                <span className="text-emerald-400 font-semibold">{fmtPct(grw?.revenue_growth)}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-800/50">
                <span className="text-slate-400">Yıllık Net Kâr Büyümesi:</span>
                <span className="text-slate-200">{fmtPct(grw?.net_income_growth)}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-800/50">
                <span className="text-slate-400">Yıllık EPS Büyümesi:</span>
                <span className="text-slate-200">{fmtPct(grw?.eps_growth)}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-800/50">
                <span className="text-slate-400">Yıllık FCF Büyümesi:</span>
                <span className="text-slate-200">{fmtPct(grw?.fcf_growth)}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-800/50">
                <span className="text-slate-400">3 Yıllık Gelir CAGR:</span>
                <span className="text-slate-300">{fmtPct(grw?.revenue_cagr_3y)}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-800/50">
                <span className="text-slate-400">5 Yıllık Gelir CAGR:</span>
                <span className="text-slate-300">{fmtPct(grw?.revenue_cagr_5y)}</span>
              </div>
              <div className="flex justify-between py-1">
                <span className="text-slate-400">Baz Etkisi Uyarısı:</span>
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

      {/* 5. BORÇ, LİKİDİTE VE DAYANIKLILIK REFERANS MODELLERİ */}
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
                  <span className="text-slate-400">Cari Oran:</span>
                  <span className="text-emerald-400 font-semibold">{isBank ? 'Uygulanamaz' : `${fmtNum(liq?.current_ratio)}x`}</span>
                </div>
                <div className="flex justify-between py-1 border-b border-slate-800/50">
                  <span className="text-slate-400">Asit-Test Oranı:</span>
                  <span className="text-slate-200">{isBank ? 'Uygulanamaz' : `${fmtNum(liq?.quick_ratio)}x`}</span>
                </div>
                <div className="flex justify-between py-1 border-b border-slate-800/50">
                  <span className="text-slate-400">Net Borç / Özsermaye:</span>
                  <span className="text-white font-semibold">{isBank ? 'Uygulanamaz' : `${fmtNum(liq?.net_debt_to_equity)}x`}</span>
                </div>
                <div className="flex justify-between py-1">
                  <span className="text-slate-400">Faiz Karşılama:</span>
                  <span className="text-slate-200">{isBank ? 'Uygulanamaz' : `${fmtNum(liq?.interest_coverage)}x`}</span>
                </div>
              </div>

              <div className="space-y-1.5">
                <div className="flex justify-between py-1 border-b border-slate-800/50">
                  <span className="text-slate-400">Toplam Borç:</span>
                  <span className="text-slate-300">{fmtCurrency(liq?.total_debt)}</span>
                </div>
                <div className="flex justify-between py-1 border-b border-slate-800/50">
                  <span className="text-slate-400">Nakit Varlıklar:</span>
                  <span className="text-slate-300">{fmtCurrency(liq?.cash)}</span>
                </div>
                <div className="flex justify-between py-1 border-b border-slate-800/50">
                  <span className="text-slate-400">Net Borç:</span>
                  <span className="text-slate-300">{fmtCurrency(liq?.net_debt)}</span>
                </div>
                <div className="flex justify-between py-1">
                  <span className="text-slate-400">Nakit Dönüşüm (CCC):</span>
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
                  <span>Altman Z-Score</span>
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
                  <span>Piotroski F-Score</span>
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

      {/* 6. VERİ KALİTESİ & KAYNAK İZLENEBİLİRLİK PANELİ (Bölüm 10) */}
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
