import React, { useEffect, useState } from 'react';
import { fetchUniverse } from '../api/client';
import { Search, ArrowUpDown, ChevronRight, RefreshCw, Filter } from 'lucide-react';

interface UniverseProps {
  onSelectAsset: (symbol: string) => void;
}

export const Universe: React.FC<UniverseProps> = ({ onSelectAsset }) => {
  const [assets, setAssets] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedClass, setSelectedClass] = useState<string>('ALL');
  const [sortField, setSortField] = useState<string>('symbol');
  const [sortAsc, setSortAsc] = useState<boolean>(true);

  const loadUniverse = async () => {
    setLoading(true);
    try {
      const cls = selectedClass === 'ALL' ? undefined : selectedClass;
      const res = await fetchUniverse(cls);
      setAssets(res.assets || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadUniverse();
  }, [selectedClass]);

  const filteredAssets = assets
    .filter((a) => {
      const matchesSearch = 
        a.symbol.toLowerCase().includes(searchTerm.toLowerCase()) ||
        a.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        (a.sector && a.sector.toLowerCase().includes(searchTerm.toLowerCase()));
      return matchesSearch;
    })
    .sort((a, b) => {
      let valA = a[sortField];
      let valB = b[sortField];
      if (valA === null || valA === undefined) valA = sortAsc ? Infinity : -Infinity;
      if (valB === null || valB === undefined) valB = sortAsc ? Infinity : -Infinity;
      if (typeof valA === 'string') {
        return sortAsc ? valA.localeCompare(valB) : valB.localeCompare(valA);
      }
      return sortAsc ? valA - valB : valB - valA;
    });

  const handleSort = (field: string) => {
    if (sortField === field) {
      setSortAsc(!sortAsc);
    } else {
      setSortField(field);
      setSortAsc(false);
    }
  };

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
    <div className="space-y-4">
      
      {/* Filtre ve Arama Çubuğu */}
      <div className="bg-dark-800 border border-slate-800/80 p-3 rounded-md flex flex-col md:flex-row gap-3 items-center justify-between">
        
        {/* Arama Input */}
        <div className="relative w-full md:w-72">
          <Search className="w-3.5 h-3.5 absolute left-3 top-2.5 text-slate-500" />
          <input
            type="text"
            placeholder="Sembol, isim veya sektör..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full bg-dark-900 border border-slate-800 rounded pl-9 pr-3 py-1.5 text-xs text-white placeholder:text-slate-500 focus:outline-none focus:border-blue-500 transition-colors font-mono"
          />
        </div>

        {/* Varlık Sınıfı Butonları */}
        <div className="flex flex-wrap gap-1 w-full md:w-auto">
          {[
            { id: 'ALL', label: 'TÜMÜ' },
            { id: 'BIST_STOCK', label: '🇹🇷 BIST 100' },
            { id: 'US_STOCK', label: '🇺🇸 ABD' },
            { id: 'BANK_STOCK', label: '🏦 BANKA' },
            { id: 'ETF', label: '📊 ETF' },
            { id: 'CRYPTO', label: '🪙 KRİPTO' },
            { id: 'FOREX', label: '💱 FX/EMTİA' }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setSelectedClass(tab.id)}
              className={`px-2.5 py-1.5 rounded text-[11px] font-mono font-medium transition-colors ${
                selectedClass === tab.id
                  ? 'bg-blue-600/20 text-blue-400 border border-blue-500/30 font-semibold'
                  : 'bg-dark-900 text-slate-400 hover:text-slate-200 border border-slate-800/60'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

      </div>

      {/* Varlık Tablosu */}
      <div className="bg-dark-800 border border-slate-800/80 rounded-md overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-dark-900/80 text-slate-500 font-mono text-[10px] border-b border-slate-800 sticky top-0">
              <tr>
                <th className="py-3 px-4 font-medium cursor-pointer hover:text-slate-300" onClick={() => handleSort('symbol')}>
                  <div className="flex items-center gap-1">
                    <span>SEMBOL</span>
                    <ArrowUpDown className="w-3 h-3" />
                  </div>
                </th>
                <th className="py-3 px-4 font-medium cursor-pointer hover:text-slate-300" onClick={() => handleSort('name')}>
                  ŞİRKET / VARLIK ADI
                </th>
                <th className="py-3 px-4 font-medium cursor-pointer hover:text-slate-300" onClick={() => handleSort('sector')}>
                  SEKTÖR
                </th>
                <th className="py-3 px-4 font-medium cursor-pointer hover:text-slate-300" onClick={() => handleSort('composite_score')}>
                  <div className="flex items-center gap-1">
                    <span>BİLEŞİK SKOR (/10)</span>
                    <ArrowUpDown className="w-3 h-3" />
                  </div>
                </th>
                <th className="py-3 px-4 font-medium">TEMEL NOT</th>
                <th className="py-3 px-4 font-medium">SİNYAL</th>
                <th className="py-3 px-4 font-medium">GÜVEN</th>
                <th className="py-3 px-4 font-medium text-right">AKSİYON</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-mono text-xs">
              {loading ? (
                <tr>
                  <td colSpan={8} className="py-12 text-center text-slate-400">
                    <RefreshCw className="w-5 h-5 text-blue-400 animate-spin mx-auto mb-2" />
                    <span>Evren verileri taranıyor...</span>
                  </td>
                </tr>
              ) : filteredAssets.length > 0 ? (
                filteredAssets.map((asset) => {
                  const ratingLetter = asset.fundamental_rating?.rating || (
                    asset.composite_score >= 8.4 ? 'S' :
                    asset.composite_score >= 7.2 ? 'A' :
                    asset.composite_score >= 5.2 ? 'B' :
                    asset.composite_score >= 3.6 ? 'C' : 'D'
                  );
                  return (
                  <tr
                    key={asset.symbol}
                    onClick={() => onSelectAsset(asset.symbol)}
                    className="hover:bg-slate-800/50 transition-colors cursor-pointer group"
                  >
                    <td className="py-2.5 px-4 font-bold text-slate-200 group-hover:text-blue-400">
                      {asset.symbol}
                    </td>
                    <td className="py-2.5 px-4 text-slate-300 font-sans font-medium">
                      {asset.name}
                    </td>
                    <td className="py-2.5 px-4 text-slate-400 font-sans text-[11px]">
                      {asset.sector || '—'}
                    </td>
                    <td className="py-2.5 px-4">
                      {asset.composite_score ? (
                        <div className="flex items-center gap-2">
                          <span className="font-bold text-emerald-400">{asset.composite_score.toFixed(2)}</span>
                          <div className="w-16 h-1.5 bg-dark-900 rounded-full overflow-hidden border border-slate-800">
                            <div
                              className="h-full bg-gradient-to-r from-blue-500 to-emerald-400"
                              style={{ width: `${(asset.composite_score / 10.0) * 100}%` }}
                            />
                          </div>
                        </div>
                      ) : (
                        <span className="text-slate-600">—</span>
                      )}
                    </td>
                    <td className="py-2.5 px-4">
                      {asset.requires_financials !== false ? (
                        <span className={`px-2 py-0.5 rounded text-[11px] font-black font-mono border ${
                          ratingLetter === 'S' ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40' :
                          ratingLetter === 'A' ? 'bg-teal-500/20 text-teal-300 border-teal-500/40' :
                          ratingLetter === 'B' ? 'bg-amber-500/20 text-amber-300 border-amber-500/40' :
                          ratingLetter === 'C' ? 'bg-rose-500/20 text-rose-300 border-rose-500/40' : 'bg-rose-700/30 text-rose-400 border-rose-700/50'
                        }`}>
                          {ratingLetter}
                        </span>
                      ) : (
                        <span className="text-slate-600 text-[10px]">NA</span>
                      )}
                    </td>
                    <td className="py-2.5 px-4">
                      {getSignalBadge(asset.signal)}
                    </td>
                    <td className="py-2.5 px-4">
                      <span className={`text-[10px] font-semibold ${
                        asset.confidence === 'HIGH' ? 'text-emerald-400' :
                        asset.confidence === 'MEDIUM' ? 'text-amber-400' : 'text-slate-500'
                      }`}>
                        {asset.confidence}
                      </span>
                    </td>
                    <td className="py-2.5 px-4 text-right">
                      <button className="inline-flex items-center gap-1 text-slate-500 group-hover:text-blue-400 text-xs">
                        <span>360° İncele</span>
                        <ChevronRight className="w-3.5 h-3.5" />
                      </button>
                    </td>
                  </tr>
                  );
                })
              ) : (
                <tr>
                  <td colSpan={8} className="py-12 text-center text-slate-500 font-mono">
                    Arama kriterine uygun varlık bulunamadı.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

    </div>
  );
};
