import React from 'react';
import { 
  LayoutDashboard, 
  Layers, 
  PieChart, 
  Settings, 
  Activity,
  Cpu
} from 'lucide-react';

interface NavbarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  selectedAsset: string | null;
}

export const Navbar: React.FC<NavbarProps> = ({ activeTab, setActiveTab, selectedAsset }) => {
  const navItems = [
    { id: 'dashboard', label: 'Terminal Özeti', icon: LayoutDashboard },
    { id: 'universe', label: 'Varlık Evreni', icon: Layers },
    { id: 'detail', label: selectedAsset ? `Detay (${selectedAsset})` : 'Asset Detail', icon: Activity },
    { id: 'portfolio', label: 'Model Portföy', icon: PieChart },
    { id: 'settings', label: 'Ayarlar & Tarama', icon: Settings },
  ];

  return (
    <header className="sticky top-0 z-50 glass-panel border-b border-white/10 px-6 py-3.5">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        
        {/* Logo & Marka */}
        <div className="flex items-center gap-3 cursor-pointer" onClick={() => setActiveTab('dashboard')}>
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-blue-600 to-emerald-500 flex items-center justify-center shadow-lg shadow-blue-500/20">
            <Cpu className="w-5 h-5 text-white" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-bold text-lg tracking-tight bg-gradient-to-r from-white via-slate-200 to-slate-400 bg-clip-text text-transparent">
                QUANTAMENTAL
              </span>
              <span className="text-[10px] font-mono uppercase px-1.5 py-0.5 rounded bg-blue-500/20 text-blue-400 border border-blue-500/30">
                7 PROVIDER PRO
              </span>
            </div>
            <p className="text-[11px] text-slate-400 font-mono tracking-wider">HİBRİT KARAR DESTEK TERMİNALİ</p>
          </div>
        </div>

        {/* Navigasyon Sekmeleri */}
        <nav className="flex items-center gap-1 bg-dark-800/80 p-1 rounded-xl border border-white/5">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`flex items-center gap-2 px-3.5 py-2 rounded-lg text-xs font-medium transition-all duration-150 ${
                  isActive
                    ? 'bg-blue-600 text-white shadow-md shadow-blue-600/30 font-semibold'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-white/5'
                }`}
              >
                <Icon className="w-4 h-4" />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>

        {/* Canlı Bağlantı Rozeti */}
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-emerald-500/10 border border-emerald-500/20">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
          <span className="text-xs font-mono text-emerald-400 font-medium">SİSTEM ÇEVRİMİÇİ</span>
        </div>

      </div>
    </header>
  );
};
