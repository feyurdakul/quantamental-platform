import React, { useEffect, useState } from 'react';
import { fetchPortfolio, deletePortfolioPosition } from '../api/client';
import { 
  Trash2, 
  ArrowUpRight, 
  ArrowDownRight, 
  Building2,
  Wallet,
  RefreshCw,
  TrendingUp
} from 'lucide-react';

interface PortfolioProps {
  onSelectAsset: (symbol: string) => void;
  onNavigateToUniverse: () => void;
}

export const Portfolio: React.FC<PortfolioProps> = ({ onSelectAsset, onNavigateToUniverse }) => {
  const [portfolio, setPortfolio] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  const loadPortfolio = async () => {
    try {
      const data = await fetchPortfolio();
      setPortfolio(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadPortfolio();
  }, []);

  const handleDelete = async (symbol: string) => {
    try {
      await deletePortfolioPosition(symbol);
      loadPortfolio();
    } catch (err) {
      console.error(err);
    }
  };

  if (loading && !portfolio) {
    return (
      <div className="flex items-center justify-center min-h-[50vh]">
        <RefreshCw className="w-6 h-6 text-blue-400 animate-spin" />
      </div>
    );
  }

  const positions = portfolio?.positions || [];
  const sectorAllocations = portfolio?.sector_allocation || {};

  return (
    <div className="space-y-5">
      
      {/* Portföy Özet Şeridi (4 Kart) */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3.5">
        
        <div className="bg-dark-800 border border-slate-800/80 p-4 rounded-md">
          <p className="text-[10px] font-mono uppercase text-slate-400 tracking-wider">Portföy Toplam Değeri</p>
          <h3 className="text-xl font-bold text-white mt-1 font-mono">
            {portfolio?.total_value ? `${portfolio.total_value.toLocaleString()} ₺` : '0 ₺'}
          </h3>
          <p className="text-[10px] text-slate-400 mt-0.5 flex items-center gap-1 font-mono">
            <Wallet className="w-3 h-3 text-blue-400" /> {portfolio?.position_count || 0} Aktif Pozisyon
          </p>
        </div>

        <div className="bg-dark-800 border border-slate-800/80 p-4 rounded-md">
          <p className="text-[10px] font-mono uppercase text-slate-400 tracking-wider">Toplam Alış Maliyeti</p>
          <h3 className="text-xl font-bold text-slate-300 mt-1 font-mono">
            {portfolio?.total_cost ? `${portfolio.total_cost.toLocaleString()} ₺` : '0 ₺'}
          </h3>
          <p className="text-[10px] text-slate-500 mt-0.5 font-mono">Ağırlıklı Ortalama Maliyet</p>
        </div>

        <div className="bg-dark-800 border border-slate-800/80 p-4 rounded-md">
          <p className="text-[10px] font-mono uppercase text-slate-400 tracking-wider">Realize Edilmemiş Net K/Z</p>
          <h3 className={`text-xl font-bold mt-1 font-mono flex items-center gap-1 ${
            (portfolio?.total_pnl || 0) >= 0 ? 'text-emerald-400' : 'text-rose-400'
          }`}>
            {(portfolio?.total_pnl || 0) >= 0 ? <ArrowUpRight className="w-5 h-5" /> : <ArrowDownRight className="w-5 h-5" />}
            {portfolio?.total_pnl ? `${portfolio.total_pnl.toLocaleString()} ₺` : '0 ₺'}
          </h3>
          <p className="text-[10px] text-emerald-400/80 mt-0.5 font-mono">
            Getiri: %{portfolio?.total_pnl_percent?.toFixed(2) || '0.00'}
          </p>
        </div>

        <div className="bg-dark-800 border border-slate-800/80 p-4 rounded-md">
          <p className="text-[10px] font-mono uppercase text-slate-400 tracking-wider">Model Portföy Tipi</p>
          <h3 className="text-xl font-bold text-blue-400 mt-1 font-mono">Quantamental</h3>
          <p className="text-[10px] text-slate-400 mt-0.5 font-mono">Temel + Teknik Hibrit Ağırlıklı</p>
        </div>

      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        
        {/* Pozisyon Tablosu (2 Kolon) */}
        <div className="lg:col-span-2 bg-dark-800 border border-slate-800/80 rounded-md p-4 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between pb-3 mb-3 border-b border-slate-800/80">
              <h4 className="font-bold text-xs font-mono uppercase tracking-wider text-slate-100">
                Açık Pozisyonlar ve Ağırlıklar
              </h4>
              <span className="text-[10px] font-mono text-slate-400">
                {positions.length} Pozisyon
              </span>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-slate-800 text-slate-500 font-mono text-[10px]">
                    <th className="pb-2 font-medium">SEMBOL</th>
                    <th className="pb-2 font-medium">GİRİŞ</th>
                    <th className="pb-2 font-medium">GÜNCEL</th>
                    <th className="pb-2 font-medium">AĞIRLIK</th>
                    <th className="pb-2 font-medium">K/Z (%)</th>
                    <th className="pb-2 font-medium">SİNYAL</th>
                    <th className="pb-2 font-medium text-right">SİL</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60 font-mono text-xs">
                  {positions.length > 0 ? (
                    positions.map((pos: any) => (
                      <tr key={pos.symbol} className="hover:bg-slate-800/50 transition-colors">
                        <td 
                          className="py-2.5 font-bold text-slate-200 hover:text-blue-400 cursor-pointer"
                          onClick={() => onSelectAsset(pos.symbol)}
                        >
                          {pos.symbol}
                          <span className="block text-[10px] text-slate-500 font-sans font-normal">{pos.name}</span>
                        </td>
                        <td className="py-2.5 text-slate-400">{pos.entry_price} ₺</td>
                        <td className="py-2.5 font-bold text-white">{pos.current_price} ₺</td>
                        <td className="py-2.5">
                          <span className="text-blue-400 font-bold">%{pos.weight_percent}</span>
                        </td>
                        <td className={`py-2.5 font-bold ${pos.unrealized_pnl >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                          {pos.unrealized_pnl >= 0 ? '+' : ''}{pos.unrealized_pnl_percent}%
                        </td>
                        <td className="py-2.5">
                          <span className="px-1.5 py-0.5 rounded text-[10px] font-semibold bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
                            {pos.signal}
                          </span>
                        </td>
                        <td className="py-2.5 text-right">
                          <button
                            onClick={() => handleDelete(pos.symbol)}
                            className="p-1 rounded text-slate-500 hover:text-rose-400 hover:bg-rose-500/10 transition-colors"
                          >
                            <Trash2 className="w-3.5 h-3.5" />
                          </button>
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan={7} className="py-12 text-center text-slate-500 font-mono text-xs">
                        Portföyde henüz pozisyon yok. <button onClick={onNavigateToUniverse} className="text-blue-400 underline">Varlık Evreni</button>'nden hisse ekleyebilirsiniz.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* Sektör Çeşitlendirme Dağılımı (1 Kolon) */}
        <div className="bg-dark-800 border border-slate-800/80 rounded-md p-4 flex flex-col justify-between">
          <div>
            <div className="flex items-center gap-2 pb-3 mb-3 border-b border-slate-800/80">
              <Building2 className="w-4 h-4 text-blue-400" />
              <h4 className="font-bold text-xs font-mono uppercase tracking-wider text-slate-100">
                Sektör Çeşitlendirmesi
              </h4>
            </div>

            <div className="space-y-2.5 font-mono">
              {Object.entries(sectorAllocations).length > 0 ? (
                Object.entries(sectorAllocations).map(([sector, pct]: [string, any]) => (
                  <div key={sector}>
                    <div className="flex justify-between text-xs mb-1">
                      <span className="text-slate-300 font-sans text-xs">{sector}</span>
                      <span className="text-blue-400 font-bold">%{pct}</span>
                    </div>
                    <div className="w-full h-1 bg-dark-900 rounded-full overflow-hidden border border-slate-800">
                      <div 
                        className="h-full bg-blue-500 rounded-full"
                        style={{ width: `${pct}%` }}
                      />
                    </div>
                  </div>
                ))
              ) : (
                <p className="text-xs text-slate-500 py-6 text-center font-mono">Sektör verisi yok.</p>
              )}
            </div>
          </div>

          <div className="p-3 bg-dark-900 border border-slate-800/80 rounded text-[10px] text-slate-400 font-mono mt-4 leading-relaxed">
            * Konsantrasyon riski kontrolü: Tek bir sektör ağırlığı %30'u geçmemelidir.
          </div>
        </div>

      </div>

    </div>
  );
};
