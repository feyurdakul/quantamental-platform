"""
01:30 TR Günlük Otomatik Zamanlayıcı (Cron Scheduler) Test Paketi
"""

import pytest
from datetime import datetime, timezone, timedelta
from app.scan.scheduler import DailyScanScheduler
from app.scan.service import ScanOrchestrator
from app.models.asset import Asset, AssetClass


def test_scheduler_calculation():
    orchestrator = ScanOrchestrator()
    scheduler = DailyScanScheduler(orchestrator)
    
    # Hedef 01:30 olmalı
    assert scheduler.target_hour == 1
    assert scheduler.target_minute == 30
    
    # Bir sonraki çalışma zamanı gelecekte bir tarih olmalı
    next_run = scheduler.get_next_run_time()
    now_tr = datetime.now(scheduler.tr_tz)
    assert next_run > now_tr
    assert next_run.hour == 1
    assert next_run.minute == 30
    
    # Kalan saniye pozitif olmalı
    seconds = scheduler.get_seconds_until_next_run()
    assert seconds > 0
    assert seconds <= 86400 # En fazla 24 saat


def test_scheduler_status_format():
    orchestrator = ScanOrchestrator()
    scheduler = DailyScanScheduler(orchestrator)
    status = scheduler.get_status()
    
    assert "is_active" in status
    assert "target_schedule" in status
    assert "01:30" in status["target_schedule"]
    assert "next_run_at_tr" in status
    assert "total_automated_runs" in status
