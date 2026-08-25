import React, { useState, useEffect } from 'react';
import { Clock, RefreshCw, Menu, Cpu } from 'lucide-react';

interface TopHeaderProps {
  activeTab: string;
  scanStatus?: any;
  onRefresh?: () => void;
  onOpenMobileMenu?: () => void;
}

export const TopHeader: React.FC<TopHeaderProps> = ({ 
  activeTab, 
  scanStatus, 
  onRefresh,
  onOpenMobileMenu 
}) => {
  const [timeStr, setTimeStr] = useState('');

  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      setTimeStr(now.toLocaleTimeString('tr-TR', { hour12: false }));
    };
    updateTime();
    const timer = setInterval(updateTime, 1000);
    return () => clearInterval(timer);
  }, []);

  const getPageTitle = (tab: string) => {
    switch (tab) {
      case 'dashboard': return 'TERMINAL ÖZETİ';
      case 'universe': return 'VARLIK EVRENİ & SCREENER';
      case 'detail': return 'VARLIK DETAY ANALİZİ';
      case 'portfolio': return 'MODEL PORTFÖYÜ';
      case 'settings': return 'SİSTEM YÖNETİMİ';
      case 'guide': return 'KULLANIM KILAVUZU';
      default: return 'QUANTAMENTAL';
    }
  };

  const isScanning = scanStatus?.stage === 'SCORING' || scanStatus?.stage === 'FETCHING' || scanStageActive(scanStatus?.stage);
  const progressPct = scanStatus?.total ? Math.round((scanStatus.processed / scanStatus.total) * 100) : 0;

  function scanStageActive(stage?: string) {
    return stage === 'INIT' || stage === 'BENCHMARKS';
  }

  return (
    <header className="h-14 bg-dark-900/90 backdrop-blur border-b border-slate-800/80 px-3 md:px-6 flex items-center justify-between sticky top-0 z-40">
      
      {/* Sol: Hamburger Butonu (Mobil) + Sayfa Başlığı */}
      <div className="flex items-center gap-2.5 min-w-0">
        {onOpenMobileMenu && (
          <button
            onClick={onOpenMobileMenu}
            className="md:hidden p-1.5 rounded-md text-slate-400 hover:text-white hover:bg-slate-800 focus:outline-none"
            aria-label="Menü"
          >
            <Menu className="w-5 h-5 text-blue-400" />
          </button>
        )}

        <div className="flex items-center gap-2 truncate">
          <div className="md:hidden w-6 h-6 rounded bg-blue-600/20 flex items-center justify-center text-blue-400 flex-shrink-0">
            <Cpu className="w-3.5 h-3.5" />
          </div>
          <h1 className="text-xs font-mono font-bold tracking-wider text-slate-200 truncate">
            {getPageTitle(activeTab)}
          </h1>
        </div>
      </div>

      {/* Orta: Aktif Tarama Canlı Banner'ı (Tarama Yürütülüyorsa) */}
      {isScanning && (
        <div className="hidden sm:flex items-center gap-2.5 px-3 py-1 rounded-md bg-blue-950/40 border border-blue-500/30">
          <RefreshCw className="w-3 h-3 text-blue-400 animate-spin flex-shrink-0" />
          <span className="text-[10px] font-mono text-blue-300 font-semibold whitespace-nowrap">
            %{progressPct} ({scanStatus?.processed || 0}/{scanStatus?.total || 601})
          </span>
          <div className="w-16 h-1.5 bg-slate-800 rounded-full overflow-hidden">
            <div className="h-full bg-blue-500 rounded-full" style={{ width: `${progressPct}%` }} />
          </div>
        </div>
      )}

      {/* Sağ: Canlı Saat ve Durum */}
      <div className="flex items-center gap-2 md:gap-3 flex-shrink-0">
        {onRefresh && (
          <button
            onClick={onRefresh}
            title="Ekranı Yenile"
            className="p-1.5 rounded text-slate-400 hover:text-white hover:bg-slate-800/60 transition-colors"
          >
            <RefreshCw className="w-3.5 h-3.5" />
          </button>
        )}

        <div className="hidden sm:flex items-center gap-1.5 text-xs font-mono text-slate-400">
          <Clock className="w-3.5 h-3.5 text-slate-500" />
          <span>{timeStr}</span>
        </div>

        <div className="flex items-center gap-1.5 px-2 py-0.5 md:px-2.5 md:py-1 rounded bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-[10px] font-mono font-semibold">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
          <span className="hidden xs:inline">ONLINE</span>
        </div>
      </div>

    </header>
  );
};
