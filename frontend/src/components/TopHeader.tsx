import React, { useState, useEffect } from 'react';
import { Activity, Clock, RefreshCw } from 'lucide-react';

interface TopHeaderProps {
  activeTab: string;
  scanStatus?: any;
  onRefresh?: () => void;
}

export const TopHeader: React.FC<TopHeaderProps> = ({ activeTab, scanStatus, onRefresh }) => {
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
      case 'dashboard': return 'TERMINAL ÖZETİ & LİDERLİK TABLOLARI';
      case 'universe': return 'VARLIK EVRENİ & KANTİTATİF SCREENER';
      case 'detail': return '360° VARLIK DETAY & DERİNLEMESİNE ANALİZ';
      case 'portfolio': return 'MODEL PORTFÖYÜ & RİSK DAĞILIMI';
      case 'settings': return 'SİSTEM YÖNETİMİ & TARAMA KONTROLÜ';
      default: return 'QUANTAMENTAL TERMINAL';
    }
  };

  const isScanning = scanStatus?.stage === 'SCORING' || scanStatus?.stage === 'FETCHING' || scanStatus?.stage === 'INIT' || scanStatus?.stage === 'BENCHMARKS';
  const progressPct = scanStatus?.total ? Math.round((scanStatus.processed / scanStatus.total) * 100) : 0;

  return (
    <header className="h-14 bg-dark-900/90 backdrop-blur border-b border-slate-800/80 px-6 flex items-center justify-between sticky top-0 z-40">
      
      {/* Sol: Sayfa Başlığı ve Aşama */}
      <div className="flex items-center gap-3">
        <h1 className="text-xs font-mono font-bold tracking-wider text-slate-200">
          {getPageTitle(activeTab)}
        </h1>
      </div>

      {/* Orta: Aktif Tarama Canlı Banner'ı (Tarama Yürütülüyorsa) */}
      {isScanning && (
        <div className="flex items-center gap-3 px-3.5 py-1.5 rounded-md bg-blue-950/40 border border-blue-500/30">
          <RefreshCw className="w-3.5 h-3.5 text-blue-400 animate-spin" />
          <span className="text-[11px] font-mono text-blue-300 font-semibold">
            TARAMA DEVAM EDİYOR: {scanStatus.processed} / {scanStatus.total} (%{progressPct})
          </span>
          <div className="w-20 h-1.5 bg-slate-800 rounded-full overflow-hidden">
            <div className="h-full bg-blue-500 rounded-full" style={{ width: `${progressPct}%` }} />
          </div>
        </div>
      )}

      {/* Sağ: Canlı Saat ve Bağlantı Rozeti */}
      <div className="flex items-center gap-3">
        {onRefresh && (
          <button
            onClick={onRefresh}
            title="Ekranı Yenile"
            className="p-1.5 rounded text-slate-400 hover:text-white hover:bg-slate-800/60 transition-colors"
          >
            <RefreshCw className="w-3.5 h-3.5" />
          </button>
        )}

        <div className="flex items-center gap-1.5 text-xs font-mono text-slate-400">
          <Clock className="w-3.5 h-3.5 text-slate-500" />
          <span>{timeStr}</span>
        </div>

        <div className="flex items-center gap-1.5 px-2.5 py-1 rounded bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-[10px] font-mono font-semibold">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
          <span>SİSTEM ÇEVRİMİÇİ</span>
        </div>
      </div>

    </header>
  );
};
