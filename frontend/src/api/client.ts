/**
 * Backend REST API İstemcisi
 */

const envApiUrl = (import.meta as any).env?.VITE_API_URL;
const API_BASE = (envApiUrl ? envApiUrl.replace(/\/$/, '') : '') + '/v1';

export async function fetchDashboardSummary() {
  const res = await fetch(`${API_BASE}/dashboard/summary`);
  if (!res.ok) throw new Error('Dashboard verisi alınamadı');
  return res.json();
}

export async function fetchUniverse(assetClass?: string, exchange?: string) {
  const params = new URLSearchParams();
  if (assetClass) params.append('asset_class', assetClass);
  if (exchange) params.append('exchange', exchange);
  
  const res = await fetch(`${API_BASE}/universe?${params.toString()}`);
  if (!res.ok) throw new Error('Varlık evreni alınamadı');
  return res.json();
}

export async function fetchAssetDetail(symbol: string) {
  const res = await fetch(`${API_BASE}/asset/${encodeURIComponent(symbol)}`);
  if (!res.ok) throw new Error('Varlık detayı alınamadı');
  return res.json();
}

export async function fetchPortfolio() {
  const res = await fetch(`${API_BASE}/portfolio`);
  if (!res.ok) throw new Error('Portföy verisi alınamadı');
  return res.json();
}

export async function addPortfolioPosition(data: {
  symbol: string;
  name: string;
  entry_price: number;
  quantity?: number;
  sector?: string;
}) {
  const res = await fetch(`${API_BASE}/portfolio/positions`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
  if (!res.ok) throw new Error('Pozisyon eklenemedi');
  return res.json();
}

export async function deletePortfolioPosition(symbol: string) {
  const res = await fetch(`${API_BASE}/portfolio/positions/${encodeURIComponent(symbol)}`, {
    method: 'DELETE'
  });
  if (!res.ok) throw new Error('Pozisyon silinemedi');
  return res.json();
}

export async function triggerScan() {
  const res = await fetch(`${API_BASE}/scan/start`, { method: 'POST' });
  if (!res.ok) throw new Error('Tarama başlatılamadı');
  return res.json();
}

export async function fetchScanStatus() {
  const res = await fetch(`${API_BASE}/scan/status`);
  if (!res.ok) throw new Error('Tarama durumu alınamadı');
  return res.json();
}
