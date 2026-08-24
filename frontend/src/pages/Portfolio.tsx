import React, { useEffect, useState } from 'react';
import { 
  fetchPortfolio, 
  deletePortfolioPosition, 
  sellPortfolioPosition, 
  addPortfolioPosition,
  triggerPortfolioAutoSync,
  fetchPortfolioTrades
} from '../api/client';
import { 
  Trash2, 
  ArrowUpRight, 
  ArrowDownRight, 
  Building2,
  Wallet,
  RefreshCw,
  TrendingUp,
  Clock,
  CheckCircle2,
  DollarSign,
  PlusCircle,
  History,
  Bot,
  UserCheck,
  X,
  Sparkles
} from 'lucide-react';

interface PortfolioProps {
  onSelectAsset: (symbol: string) => void;
  onNavigateToUniverse: () => void;
}

export const Portfolio: React.FC<PortfolioProps> = ({ onSelectAsset, onNavigateToUniverse }) => {
  const [portfolio, setPortfolio] = useState<any>(null);
  const [trades, setTrades] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);
  const [activeTab, setActiveTab] = useState<'positions' | 'trades'>('positions');

  // Modallar
  const [sellModalPos, setSellModalPos] = useState<any>(null);
  const [sellPercent, setSellPercent] = useState<number>(100);
  const [isSelling, setIsSelling] = useState(false);

  const [addModalOpen, setAddModalOpen] = useState(false);
  const [newSymbol, setNewSymbol] = useState('');
  const [newName, setNewName] = useState('');
  const [newPrice, setNewPrice] = useState<number>(100);
  const [newQty, setNewQty] = useState<number>(100);
  const [newWeight, setNewWeight] = useState<number>(10);
  const [newSector, setNewSector] = useState('Teknoloji');
  const [isAdding, setIsAdding] = useState(false);

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

  const loadTrades = async () => {
    try {
      const tradeList = await fetchPortfolioTrades();
      setTrades(tradeList);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    loadPortfolio();
    loadTrades();
  }, []);

  const handleAutoSync = async () => {
    setSyncing(true);
    try {
      await triggerPortfolioAutoSync();
      await loadPortfolio();
      await loadTrades();
    } catch (err) {
      console.error(err);
    } finally {
      setSyncing(false);
    }
  };

  const handleDelete = async (symbol: string) => {
    try {
      await deletePortfolioPosition(symbol);
      await loadPortfolio();
      await loadTrades();
    } catch (err) {
      console.error(err);
    }
  };

  const handleConfirmSell = async () => {
    if (!sellModalPos) return;
    setIsSelling(true);
    try {
      await sellPortfolioPosition({
        symbol: sellModalPos.symbol,
        sell_percent: sellPercent,
        current_price: sellModalPos.current_price
      });
      setSellModalPos(null);
      await loadPortfolio();
      await loadTrades();
    } catch (err: any) {
      alert(err.message || 'Satış hatası oluştu');
    } finally {
      setIsSelling(false);
    }
  };

  const handleConfirmAdd = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newSymbol) return;
    setIsAdding(true);
    try {
      await addPortfolioPosition({
        symbol: newSymbol.toUpperCase(),
        name: newName || newSymbol.toUpperCase(),
        entry_price: Number(newPrice),
        quantity: Number(newQty),
        target_weight_percent: Number(newWeight),
        sector: newSector,
        is_auto_managed: false
      });
      setAddModalOpen(false);
      setNewSymbol('');
      setNewName('');
      await loadPortfolio();
      await loadTrades();
    } catch (err: any) {
      alert(err.message || 'Ekleme hatası oluştu');
    } finally {
      setIsAdding(false);
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
    <div className="space-y-5 font-sans">
      
      {/* Üst Yönetim ve Aksiyon Çubuğu */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 bg-dark-800/80 border border-slate-800/80 p-3.5 rounded-md">
        <div className="flex items-center gap-2">
          <button
            onClick={() => setActiveTab('positions')}
            className={`px-3 py-1.5 rounded text-xs font-mono font-bold transition-colors flex items-center gap-1.5 ${
              activeTab === 'positions'
                ? 'bg-blue-600/20 text-blue-400 border border-blue-500/30'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Wallet className="w-3.5 h-3.5" />
            <span>Aktif Pozisyonlar ({positions.length})</span>
          </button>

          <button
            onClick={() => { setActiveTab('trades'); loadTrades(); }}
            className={`px-3 py-1.5 rounded text-xs font-mono font-bold transition-colors flex items-center gap-1.5 ${
              activeTab === 'trades'
                ? 'bg-blue-600/20 text-blue-400 border border-blue-500/30'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <History className="w-3.5 h-3.5" />
            <span>İşlem Geçmişi ({trades.length})</span>
          </button>
        </div>

        <div className="flex items-center gap-2 w-full sm:w-auto">
          <button
            onClick={handleAutoSync}
            disabled={syncing}
            className="flex-1 sm:flex-none px-3 py-1.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 hover:bg-emerald-500/20 text-xs font-mono font-semibold flex items-center justify-center gap-1.5 transition-colors disabled:opacity-50"
          >
            <Sparkles className={`w-3.5 h-3.5 ${syncing ? 'animate-spin' : ''}`} />
            <span>{syncing ? 'Senkronize Ediliyor...' : 'Sinyalleri Otomatik Senkronize Et'}</span>
          </button>

          <button
            onClick={() => setAddModalOpen(true)}
            className="flex-1 sm:flex-none px-3 py-1.5 rounded bg-blue-600 hover:bg-blue-500 text-white text-xs font-mono font-semibold flex items-center justify-center gap-1.5 transition-colors shadow-sm"
          >
            <PlusCircle className="w-3.5 h-3.5" />
            <span>Pozisyon Ekle</span>
          </button>
        </div>
      </div>

      {/* Portföy Özet Şeridi (4 Kart) */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3.5">
        
        <div className="bg-dark-800 border border-slate-800/80 p-4 rounded-md">
          <p className="text-[10px] font-mono uppercase text-slate-400 tracking-wider">Portföy Toplam Değeri</p>
          <h3 className="text-xl font-bold text-white mt-1 font-mono">
            {portfolio?.total_value ? `${portfolio.total_value.toLocaleString()} ₺` : '0 ₺'}
          </h3>
          <p className="text-[10px] text-slate-400 mt-0.5 flex items-center gap-1 font-mono">
            <Wallet className="w-3 h-3 text-blue-400" /> {portfolio?.position_count || 0} Aktif Hisse
          </p>
        </div>

        <div className="bg-dark-800 border border-slate-800/80 p-4 rounded-md">
          <p className="text-[10px] font-mono uppercase text-slate-400 tracking-wider">Toplam Alış Maliyeti</p>
          <h3 className="text-xl font-bold text-slate-300 mt-1 font-mono">
            {portfolio?.total_cost ? `${portfolio.total_cost.toLocaleString()} ₺` : '0 ₺'}
          </h3>
          <p className="text-[10px] text-slate-500 mt-0.5 font-mono">Kalıcı Supabase Depolu</p>
        </div>

        <div className="bg-dark-800 border border-slate-800/80 p-4 rounded-md">
          <p className="text-[10px] font-mono uppercase text-slate-400 tracking-wider">Realize Edilmemiş Net K/Z</p>
          <h3 className={`text-xl font-bold mt-1 font-mono flex items-center gap-1 ${
            (portfolio?.total_pnl || 0) >= 0 ? 'text-emerald-400' : 'text-rose-400'
          }`}>
            {(portfolio?.total_pnl || 0) >= 0 ? <ArrowUpRight className="w-5 h-5" /> : <ArrowDownRight className="w-5 h-5" />}
            {portfolio?.total_pnl ? `${portfolio.total_pnl.toLocaleString()} ₺` : '0 ₺'}
          </h3>
          <p className="text-[10px] text-emerald-400/80 mt-0.5 font-mono font-bold">
            Getiri: %{portfolio?.total_pnl_percent?.toFixed(2) || '0.00'}
          </p>
        </div>

        <div className="bg-dark-800 border border-slate-800/80 p-4 rounded-md">
          <p className="text-[10px] font-mono uppercase text-slate-400 tracking-wider">Alım Kuralı Dağılımı</p>
          <h3 className="text-sm font-bold text-blue-400 mt-1 font-mono">Strong Buy: %8-10 | Buy: %5-8</h3>
          <p className="text-[10px] text-slate-400 mt-0.5 font-mono">Sat Sinyalinde Otomatik Çıkış</p>
        </div>

      </div>

      {activeTab === 'positions' ? (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          
          {/* Pozisyon Tablosu (2 Kolon) */}
          <div className="lg:col-span-2 bg-dark-800 border border-slate-800/80 rounded-md p-4 flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between pb-3 mb-3 border-b border-slate-800/80">
                <h4 className="font-bold text-xs font-mono uppercase tracking-wider text-slate-100 flex items-center gap-2">
                  <TrendingUp className="w-4 h-4 text-emerald-400" />
                  <span>Açık Pozisyonlar & Elde Tutma Süreleri</span>
                </h4>
                <span className="text-[10px] font-mono text-slate-400">
                  {positions.length} Pozisyon
                </span>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead>
                    <tr className="border-b border-slate-800 text-slate-500 font-mono text-[10px]">
                      <th className="pb-2 font-medium">SEMBOL & İSİM</th>
                      <th className="pb-2 font-medium">GİRİŞ & SÜRE</th>
                      <th className="pb-2 font-medium">FİYAT (ALIŞ / GÜNCEL)</th>
                      <th className="pb-2 font-medium">ADET</th>
                      <th className="pb-2 font-medium">AĞIRLIK</th>
                      <th className="pb-2 font-medium">K/Z (%)</th>
                      <th className="pb-2 font-medium">SİNYAL</th>
                      <th className="pb-2 font-medium text-right">İŞLEMLER</th>
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
                            <div className="flex items-center gap-1.5">
                              <span>{pos.symbol}</span>
                              {pos.is_auto_managed ? (
                                <span title="Otomatik Sinyalle Eklendi" className="px-1 py-0.2 rounded text-[9px] bg-purple-500/20 text-purple-300 border border-purple-500/30 flex items-center gap-0.5">
                                  <Bot className="w-2.5 h-2.5" /> Oto
                                </span>
                              ) : (
                                <span title="Manuel Eklendi" className="px-1 py-0.2 rounded text-[9px] bg-slate-700/50 text-slate-400 border border-slate-600/30 flex items-center gap-0.5">
                                  <UserCheck className="w-2.5 h-2.5" /> Manuel
                                </span>
                              )}
                            </div>
                            <span className="block text-[10px] text-slate-500 font-sans font-normal truncate max-w-[120px]">{pos.name}</span>
                          </td>

                          <td className="py-2.5 text-slate-400">
                            <span className="text-[11px] text-slate-300 font-medium">{pos.holding_duration || 'Bugün'}</span>
                            <span className="block text-[9px] text-slate-500">{pos.entry_date}</span>
                          </td>

                          <td className="py-2.5">
                            <span className="text-slate-400 text-[11px]">{pos.entry_price} ₺</span>
                            <span className="text-slate-600 mx-1">→</span>
                            <span className="font-bold text-white text-[11px]">{pos.current_price} ₺</span>
                          </td>

                          <td className="py-2.5 text-slate-300">
                            {pos.quantity} Lot
                          </td>

                          <td className="py-2.5">
                            <div className="flex items-center gap-1.5">
                              <span className="text-blue-400 font-bold">%{pos.weight_percent}</span>
                              <span className="text-[9px] text-slate-500">(Hedef %{pos.target_weight_percent || 10})</span>
                            </div>
                          </td>

                          <td className={`py-2.5 font-bold ${pos.unrealized_pnl >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                            {pos.unrealized_pnl >= 0 ? '+' : ''}{pos.unrealized_pnl_percent}%
                            <span className="block text-[9px] font-normal opacity-80">
                              {pos.unrealized_pnl >= 0 ? '+' : ''}{Math.round(pos.unrealized_pnl)} ₺
                            </span>
                          </td>

                          <td className="py-2.5">
                            <span className={`px-1.5 py-0.5 rounded text-[10px] font-semibold border ${
                              pos.signal === 'STRONG_BUY' ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40' :
                              pos.signal === 'BUY' ? 'bg-teal-500/20 text-teal-300 border-teal-500/40' :
                              pos.signal === 'HOLD' ? 'bg-amber-500/20 text-amber-300 border-amber-500/40' :
                              'bg-rose-500/20 text-rose-300 border-rose-500/40'
                            }`}>
                              {pos.signal}
                            </span>
                          </td>

                          <td className="py-2.5 text-right">
                            <div className="flex items-center justify-end gap-1.5">
                              <button
                                onClick={() => { setSellModalPos(pos); setSellPercent(100); }}
                                className="px-2 py-1 rounded bg-amber-500/10 text-amber-400 hover:bg-amber-500/20 border border-amber-500/30 text-[10px] font-bold font-mono transition-colors"
                              >
                                SAT
                              </button>
                              <button
                                onClick={() => handleDelete(pos.symbol)}
                                title="Portföyden Sil"
                                className="p-1 rounded text-slate-500 hover:text-rose-400 hover:bg-rose-500/10 transition-colors"
                              >
                                <Trash2 className="w-3.5 h-3.5" />
                              </button>
                            </div>
                          </td>
                        </tr>
                      ))
                    ) : (
                      <tr>
                        <td colSpan={8} className="py-12 text-center text-slate-500 font-mono text-xs">
                          Portföyde henüz pozisyon yok. Otomatik senkronizasyon yapabilir veya <button onClick={onNavigateToUniverse} className="text-blue-400 underline">Varlık Evreni</button>'nden ekleyebilirsiniz.
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
              * Risk Yönetimi: Strong Buy hisseleri %8-10, Buy hisseleri %5-8 ağırlıkla tutulur. Sat sinyalinde otomatik kapatılır.
            </div>
          </div>

        </div>
      ) : (
        /* İşlem Geçmişi (Trades) Tablosu */
        <div className="bg-dark-800 border border-slate-800/80 rounded-md p-4">
          <div className="flex items-center justify-between pb-3 mb-3 border-b border-slate-800/80">
            <h4 className="font-bold text-xs font-mono uppercase tracking-wider text-slate-100 flex items-center gap-2">
              <History className="w-4 h-4 text-blue-400" />
              <span>Gerçekleşen Alım & Satım İşlemleri</span>
            </h4>
            <span className="text-[10px] font-mono text-slate-400">
              Son {trades.length} İşlem
            </span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-slate-800 text-slate-500 font-mono text-[10px]">
                  <th className="pb-2 font-medium">TARİH & SAAT</th>
                  <th className="pb-2 font-medium">SEMBOL</th>
                  <th className="pb-2 font-medium">İŞLEM TİPİ</th>
                  <th className="pb-2 font-medium">FİYAT</th>
                  <th className="pb-2 font-medium">MİKTAR</th>
                  <th className="pb-2 font-medium">TOPLAM TUTAR</th>
                  <th className="pb-2 font-medium">REALİZE EDİLEN K/Z</th>
                  <th className="pb-2 font-medium">AÇIKLAMA</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-mono text-xs">
                {trades.length > 0 ? (
                  trades.map((t: any) => (
                    <tr key={t.id} className="hover:bg-slate-800/50 transition-colors">
                      <td className="py-2.5 text-slate-400">{t.created_at?.slice(0, 16).replace('T', ' ')}</td>
                      <td className="py-2.5 font-bold text-slate-200">{t.symbol}</td>
                      <td className="py-2.5">
                        <span className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${
                          t.action.includes('BUY') ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30' : 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                        }`}>
                          {t.action}
                        </span>
                      </td>
                      <td className="py-2.5 text-slate-300">{t.price} ₺</td>
                      <td className="py-2.5 text-slate-400">{t.quantity} Lot</td>
                      <td className="py-2.5 font-bold text-white">{Math.round(t.total_amount).toLocaleString()} ₺</td>
                      <td className={`py-2.5 font-bold ${t.realized_pnl > 0 ? 'text-emerald-400' : t.realized_pnl < 0 ? 'text-rose-400' : 'text-slate-400'}`}>
                        {t.realized_pnl > 0 ? '+' : ''}{Math.round(t.realized_pnl).toLocaleString()} ₺
                      </td>
                      <td className="py-2.5 text-slate-400 text-[11px] font-sans">{t.reason || '—'}</td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={8} className="py-10 text-center text-slate-500 font-mono text-xs">
                      Henüz kayıtlı alım/satım işlemi bulunmuyor.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* KISMİ / TAM SATIŞ MODALI */}
      {sellModalPos && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
          <div className="bg-dark-800 border border-slate-700 rounded-lg max-w-md w-full p-5 space-y-4 shadow-2xl">
            <div className="flex items-center justify-between pb-3 border-b border-slate-700">
              <div className="flex items-center gap-2">
                <DollarSign className="w-5 h-5 text-amber-400" />
                <h3 className="font-bold text-sm text-white font-mono">
                  Pozisyon Satışı & Kâr Realizasyonu
                </h3>
              </div>
              <button onClick={() => setSellModalPos(null)} className="text-slate-400 hover:text-white">
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="space-y-3 font-mono text-xs">
              <div className="p-3 bg-dark-900 rounded border border-slate-800 space-y-1.5">
                <div className="flex justify-between">
                  <span className="text-slate-400">Varlık Sembolü:</span>
                  <span className="font-bold text-white">{sellModalPos.symbol} ({sellModalPos.name})</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Alış Fiyatı / Güncel Fiyat:</span>
                  <span>{sellModalPos.entry_price} ₺ / <strong className="text-emerald-400">{sellModalPos.current_price} ₺</strong></span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Mevcut Miktar:</span>
                  <span className="text-slate-200">{sellModalPos.quantity} Lot</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Realize Edilmemiş K/Z:</span>
                  <span className={`font-bold ${sellModalPos.unrealized_pnl >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                    %{sellModalPos.unrealized_pnl_percent} ({sellModalPos.unrealized_pnl} ₺)
                  </span>
                </div>
              </div>

              {/* Satış Yüzdesi Seçici */}
              <div className="space-y-1.5">
                <label className="text-slate-300 font-semibold block">Satılacak Oran / Miktar:</label>
                <div className="grid grid-cols-4 gap-2">
                  {[25, 50, 75, 100].map((pct) => (
                    <button
                      key={pct}
                      type="button"
                      onClick={() => setSellPercent(pct)}
                      className={`py-2 rounded font-bold transition-colors ${
                        sellPercent === pct
                          ? 'bg-amber-500 text-black border border-amber-400'
                          : 'bg-dark-900 text-slate-300 border border-slate-700 hover:border-slate-500'
                      }`}
                    >
                      %{pct}
                    </button>
                  ))}
                </div>
              </div>

              {/* Tahmini Satış Özeti */}
              <div className="p-3 bg-amber-500/10 border border-amber-500/30 rounded text-[11px] space-y-1">
                <div className="flex justify-between">
                  <span className="text-slate-300">Satılacak Lot:</span>
                  <strong className="text-white">{(sellModalPos.quantity * (sellPercent / 100)).toFixed(1)} Lot</strong>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-300">Kalan Lot:</span>
                  <span className="text-slate-300">{(sellModalPos.quantity * (1 - sellPercent / 100)).toFixed(1)} Lot</span>
                </div>
                <div className="flex justify-between pt-1 border-t border-amber-500/20">
                  <span className="text-amber-300 font-semibold">Realize Edilecek Net Kâr:</span>
                  <strong className="text-emerald-400">
                    +{Math.round((sellModalPos.current_price - sellModalPos.entry_price) * (sellModalPos.quantity * (sellPercent / 100)))} ₺
                  </strong>
                </div>
              </div>
            </div>

            <div className="flex gap-2 pt-2">
              <button
                type="button"
                onClick={() => setSellModalPos(null)}
                className="flex-1 py-2 rounded bg-dark-900 text-slate-300 border border-slate-700 text-xs font-mono hover:bg-slate-800"
              >
                İptal
              </button>
              <button
                type="button"
                onClick={handleConfirmSell}
                disabled={isSelling}
                className="flex-1 py-2 rounded bg-amber-500 hover:bg-amber-400 text-black font-bold text-xs font-mono transition-colors disabled:opacity-50"
              >
                {isSelling ? 'Satılıyor...' : `%${sellPercent} Satışı Onayla`}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* MANUEL POZİSYON EKLEME MODALI */}
      {addModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
          <form onSubmit={handleConfirmAdd} className="bg-dark-800 border border-slate-700 rounded-lg max-w-md w-full p-5 space-y-4 shadow-2xl">
            <div className="flex items-center justify-between pb-3 border-b border-slate-700">
              <div className="flex items-center gap-2">
                <PlusCircle className="w-5 h-5 text-blue-400" />
                <h3 className="font-bold text-sm text-white font-mono">
                  Portföye Yeni Hisse Ekle
                </h3>
              </div>
              <button type="button" onClick={() => setAddModalOpen(false)} className="text-slate-400 hover:text-white">
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="space-y-3 font-mono text-xs">
              <div>
                <label className="text-slate-300 block mb-1">Hisse Sembolü (Örn: BIST:THYAO veya ASELS):</label>
                <input
                  type="text"
                  required
                  placeholder="BIST:THYAO"
                  value={newSymbol}
                  onChange={(e) => setNewSymbol(e.target.value)}
                  className="w-full bg-dark-900 border border-slate-700 rounded p-2 text-white focus:outline-none focus:border-blue-500"
                />
              </div>

              <div>
                <label className="text-slate-300 block mb-1">Şirket Adı (Opsiyonel):</label>
                <input
                  type="text"
                  placeholder="Türk Hava Yolları"
                  value={newName}
                  onChange={(e) => setNewName(e.target.value)}
                  className="w-full bg-dark-900 border border-slate-700 rounded p-2 text-white focus:outline-none focus:border-blue-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-slate-300 block mb-1">Alış Fiyatı (₺):</label>
                  <input
                    type="number"
                    step="0.01"
                    required
                    value={newPrice}
                    onChange={(e) => setNewPrice(Number(e.target.value))}
                    className="w-full bg-dark-900 border border-slate-700 rounded p-2 text-white focus:outline-none focus:border-blue-500"
                  />
                </div>

                <div>
                  <label className="text-slate-300 block mb-1">Lot / Miktar:</label>
                  <input
                    type="number"
                    step="1"
                    required
                    value={newQty}
                    onChange={(e) => setNewQty(Number(e.target.value))}
                    className="w-full bg-dark-900 border border-slate-700 rounded p-2 text-white focus:outline-none focus:border-blue-500"
                  />
                </div>
              </div>

              {/* Hedef Portföy Ağırlığı */}
              <div>
                <label className="text-slate-300 block mb-1.5 font-semibold">Hedef Portföy Ağırlığı (%):</label>
                <div className="grid grid-cols-3 gap-2 mb-2">
                  {[
                    { label: 'Strong Buy (%10)', val: 10 },
                    { label: 'Buy (%7)', val: 7 },
                    { label: 'Standart (%5)', val: 5 }
                  ].map((btn) => (
                    <button
                      key={btn.val}
                      type="button"
                      onClick={() => setNewWeight(btn.val)}
                      className={`py-1.5 rounded text-[11px] font-bold transition-colors ${
                        newWeight === btn.val
                          ? 'bg-blue-600 text-white border border-blue-400'
                          : 'bg-dark-900 text-slate-300 border border-slate-700'
                      }`}
                    >
                      {btn.label}
                    </button>
                  ))}
                </div>
                <input
                  type="number"
                  step="0.5"
                  value={newWeight}
                  onChange={(e) => setNewWeight(Number(e.target.value))}
                  className="w-full bg-dark-900 border border-slate-700 rounded p-2 text-white focus:outline-none focus:border-blue-500"
                  placeholder="Özel Yüzde Girişi (%)"
                />
              </div>
            </div>

            <div className="flex gap-2 pt-2">
              <button
                type="button"
                onClick={() => setAddModalOpen(false)}
                className="flex-1 py-2 rounded bg-dark-900 text-slate-300 border border-slate-700 text-xs font-mono hover:bg-slate-800"
              >
                İptal
              </button>
              <button
                type="submit"
                disabled={isAdding}
                className="flex-1 py-2 rounded bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs font-mono transition-colors disabled:opacity-50"
              >
                {isAdding ? 'Ekleniyor...' : 'Portföye Ekle'}
              </button>
            </div>
          </form>
        </div>
      )}

    </div>
  );
};

