"""
FastAPI REST API Uç Noktaları (sistem_mimari.md Bölüm 10 UI Sayfaları için)
"""

import asyncio
from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from typing import Optional, List, Dict, Any
from app.models.asset import Asset, AssetClass
from app.db.repositories import AssetRepository
from app.scan.service import ScanOrchestrator
from app.scan.scheduler import DailyScanScheduler

import math

router = APIRouter(prefix="/v1")

# Global orchestrator singleton
orchestrator = ScanOrchestrator()
# Global daily 01:30 TR scan scheduler singleton
daily_scheduler = DailyScanScheduler(orchestrator)


def sanitize_for_json(obj: Any) -> Any:
    """Float NaN ve Infinity değerlerini JSON uyumlu None / null değerlerine dönüştürür"""
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return obj
    elif isinstance(obj, dict):
        return {k: sanitize_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [sanitize_for_json(v) for v in obj]
    elif hasattr(obj, "model_dump"):
        return sanitize_for_json(obj.model_dump())
    return obj



def _ensure_initial_scores():
    """İlk açılışta dashboard liderlik tablolarının dolu gelmesini garanti eder"""
    if not orchestrator.status.results:
        universe = AssetRepository.get_all()
        # İlk 15 majör varlık için hızlı ilk hesaplama yap
        sample_batch = universe[:25]
        orchestrator.process_universe_sync(sample_batch)
        # Açılış sonrası durumu IDLE (Hazır) yap ki kullanıcı tarama başlatabilsin
        orchestrator.status.stage = "IDLE"
        orchestrator.status.total_assets = len(universe)



_ensure_initial_scores()


@router.get("/dashboard/summary")
async def get_dashboard_summary():
    """
    10.1 Terminal Özeti / Dashboard:
    Aktif tarama durumu, toplam varlık, liderlik listeleri, veri tazeliği.
    """
    total_assets_count = len(AssetRepository.get_all())
    leaderboards = orchestrator._generate_leaderboards()

    return sanitize_for_json({
        "scan_stage": orchestrator.status.stage,
        "total_assets": total_assets_count,
        "processed_assets": orchestrator.status.processed_assets,
        "failed_assets": orchestrator.status.failed_assets,
        "leaderboards": leaderboards,
        "last_updated": orchestrator.status.completed_at
    })


@router.get("/universe")
async def get_universe(
    asset_class: Optional[str] = Query(None, description="Varlık sınıfı filtresi"),
    exchange: Optional[str] = Query(None, description="Borsa filtresi")
):
    """
    10.2 Varlık Evreni Listesi:
    Filtrelenebilir ve sıralanabilir tablo.
    """
    assets = AssetRepository.get_all(asset_class=asset_class, exchange=exchange)

    items = []
    for a in assets:
        sc = orchestrator.status.results.get(a.symbol, {})
        sr = sc.get("score_result")
        fr = sr.fundamental_rating if sr else None
        items.append({
            "symbol": a.symbol,
            "name": a.name,
            "asset_class": a.asset_class.value,
            "exchange": a.exchange,
            "sector": a.sector,
            "composite_score": sr.composite_score if sr else None,
            "signal": sr.signal.value if sr else "HOLD",
            "confidence": sr.confidence_level.value if sr else "LOW",
            "current_price": sc.get("technicals", {}).get("current_price"),
            "rating_letter": fr.get("rating") if fr else None,
            "rating_score": fr.get("total_score") if fr else None
        })

    return sanitize_for_json({"count": len(items), "assets": items})



@router.get("/asset/{symbol:path}")
async def get_asset_detail(symbol: str):
    """
    10.3 360° Asset Detail:
    Puan detayı, kategori açılımları, finansallar, Altman Z / Piotroski F, kaynak izlenebilirliği.
    """
    asset = AssetRepository.get_by_symbol(symbol)
    if not asset:
        raise HTTPException(status_code=404, detail=f"'{symbol}' varlığı evrende bulunamadı")

    scan_data = orchestrator.status.results.get(asset.symbol)
    
    # Eğer bu varlık henüz taranmamışsa veya teknik/fiyat verisi eksikse, anında canlı veri çek ve hesapla
    if not scan_data or not scan_data.get("technicals", {}).get("current_price"):
        from app.scan.pipeline import AssetScanPipeline
        from app.scan.market_fetcher import LiveMarketFetcher
        m_series = LiveMarketFetcher.fetch_market_series_fast(asset)
        fin_snaps = LiveMarketFetcher.fetch_financial_snapshots_fast(asset) if asset.requires_financials else []
        fresh_data = AssetScanPipeline.process_asset(asset, m_series, fin_snaps)
        if fresh_data.get("success"):
            orchestrator.status.results[asset.symbol] = fresh_data
            scan_data = fresh_data
            orchestrator._save_score_to_db(fresh_data)

    return sanitize_for_json({
        "asset": asset,
        "detail": scan_data or {}
    })




@router.post("/scan/start")
async def start_universe_scan():
    """
    10.5 Tam Taramayı Arka Planda Başlatma (Non-blocking Asenkron)
    """
    universe = AssetRepository.get_all()
    # Durumu hemen INIT / FETCHING olarak işaretle
    orchestrator.start_scan(universe)
    # Arka plan görevi olarak çalıştır
    asyncio.create_task(orchestrator.run_background_scan(universe))
    
    return {
        "message": "Evren taraması arka planda başarıyla başlatıldı.",
        "run_id": orchestrator.status.current_run_id,
        "total_assets": len(universe),
        "stage": "INIT"
    }


@router.get("/scan/status")
async def get_scan_status():
    """
    10.5 Gerçek Zamanlı Aşama ve Dürüst İlerleme Takibi
    """
    return {
        "run_id": orchestrator.status.current_run_id,
        "stage": orchestrator.status.stage,
        "total": orchestrator.status.total_assets,
        "processed": orchestrator.status.processed_assets,
        "failed": orchestrator.status.failed_assets,
        "started_at": orchestrator.status.started_at,
        "completed_at": orchestrator.status.completed_at
    }


@router.get("/scan/scheduler")
async def get_scheduler_status():
    """
    Her Gece TR 01:30 Otomatik Tarama Zamanlayıcısı Durumu
    """
    return daily_scheduler.get_status()


@router.post("/scan/scheduler/run-now")
async def trigger_scheduler_now():
    """
    Zamanlayıcıyı beklemeden günlük taramayı manuel hemen tetikler
    """
    universe = AssetRepository.get_all()
    orchestrator.start_scan(universe)
    asyncio.create_task(orchestrator.run_background_scan(universe))
    daily_scheduler.last_run_status = "TRIGGERED_MANUALLY"
    return {
        "message": "Günlük tarama manuel olarak hemen tetiklendi.",
        "total_assets": len(universe),
        "scheduler": daily_scheduler.get_status()
    }

