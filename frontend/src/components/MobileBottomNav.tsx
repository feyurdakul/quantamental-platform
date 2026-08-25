import React from 'react';
import { 
  LayoutDashboard, 
  Layers, 
  PieChart, 
  Settings, 
  Activity,
  BookOpen
} from 'lucide-react';

interface MobileBottomNavProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  selectedAsset: string | null;
  scanStage?: string;
}

export const MobileBottomNav: React.FC<MobileBottomNavProps> = ({
  activeTab,
  setActiveTab,
  selectedAsset,
  scanStage
}) => {
  const isScanning = scanStage === 'SCORING' || scanStage === 'FETCHING' || scanStage === 'INIT' || scanStage === 'BENCHMARKS';

  const navItems = [
    { id: 'dashboard', label: 'Özet', icon: LayoutDashboard },
    { id: 'universe', label: 'Evren', icon: Layers },
    { id: 'detail', label: 'Detay', icon: Activity },
    { id: 'portfolio', label: 'Portföy', icon: PieChart },
    { id: 'settings', label: 'Ayarlar', icon: Settings },
    { id: 'guide', label: 'Rehber', icon: BookOpen },
  ];

  return (
    <nav className="md:hidden fixed bottom-0 left-0 right-0 z-50 bg-dark-900/95 backdrop-blur-md border-t border-slate-800/90 px-1 py-1 shadow-2xl safe-area-bottom pointer-events-auto">
      <div className="grid grid-cols-6 items-center gap-0.5">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              id={`mobile-nav-${item.id}`}
              onClick={() => setActiveTab(item.id)}
              className={`flex flex-col items-center justify-center min-h-[48px] py-1 px-0.5 rounded-md transition-all relative select-none cursor-pointer ${
                isActive
                  ? 'text-blue-400 bg-blue-500/10 font-bold'
                  : 'text-slate-400 hover:text-slate-200 active:bg-slate-800/50'
              }`}
            >
              <div className="relative">
                <Icon className={`w-4 h-4 transition-transform ${isActive ? 'scale-110 text-blue-400' : 'text-slate-400'}`} />
                {item.id === 'settings' && isScanning && (
                  <span className="absolute -top-1 -right-1 w-2 h-2 rounded-full bg-blue-400 animate-ping" />
                )}
              </div>
              <span className="text-[10px] font-mono mt-0.5 tracking-tight truncate max-w-full">
                {item.label}
              </span>
              {isActive && (
                <span className="absolute top-0 w-5 h-0.5 bg-blue-500 rounded-full" />
              )}
            </button>
          );
        })}
      </div>
    </nav>
  );
};
