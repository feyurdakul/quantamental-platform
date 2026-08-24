import React, { useEffect, useState } from 'react';
import { fetchDashboardSummary, fetchUniverse } from '../api/client';
import { 
  TrendingUp, 
  AlertTriangle, 
  Layers, 
  CheckCircle2, 
  Clock, 
  ArrowUpRight,
  ShieldCheck,
  Zap,
  RefreshCw,
  Search
} from 'lucide-react';

interface DashboardProps {
  onSelectAsset: (symbol: string) => void;
  onNavigateToSettings: () => void;
}

export const Dashboard: React.FC<DashboardProps> = ({ onSelectAsset, onNavigateToSettings }) => {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [selectedClass, setSelectedClass] = useState<string>('ALL');

  const loadData = async () => {
    try {
      const summary = await fetchDashboardSummary();
      setData(summary);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 5000);
    return () => clearInterval(interval);
  }, []);

  if (loading && !data) {
    return (
      <div className="flex items-center justify-center min-h-[50vh]">
        <div className="flex flex-col items-center gap-3">
          <RefreshCw className="w-6 h-6 text-blue-400 animate-spin" />
          <p className="text-xs font-mono text-slate-400">Terminal verileri yükleniyor...</p>
        </div>
      </div>
    );
  }

  const leaderboards = data?.leaderboards || {};
  let topPotential = leaderboards.top_potential || [];
  let mostRisky = leaderboards.most_risky_overvalued || [];

  // Varlık sınıfı filtrelemesi
  if (selectedClass !== 'ALL') {
    topPotential = topPotential.filter((item: any) => {
      if (selectedClass === 'BIST') return item.symbol.startsWith('BIST:');
      if (selectedClass === 'US') return item.symbol.startsWith('NASDAQ:') || item.symbol.startsWith('NYSE:');
      if (selectedClass === 'FOREX') return item.symbol.startsWith('FX:') || item.symbol.startsWith('TVC:');
      return true;
    });
    mostRisky = mostRisky.filter((item: any) => {
      if (selectedClass === 'BIST') return item.symbol.startsWith('BIST:');
      if (selectedClass === 'US') return item.symbol.startsWith('NASDAQ:') || item.symbol.startsWith('NYSE:');
      if (selectedClass === 'FOREX') return item.symbol.startsWith('FX:') || item.symbol.startsWith('TVC:');
      return true;
    });
  }

  const getSignalBadge = (signal: string) => {
    switch (signal) {
      case 'STRONG_BUY':
        return <span className="px-1.5 py-0.5 rounded text-[10px] font-bold bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">STRONG BUY</span>;
      case 'BUY':
        return <span className="px-1.5 py-0.5 rounded text-[10px] font-semibold bg-teal-500/15 text-teal-400 border border-teal-500/30">BUY</span>;
      case 'HOLD':
        return <span className="px-1.5 py-0.5 rounded text-[10px] font-semibold bg-amber-500/15 text-amber-300 border border-amber-500/30">HOLD</span>;
      case 'WATCH':
        return <span className="px-1.5 py-0.5 rounded text-[10px] font-semibold bg-blue-500/15 text-blue-300 border border-blue-500/30">WATCH</span>;
      case 'SELL':
        return <span className="px-1.5 py-0.5 rounded text-[10px] font-semibold bg-rose-500/15 text-rose-300 border border-rose-500/30">SELL</span>;
      case 'STRONG_SELL':
        return <span className="px-1.5 py-0.5 rounded text-[10px] font-bold bg-rose-600/20 text-rose-400 border border-rose-600/40">STRONG SELL</span>;
      default:
        return <span className="px-1.5 py-0.5 rounded text-[10px] bg-slate-800 text-slate-400">HOLD</span>;
    }
  };

  return (
    <div className="space-y-5">
      
      {/* 4'lü Üst İstatistik Şeridi */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3.5">
        
        <div className="bg-dark-800 border border-slate-800/80 p-4 rounded-md flex items-center justify-between">
          <div>
            <p className="text-[10px] font-mono uppercase text-slate-400 tracking-wider">Aktif Evren Büyüklüğü</p>
            <h3 className="text-xl font-bold text-white mt-1 font-mono">{data?.total_assets || 668} Varlık</h3>
            <p className="text-[10px] text-blue-400 mt-0.5 flex items-center gap-1 font-mono">
              <Layers className="w-3 h-3" /> BIST 100, S&P 500, FX & Emtia
            </p>
          </div>
          <div className="w-9 h-9 rounded bg-blue-600/10 border border-blue-500/20 flex items-center justify-center text-blue-400">
            <Layers className="w-4 h-4" />
          </div>
        </div>

        <div className="bg-dark-800 border border-slate-800/80 p-4 rounded-md flex items-center justify-between">
          <div>
            <p className="text-[10px] font-mono uppercase text-slate-400 tracking-wider">Tarama Durumu</p>
            <h3 className="text-xl font-bold text-emerald-400 mt-1 font-mono">{data?.scan_stage || 'HAZIR'}</h3>
            <p className="text-[10px] text-emerald-400/80 mt-0.5 flex items-center gap-1 font-mono">
              <CheckCircle2 className="w-3 h-3" /> {data?.processed_assets || data?.total_assets || 0} Varlık İşlendi
            </p>
          </div>
          <div className="w-9 h-9 rounded bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400">
            <ShieldCheck className="w-4 h-4" />
          </div>
        </div>

        <div className="bg-dark-800 border border-slate-800/80 p-4 rounded-md flex items-center justify-between">
          <div>
            <p className="text-[10px] font-mono uppercase text-slate-400 tracking-wider">Veri Sağlayıcılar</p>
            <h3 className="text-xl font-bold text-white mt-1 font-mono">7 / 7 Online</h3>
            <p className="text-[10px] text-purple-400 mt-0.5 flex items-center gap-1 font-mono">
              <Zap className="w-3 h-3" /> TV, GF, FRED, YF, FMP, İŞ, FH
            </p>
          </div>
          <div className="w-9 h-9 rounded bg-purple-500/10 border border-purple-500/20 flex items-center justify-center text-purple-400">
            <Zap className="w-4 h-4" />
          </div>
        </div>

        <div className="bg-dark-800 border border-slate-800/80 p-4 rounded-md flex items-center justify-between">
          <div>
            <p className="text-[10px] font-mono uppercase text-slate-400 tracking-wider">Veri Tazeliği</p>
            <h3 className="text-xl font-bold text-white mt-1 font-mono">Canlı Akış</h3>
            <p className="text-[10px] text-slate-400 mt-0.5 flex items-center gap-1 font-mono">
              <Clock className="w-3 h-3" /> Anlık SSE & WebSocket
            </p>
          </div>
          <div className="w-9 h-9 rounded bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amber-400">
            <Clock className="w-4 h-4" />
          </div>
        </div>

      </div>

      {/* Varlık Sınıfı Filtre Sekmeleri */}
      <div className="flex items-center gap-1 bg-dark-800/60 p-1 rounded-md border border-slate-800/80 overflow-x-auto">
        {[
          { id: 'ALL', label: 'TÜM EVREN' },
          { id: 'BIST', label: '🇹🇷 BIST 100' },
          { id: 'US', label: '🇺🇸 ABD EQUITIES' },
          { id: 'FOREX', label: '💱 FX & EMTİA' }
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setSelectedClass(tab.id)}
            className={`px-3 py-1.5 rounded text-[11px] font-mono font-medium transition-colors whitespace-nowrap ${
              selectedClass === tab.id
                ? 'bg-blue-600/20 text-blue-400 border border-blue-500/30 font-semibold'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* 2 Kolonlu Liderlik Tabloları */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        
        {/* Sol Kolon: En Güçlü Potansiyel (Top Potential) */}
        <div className="bg-dark-800 border border-slate-800/80 rounded-md p-4 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between pb-3 mb-3 border-b border-slate-800/80">
              <div className="flex items-center gap-2">
                <TrendingUp className="w-4 h-4 text-emerald-400" />
                <h4 className="font-bold text-xs font-mono uppercase tracking-wider text-slate-100">
                  En Güçlü Potansiyel Liderleri
                </h4>
              </div>
              <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                GÜÇLÜ AL SİNYALLERİ
              </span>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-slate-800 text-slate-500 font-mono text-[10px]">
                    <th className="pb-2 font-medium">SEMBOL</th>
                    <th className="pb-2 font-medium">SKOR (/10)</th>
                    <th className="pb-2 font-medium">TEMEL NOT</th>
                    <th className="pb-2 font-medium">SİNYAL</th>
                    <th className="pb-2 font-medium">F/K</th>
                    <th className="pb-2 font-medium">ALTMAN Z</th>
                    <th className="pb-2 font-medium text-right">DETAY</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60 font-mono text-xs">
                  {topPotential.length > 0 ? (
                    topPotential.map((item: any) => {
                      const letter = (item.rating_letter && ['S', 'A', 'B', 'C', 'D'].includes(item.rating_letter)) ? item.rating_letter : null;
                      const rScore = item.rating_score;
                      return (
                      <tr 
                        key={item.symbol} 
                        onClick={() => onSelectAsset(item.symbol)}
                        className="hover:bg-slate-800/50 transition-colors cursor-pointer group"
                      >
                        <td className="py-2.5 font-bold text-slate-200 group-hover:text-blue-400">
                          {item.symbol}
                        </td>
                        <td className="py-2.5">
                          <span className="font-bold text-emerald-400">{item.composite_score?.toFixed(2)}</span>
                          <span className="text-slate-500 text-[10px]"> / 10.0</span>
                        </td>
                        <td className="py-2.5">
                          {letter ? (
                            <div className="flex items-center gap-1.5">
                              <span className={`px-1.5 py-0.5 rounded text-[10px] font-black border ${
                                letter === 'S' ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40' :
                                letter === 'A' ? 'bg-teal-500/20 text-teal-300 border-teal-500/40' :
                                letter === 'B' ? 'bg-amber-500/20 text-amber-300 border-amber-500/40' :
                                letter === 'C' ? 'bg-rose-500/20 text-rose-300 border-rose-500/40' : 'bg-rose-700/30 text-rose-400 border-rose-700/50'
                              }`}>
                                {letter}
                              </span>
                              {rScore && <span className="text-[10px] text-slate-400">({rScore}/30)</span>}
                            </div>
                          ) : (
                            <span className="text-slate-600 font-mono text-xs">—</span>
                          )}
                        </td>
                        <td className="py-2.5">
                          {getSignalBadge(item.signal)}
                        </td>
                        <td className="py-2.5 text-slate-400">
                          {item.pe_ratio ? `${item.pe_ratio}x` : '—'}
                        </td>
                        <td className="py-2.5 text-slate-400">
                          {item.altman_z ? item.altman_z : '—'}
                        </td>
                        <td className="py-2.5 text-right">
                          <button className="p-1 rounded text-slate-500 group-hover:text-blue-400">
                            <ArrowUpRight className="w-3.5 h-3.5" />
                          </button>
                        </td>
                      </tr>
                      );
                    })
                  ) : (
                    <tr>
                      <td colSpan={7} className="py-8 text-center text-slate-500 text-xs font-mono">
                        Seçilen varlık sınıfında henüz skorlanmış varlık yok. <button onClick={onNavigateToSettings} className="text-blue-400 underline">Taramayı Başlatın</button>.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* Sağ Kolon: En Riskli & Aşırı Değerli */}
        <div className="bg-dark-800 border border-slate-800/80 rounded-md p-4 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between pb-3 mb-3 border-b border-slate-800/80">
              <div className="flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 text-rose-400" />
                <h4 className="font-bold text-xs font-mono uppercase tracking-wider text-slate-100">
                  En Riskli & Aşırı Değerli Listesi
                </h4>
              </div>
              <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-rose-500/10 text-rose-400 border border-rose-500/20">
                RİSK / SAT SİNYALİ
              </span>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-slate-800 text-slate-500 font-mono text-[10px]">
                    <th className="pb-2 font-medium">SEMBOL</th>
                    <th className="pb-2 font-medium">SKOR (/10)</th>
                    <th className="pb-2 font-medium">TEMEL NOT</th>
                    <th className="pb-2 font-medium">SİNYAL</th>
                    <th className="pb-2 font-medium">F/K</th>
                    <th className="pb-2 font-medium">ALTMAN Z</th>
                    <th className="pb-2 font-medium text-right">DETAY</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60 font-mono text-xs">
                  {mostRisky.length > 0 ? (
                    mostRisky.map((item: any) => {
                      const letter = (item.rating_letter && ['S', 'A', 'B', 'C', 'D'].includes(item.rating_letter)) ? item.rating_letter : null;
                      const rScore = item.rating_score;
                      return (
                      <tr 
                        key={item.symbol} 
                        onClick={() => onSelectAsset(item.symbol)}
                        className="hover:bg-slate-800/50 transition-colors cursor-pointer group"
                      >
                        <td className="py-2.5 font-bold text-slate-200 group-hover:text-rose-400">
                          {item.symbol}
                        </td>
                        <td className="py-2.5">
                          <span className="font-bold text-rose-400">{item.composite_score?.toFixed(2)}</span>
                          <span className="text-slate-500 text-[10px]"> / 10.0</span>
                        </td>
                        <td className="py-2.5">
                          {letter ? (
                            <div className="flex items-center gap-1.5">
                              <span className={`px-1.5 py-0.5 rounded text-[10px] font-black border ${
                                letter === 'S' ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40' :
                                letter === 'A' ? 'bg-teal-500/20 text-teal-300 border-teal-500/40' :
                                letter === 'B' ? 'bg-amber-500/20 text-amber-300 border-amber-500/40' :
                                letter === 'C' ? 'bg-rose-500/20 text-rose-300 border-rose-500/40' : 'bg-rose-700/30 text-rose-400 border-rose-700/50'
                              }`}>
                                {letter}
                              </span>
                              {rScore && <span className="text-[10px] text-slate-400">({rScore}/30)</span>}
                            </div>
                          ) : (
                            <span className="text-slate-600 font-mono text-xs">—</span>
                          )}
                        </td>
                        <td className="py-2.5">
                          {getSignalBadge(item.signal)}
                        </td>
                        <td className="py-2.5 text-slate-400">
                          {item.pe_ratio ? `${item.pe_ratio}x` : '—'}
                        </td>
                        <td className="py-2.5 text-rose-400">
                          {item.altman_z ? item.altman_z : '—'}
                        </td>
                        <td className="py-2.5 text-right">
                          <button className="p-1 rounded text-slate-500 group-hover:text-rose-400">
                            <ArrowUpRight className="w-3.5 h-3.5" />
                          </button>
                        </td>
                      </tr>
                      );
                    })
                  ) : (
                    <tr>
                      <td colSpan={7} className="py-8 text-center text-slate-500 text-xs font-mono">
                        Risk listesi tarama sonuçlarına göre otomatik güncellenir.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>

      </div>

    </div>
  );
};
