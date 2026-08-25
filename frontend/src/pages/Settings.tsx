import React, { useEffect, useState } from 'react';
import { triggerScan, fetchScanStatus, fetchDashboardSummary, fetchSchedulerStatus, triggerSchedulerNow, reloadCache } from '../api/client';
import { 
  Play, 
  RefreshCw, 
  CheckCircle2, 
  AlertCircle, 
  Server, 
  Zap, 
  Clock,
  Cpu,
  Layers,
  Database,
  Radio,
  Calendar
} from 'lucide-react';

interface SettingsProps {
  onRefreshAll?: () => void;
}

export const Settings: React.FC<SettingsProps> = ({ onRefreshAll }) => {
  const [status, setStatus] = useState<any>(null);
  const [scheduler, setScheduler] = useState<any>(null);
  const [scanning, setScanning] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [backendError, setBackendError] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  const loadStatus = async () => {
    try {
      const data = await fetchScanStatus();
      setStatus(data);
      setBackendError(false);
      if (data.stage === 'SCORING' || data.stage === 'FETCHING' || data.stage === 'INIT' || data.stage === 'BENCHMARKS') {
        setScanning(true);
      } else {
        setScanning(false);
      }
    } catch (err) {
      setBackendError(true);
      setScanning(false);
    }
  };

  const loadScheduler = async () => {
    try {
      const s = await fetchSchedulerStatus();
      setScheduler(s);
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    loadStatus();
    loadScheduler();
    const interval = setInterval(() => {
      loadStatus();
      loadScheduler();
    }, 3000);
    return () => clearInterval(interval);
  }, []);

  // 1. TARAMAYI BAŞLAT: Yalnızca scan endpoint'ini çağırır
  const handleStartScan = async () => {
    setScanning(true);
    setMessage('Tarama başlatılıyor...');
    try {
      const res = await triggerScan();
      setMessage('Tarama başlatıldı. İlerleme işleniyor...');
      if (res && res.total_assets) {
        setStatus((prev: any) => ({
          ...(prev || {}),
          stage: 'SCORING',
          total: res.total_assets,
          processed: 0,
          failed: 0
        }));
      }
      setTimeout(loadStatus, 400);
    } catch (err: any) {
      setMessage(`Tarama hatası: ${err.message}`);
      setScanning(false);
    }
  };

  // 2. EKRANI GÜNCELLE: Veritabanındaki tüm 601 skoru anında yükler (10ms)
  const handleRefreshUI = async () => {
    setRefreshing(true);
    setMessage('Veritabanından 601 varlık yükleniyor...');
    try {
      await reloadCache();
      await Promise.all([fetchDashboardSummary(), loadStatus()]);
      if (onRefreshAll) onRefreshAll();
      setMessage('Tüm ekran verileri ve 601 varlık başarıyla güncellendi!');
      setTimeout(() => setMessage(null), 3000);
    } catch (err: any) {
      setMessage('Veri tazelenirken hata oluştu.');
    } finally {
      setRefreshing(false);
    }
  };

  // Görsel Sözleşme Metin Eşlemesi
  const getStatusDisplay = () => {
    if (backendError) return { text: 'TARAMA DURUMU ALINAMADI', color: 'text-rose-400', badge: 'bg-rose-500/10 border-rose-500/30' };
    if (!status) return { text: 'HAZIR / BEKLEMEDE', color: 'text-slate-400', badge: 'bg-slate-800 border-slate-700' };

    switch (status.stage) {
      case 'INIT':
        return { text: 'HAZIRLANIYOR', color: 'text-blue-400', badge: 'bg-blue-500/10 border-blue-500/30' };
      case 'FETCHING':
      case 'SCORING':
        return { text: 'TARAMA DEVAM EDİYOR', color: 'text-blue-400', badge: 'bg-blue-500/10 border-blue-500/30' };
      case 'BENCHMARKS':
        return { text: 'SONUÇLAR HESAPLANIYOR', color: 'text-purple-400', badge: 'bg-purple-500/10 border-purple-500/30' };
      case 'COMPLETED':
        return { text: 'TARAMA TAMAMLANDI', color: 'text-emerald-400', badge: 'bg-emerald-500/10 border-emerald-500/30' };
      case 'FAILED':
        return { text: 'TARAMA HATASI', color: 'text-rose-400', badge: 'bg-rose-500/10 border-rose-500/30' };
      default:
        return { text: 'HAZIR / BEKLEMEDE', color: 'text-slate-400', badge: 'bg-slate-800 border-slate-700' };
    }
  };

  const statusInfo = getStatusDisplay();
  const isCompleted = status?.stage === 'COMPLETED';
  const progressPercent = status?.total ? Math.min(100, Math.round((status.processed / status.total) * 100)) : (isCompleted ? 100 : 0);

  const providers = [
    { name: 'isyatirimhisse v5.0.1', desc: 'BIST Resmi KAP/UFRS Bilançoları & TMS-29 USD Bilanço', status: 'Online', badge: 'BIST Temel' },
    { name: 'yfinance', desc: 'BIST & US Bölünme/Temettü Düzeltmeli Adj Close & Tedavüldeki Hisse', status: 'Online', badge: 'Fiyat/Kurumsal' },
    { name: 'Financial Modeling Prep (FMP)', desc: 'ABD GAAP Standartlaştırılmış 3 Tablo & Firma Değeri (EV)', status: 'Online', badge: 'US Bilanço' },
    { name: 'Finnhub API', desc: 'Wall Street Hedef Fiyatları, Analist Tavsiyeleri & EPS Sürprizleri', status: 'Online', badge: 'Analist/Tahmin' },
    { name: 'Google Finance REST API', desc: 'Şirket Künyesi (CEO, Sektör, 52W Aralık), Haberler & SSE Canlı Akış', status: 'Online', badge: 'Profil/Canlı' },
    { name: '@mathieuc/tradingview', desc: 'Milisaniyelik Canlı WebSocket OHLCV & Pine Script İndikatörleri', status: 'Online', badge: 'Canlı Mumlar' },
    { name: 'fredapi (St. Louis Fed)', desc: 'TÜFE, Faizler, Likidite & ALFRED Point-in-Time Revizyon Verileri', status: 'Online', badge: 'Makro/Revizyon' },
  ];

  return (
    <div className="space-y-4 md:space-y-5 max-w-5xl">
      
      {/* Yan Yana 2 Aksiyon Kartı: TARAMAYI BAŞLAT ve EKRANI GÜNCELLE */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3 md:gap-4">
        
        {/* Kart 1: TARAMAYI BAŞLAT */}
        <div className="bg-dark-800 border border-slate-800/80 p-3.5 md:p-5 rounded-md flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-[9px] md:text-[10px] font-mono px-2 py-0.5 rounded bg-blue-600/20 text-blue-400 border border-blue-500/30 font-semibold">
                MOTOR KONTROLÜ
              </span>
              <span className="text-xs font-mono text-slate-500">{status?.total || 601} Varlık</span>
            </div>
            <h3 className="text-sm md:text-base font-bold text-white font-mono">TARAMAYI BAŞLAT</h3>
            <p className="text-xs text-slate-400 mt-1 leading-relaxed">
              Arka planda tüm 7 veri sağlayıcıdan güncel fiyat ve tabloları çekerek 10'luk skorları ve liderlik listelerini baştan hesaplar.
            </p>
          </div>

          <button
            onClick={handleStartScan}
            disabled={scanning}
            className={`mt-4 w-full flex items-center justify-center gap-2 py-2.5 rounded text-xs font-bold font-mono transition-colors ${
              scanning
                ? 'bg-blue-900/50 text-blue-300/50 border border-blue-800 cursor-not-allowed'
                : 'bg-blue-600 hover:bg-blue-500 text-white shadow-sm'
            }`}
          >
            {scanning ? (
              <>
                <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                <span>TARAMA YÜRÜTÜLÜYOR...</span>
              </>
            ) : (
              <>
                <Play className="w-3.5 h-3.5 fill-current" />
                <span>TAM TARAMAYI BAŞLAT</span>
              </>
            )}
          </button>
        </div>

        {/* Kart 2: EKRANI GÜNCELLE */}
        <div className="bg-dark-800 border border-slate-800/80 p-3.5 md:p-5 rounded-md flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-[9px] md:text-[10px] font-mono px-2 py-0.5 rounded bg-slate-700/50 text-slate-300 border border-slate-600/50 font-semibold">
                ARAYÜZ TAZELENMESİ
              </span>
              <span className="text-xs font-mono text-slate-500">Salt Okunur</span>
            </div>
            <h3 className="text-sm md:text-base font-bold text-white font-mono">EKRANI GÜNCELLE</h3>
            <p className="text-xs text-slate-400 mt-1 leading-relaxed">
              Arayüz verilerini ve son hesaplanmış veritabanı skorlarını yeniden okur. Dış sağlayıcı çağrısı yapmaz ve tarama başlatmaz.
            </p>
          </div>

          <button
            onClick={handleRefreshUI}
            disabled={refreshing}
            className={`mt-4 w-full flex items-center justify-center gap-2 py-2.5 rounded text-xs font-bold font-mono transition-colors ${
              refreshing
                ? 'bg-slate-800 text-slate-500 border border-slate-700 cursor-not-allowed'
                : 'bg-dark-900 hover:bg-slate-800 text-slate-200 border border-slate-700'
            }`}
          >
            <RefreshCw className={`w-3.5 h-3.5 ${refreshing ? 'animate-spin' : ''}`} />
            <span>{refreshing ? 'GÜNCELLENİYOR...' : 'EKRANI GÜNCELLE'}</span>
          </button>
        </div>

      </div>

      {/* Tarama Durumu ve Dürüst İlerleme Paneli */}
      <div className="bg-dark-800 border border-slate-800/80 p-3.5 md:p-5 rounded-md space-y-4">
        <div className="flex items-center justify-between border-b border-slate-800/80 pb-3">
          <div className="flex items-center gap-2">
            <Server className="w-4 h-4 text-blue-400" />
            <h4 className="font-bold text-xs font-mono uppercase tracking-wider text-slate-100">
              Tarama Döngüsü & Aşama Takibi
            </h4>
          </div>

          <div className={`px-2.5 py-1 rounded text-xs font-mono font-bold border ${statusInfo.badge} ${statusInfo.color}`}>
            {statusInfo.text}
          </div>
        </div>

        {/* İlerleme Çubuğu */}
        <div>
          <div className="flex justify-between items-center text-xs font-mono mb-1.5 flex-wrap gap-1">
            <span className="text-slate-400">
              İlerleme: <strong className={isCompleted ? "text-emerald-400" : "text-white"}>%{progressPercent}</strong>
            </span>
            <span className="text-slate-400">
              İşlenen: <strong className="text-white">{status?.processed || (isCompleted ? status?.total || 601 : 0)}</strong> / {status?.total || 601}
              <span className="text-slate-500 ml-1.5">(Hata: {status?.failed || 0})</span>
            </span>
          </div>

          <div className="w-full h-2 bg-dark-900 rounded-full overflow-hidden border border-slate-800">
            <div
              className={`h-full transition-all duration-300 rounded-full ${isCompleted ? 'bg-emerald-500' : 'bg-blue-500'}`}
              style={{ width: `${progressPercent}%` }}
            />
          </div>

          <div className="mt-3 flex justify-between text-[10px] md:text-[11px] font-mono text-slate-500 flex-wrap gap-1">
            <span>Aşama Kodu: {status?.stage || 'IDLE'}</span>
            <span>Son Güncelleme: {status?.completed_at ? new Date(status.completed_at).toLocaleTimeString('tr-TR') : 'Hazır'}</span>
          </div>

          {message && (
            <p className="text-xs font-mono text-blue-400 mt-2 bg-blue-950/20 p-2 rounded border border-blue-900/30">
              {message}
            </p>
          )}
        </div>
      </div>

      {/* Gece 01:30 TR Otomatik Cron Zamanlayıcısı Kartı */}
      <div className="bg-dark-800 border border-emerald-900/40 p-5 rounded-md space-y-3 font-mono text-xs">
        <div className="flex items-center justify-between border-b border-slate-800/80 pb-3">
          <div className="flex items-center gap-2">
            <Clock className="w-4 h-4 text-emerald-400" />
            <h4 className="font-bold text-xs uppercase tracking-wider text-slate-100">
              Otomatik Gece Taraması (Cron Scheduler — 01:30 TR)
            </h4>
          </div>
          <span className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-300 font-bold border border-emerald-500/30 text-[10px]">
            {scheduler?.is_active ? '● AKTİF ÇALIŞIYOR' : '○ DEVRE DIŞI'}
          </span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-1">
          <div className="bg-dark-900 p-3 rounded border border-slate-800">
            <span className="text-[10px] text-slate-400 block">HEDEF ZAMAN ÇİZELGESİ</span>
            <span className="text-white font-bold text-sm block mt-1">Her Gece 01:30 (UTC+3)</span>
            <span className="text-[10px] text-slate-500 mt-0.5 block">Otomatik fiyat ve skor güncellemesi</span>
          </div>

          <div className="bg-dark-900 p-3 rounded border border-slate-800">
            <span className="text-[10px] text-slate-400 block">SONRAKİ OTOMATİK ÇALIŞMA</span>
            <span className="text-emerald-400 font-bold text-sm block mt-1">
              {scheduler?.next_run_at_tr || 'Hesaplanıyor...'}
            </span>
            <span className="text-[10px] text-slate-400 mt-0.5 block">
              {scheduler?.seconds_until_next_run ? `Kalan: ${Math.floor(scheduler.seconds_until_next_run / 3600)} sa ${Math.floor((scheduler.seconds_until_next_run % 3600) / 60)} dk` : '—'}
            </span>
          </div>

          <div className="bg-dark-900 p-3 rounded border border-slate-800">
            <span className="text-[10px] text-slate-400 block">SON OTOMATİK ÇALIŞMA</span>
            <span className="text-white font-bold text-sm block mt-1">
              {scheduler?.last_run_at_tr || 'Henüz Tetiklenmedi'}
            </span>
            <span className="text-[10px] text-emerald-400 mt-0.5 block">
              Toplam Başarılı Tur: {scheduler?.total_automated_runs || 0}
            </span>
          </div>
        </div>
      </div>

      {/* Alt: OTOMASYON & YÜKSEK HIZLI MOTOR (Mor Vurgular Yalnız Burada) */}
      <div className="bg-dark-800 border border-purple-900/30 p-5 rounded-md space-y-4">
        <div className="flex items-center justify-between border-b border-slate-800/80 pb-3">
          <div className="flex items-center gap-2">
            <Zap className="w-4 h-4 text-purple-400" />
            <h4 className="font-bold text-xs font-mono uppercase tracking-wider text-slate-100">
              OTOMASYON & YÜKSEK HIZLI VERİ MOTORU
            </h4>
          </div>
          <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-purple-500/10 text-purple-400 border border-purple-500/30 font-semibold">
            CRON / 7-PROVIDER ENTEGRE
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {providers.map((p) => (
            <div key={p.name} className="bg-dark-900 p-3 rounded border border-slate-800/80 flex items-start justify-between">
              <div>
                <div className="flex items-center gap-1.5">
                  <span className="font-bold text-xs font-mono text-slate-200">{p.name}</span>
                  <span className="text-[9px] font-mono px-1.5 py-0.2 rounded bg-slate-800 text-slate-400">
                    {p.badge}
                  </span>
                </div>
                <p className="text-[10px] text-slate-400 mt-1 leading-relaxed">{p.desc}</p>
              </div>

              <div className="flex items-center gap-1 text-[10px] font-mono text-emerald-400 flex-shrink-0 ml-2">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
                <span>{p.status}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

    </div>
  );
};
