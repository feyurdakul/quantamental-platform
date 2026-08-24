import React from 'react';
import { 
  LayoutDashboard, 
  Layers, 
  PieChart, 
  Settings, 
  Activity,
  Cpu,
  Database,
  Radio,
  BookOpen
} from 'lucide-react';

interface SidebarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  selectedAsset: string | null;
  scanStage?: string;
}

export const Sidebar: React.FC<SidebarProps> = ({ 
  activeTab, 
  setActiveTab, 
  selectedAsset,
  scanStage 
}) => {
  const menuItems = [
    { id: 'dashboard', label: 'Terminal Özeti', icon: LayoutDashboard },
    { id: 'universe', label: 'Varlık Evreni', icon: Layers },
    { id: 'detail', label: selectedAsset ? `Detay (${selectedAsset})` : 'Asset Detail', icon: Activity },
    { id: 'portfolio', label: 'Model Portföy', icon: PieChart },
    { id: 'settings', label: 'Ayarlar & Yönetim', icon: Settings },
    { id: 'guide', label: 'Nasıl Kullanılır?', icon: BookOpen },
  ];

  const isScanning = scanStage === 'SCORING' || scanStage === 'FETCHING' || scanStage === 'INIT' || scanStage === 'BENCHMARKS';

  return (
    <aside className="w-64 bg-dark-900 border-r border-slate-800/80 flex flex-col justify-between flex-shrink-0 min-h-screen">
      <div>
        {/* Logo & Marka Başlığı */}
        <div 
          onClick={() => setActiveTab('dashboard')}
          className="p-5 border-b border-slate-800/80 cursor-pointer flex items-center gap-3 group"
        >
          <div className="w-8 h-8 rounded-md bg-blue-600/20 border border-blue-500/40 flex items-center justify-center text-blue-400 group-hover:bg-blue-600 group-hover:text-white transition-all">
            <Cpu className="w-4 h-4" />
          </div>
          <div>
            <div className="flex items-center gap-1.5">
              <span className="font-bold text-sm tracking-wider text-white">QUANTAMENTAL</span>
            </div>
            <span className="text-[10px] font-mono text-blue-400 block tracking-wider">7-PROVIDER TERMINAL</span>
          </div>
        </div>

        {/* Ana Navigasyon */}
        <div className="px-3 py-4">
          <p className="px-3 text-[10px] font-mono text-slate-500 uppercase tracking-wider mb-2">NAVİGASYON</p>
          <nav className="space-y-1">
            {menuItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => setActiveTab(item.id)}
                  className={`w-full flex items-center justify-between px-3 py-2.5 rounded-md text-xs font-medium transition-colors ${
                    isActive
                      ? 'bg-blue-600/15 text-blue-400 border border-blue-500/30 font-semibold'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                  }`}
                >
                  <div className="flex items-center gap-2.5">
                    <Icon className={`w-4 h-4 ${isActive ? 'text-blue-400' : 'text-slate-400'}`} />
                    <span>{item.label}</span>
                  </div>
                  {item.id === 'settings' && isScanning && (
                    <span className="w-2 h-2 rounded-full bg-blue-400 animate-ping" />
                  )}
                </button>
              );
            })}
          </nav>
        </div>
      </div>

      {/* Alt Sistem Durum Kartı */}
      <div className="p-4 border-t border-slate-800/80 bg-dark-900/60">
        <div className="space-y-2 text-[11px] font-mono">
          <div className="flex items-center justify-between text-slate-400">
            <span className="flex items-center gap-1.5">
              <Radio className="w-3 h-3 text-emerald-400" />
              Sağlayıcılar:
            </span>
            <span className="text-emerald-400 font-semibold">7 / 7 Online</span>
          </div>
          <div className="flex items-center justify-between text-slate-400">
            <span className="flex items-center gap-1.5">
              <Database className="w-3 h-3 text-blue-400" />
              Veritabanı:
            </span>
            <span className="text-slate-300">SQLite Aktif</span>
          </div>
          <div className="pt-2 border-t border-slate-800/50 flex justify-between text-[10px] text-slate-500">
            <span>Sürüm v1.0.0</span>
            <span>PRO EDITION</span>
          </div>
        </div>
      </div>
    </aside>
  );
};
