import React, { useState, useEffect } from 'react';
import { Sidebar } from './components/Sidebar';
import { TopHeader } from './components/TopHeader';
import { MobileBottomNav } from './components/MobileBottomNav';
import { Dashboard } from './pages/Dashboard';
import { Universe } from './pages/Universe';
import { AssetDetail } from './pages/AssetDetail';
import { Portfolio } from './pages/Portfolio';
import { Settings } from './pages/Settings';
import { UserGuide } from './pages/UserGuide';
import { fetchScanStatus } from './api/client';

export function App() {
  const [activeTab, setActiveTab] = useState<string>('dashboard');
  const [selectedAsset, setSelectedAsset] = useState<string | null>('BIST:THYAO');
  const [scanStatus, setScanStatus] = useState<any>(null);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState<boolean>(false);

  const loadStatus = async () => {
    try {
      const data = await fetchScanStatus();
      setScanStatus(data);
    } catch (err) {
      // Backend bağlantısı henüz hazır değilse
    }
  };

  useEffect(() => {
    loadStatus();
    const timer = setInterval(loadStatus, 2500);
    return () => clearInterval(timer);
  }, []);

  const handleSelectAsset = (symbol: string) => {
    setSelectedAsset(symbol);
    setActiveTab('detail');
  };

  return (
    <div className="min-h-screen bg-dark-900 text-slate-100 flex overflow-hidden">
      
      {/* Sol Terminal Sidebar (Masaüstünde sabit, mobilde açılır çekmece) */}
      <Sidebar 
        activeTab={activeTab} 
        setActiveTab={setActiveTab}
        selectedAsset={selectedAsset}
        scanStage={scanStatus?.stage}
        isMobileOpen={isMobileMenuOpen}
        onCloseMobile={() => setIsMobileMenuOpen(false)}
      />

      {/* Ana Ekran Alanı (Üst Başlık Çubuğu + İçerik + Mobil Alt Bar) */}
      <div className="flex-1 flex flex-col min-w-0 h-screen overflow-y-auto">
        <TopHeader 
          activeTab={activeTab}
          scanStatus={scanStatus}
          onRefresh={loadStatus}
          onOpenMobileMenu={() => setIsMobileMenuOpen(true)}
        />

        <main className="p-3 md:p-6 pb-24 md:pb-6 flex-1 max-w-[1600px] w-full mx-auto">
          {activeTab === 'dashboard' && (
            <Dashboard 
              onSelectAsset={handleSelectAsset} 
              onNavigateToSettings={() => setActiveTab('settings')}
            />
          )}
          {activeTab === 'universe' && (
            <Universe onSelectAsset={handleSelectAsset} />
          )}
          {activeTab === 'detail' && (
            <AssetDetail 
              symbol={selectedAsset || 'BIST:THYAO'} 
              onBack={() => setActiveTab('universe')} 
            />
          )}
          {activeTab === 'portfolio' && (
            <Portfolio 
              onSelectAsset={handleSelectAsset} 
              onNavigateToUniverse={() => setActiveTab('universe')}
            />
          )}
          {activeTab === 'settings' && (
            <Settings onRefreshAll={loadStatus} />
          )}
          {activeTab === 'guide' && (
            <UserGuide />
          )}
        </main>

        {/* Mobil Alt Dokunmatik Navigasyon Çubuğu */}
        <MobileBottomNav 
          activeTab={activeTab}
          setActiveTab={setActiveTab}
          selectedAsset={selectedAsset}
          scanStage={scanStatus?.stage}
        />
      </div>

    </div>
  );
}

export default App;
