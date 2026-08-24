import React, { useState, useEffect } from 'react';
import { Sidebar } from './components/Sidebar';
import { TopHeader } from './components/TopHeader';
import { Dashboard } from './pages/Dashboard';
import { Universe } from './pages/Universe';
import { AssetDetail } from './pages/AssetDetail';
import { Portfolio } from './pages/Portfolio';
import { Settings } from './pages/Settings';
import { fetchScanStatus } from './api/client';

export function App() {
  const [activeTab, setActiveTab] = useState<string>('dashboard');
  const [selectedAsset, setSelectedAsset] = useState<string | null>('BIST:THYAO');
  const [scanStatus, setScanStatus] = useState<any>(null);

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
      
      {/* Sabit Sol Terminal Sidebar */}
      <Sidebar 
        activeTab={activeTab} 
        setActiveTab={setActiveTab}
        selectedAsset={selectedAsset}
        scanStage={scanStatus?.stage}
      />

      {/* Ana Ekran Alanı (Üst Başlık Çubuğu + İçerik) */}
      <div className="flex-1 flex flex-col min-w-0 h-screen overflow-y-auto">
        <TopHeader 
          activeTab={activeTab}
          scanStatus={scanStatus}
          onRefresh={loadStatus}
        />

        <main className="p-6 flex-1 max-w-[1600px] w-full mx-auto">
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
        </main>
      </div>

    </div>
  );
}

export default App;
