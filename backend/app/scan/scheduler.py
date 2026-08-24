"""
Otomatik Günlük Tarama ve Fiyat Güncelleme Zamanlayıcısı (Cron Scheduler)
Her gece TR Saati ile 01:30'da (UTC+3) otomatik olarak tüm evren için fiyatları çeker,
skorları günceller ve model portföy sinyallerini senkronize eder.
"""

import asyncio
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any
from app.db.repositories import AssetRepository
from app.scan.service import ScanOrchestrator


class DailyScanScheduler:
    """
    Her gün TR saati ile 01:30'da otomatik tarama çalıştıran arka plan servisi.
    """

    def __init__(self, orchestrator: ScanOrchestrator):
        self.orchestrator = orchestrator
        self.target_hour = 1
        self.target_minute = 30
        self.tr_tz = timezone(timedelta(hours=3))  # UTC+3 Türkiye Zaman Dilimi
        self._task: Optional[asyncio.Task] = None
        self._is_active = False
        self.last_run_at: Optional[datetime] = None
        self.last_run_status: str = "NEVER_RUN"
        self.total_automated_runs: int = 0

    def get_next_run_time(self) -> datetime:
        """Bir sonraki 01:30 TR çalışma zamanını hesaplar"""
        now_tr = datetime.now(self.tr_tz)
        target_today = now_tr.replace(hour=self.target_hour, minute=self.target_minute, second=0, microsecond=0)
        
        if now_tr >= target_today:
            # Bugünün 01:30'u geçti, yarına kur
            target_next = target_today + timedelta(days=1)
        else:
            target_next = target_today
            
        return target_next

    def get_seconds_until_next_run(self) -> float:
        """Bir sonraki 01:30'a kadar kalan saniyeyi hesaplar"""
        now_tr = datetime.now(self.tr_tz)
        next_run = self.get_next_run_time()
        delta = (next_run - now_tr).total_seconds()
        return max(1.0, delta)

    async def _scheduler_loop(self):
        """Sürekli çalışan arka plan cron döngüsü"""
        print(f"⏰ [CRON] Günlük Otomatik Veri Çekim Zamanlayıcısı Aktif. Hedef: Her gece TR 01:30 (UTC+3)")
        
        while self._is_active:
            try:
                seconds_to_wait = self.get_seconds_until_next_run()
                next_run = self.get_next_run_time()
                hours = int(seconds_to_wait // 3600)
                minutes = int((seconds_to_wait % 3600) // 60)
                print(f"⏰ [CRON] Sonraki otomatik tarama: {next_run.strftime('%d.%m.%Y %H:%M:%S TR')} (Kalan: {hours} sa {minutes} dk)")

                # Hedef zamana kadar uyu (1 dakikalık parçalarla kontrol ederek iptal durumunu dinle)
                while seconds_to_wait > 0 and self._is_active:
                    sleep_chunk = min(seconds_to_wait, 60.0)
                    await asyncio.sleep(sleep_chunk)
                    seconds_to_wait = self.get_seconds_until_next_run()

                if not self._is_active:
                    break

                # 01:30 Geldi! Otomatik Taramayı Başlat
                print(f"🚀 [CRON 01:30 TR] Otomatik Günlük Fiyat & Skor Taraması Başlatılıyor...")
                self.last_run_at = datetime.now(self.tr_tz)
                self.last_run_status = "RUNNING"

                universe = AssetRepository.get_all()
                if universe:
                    # Tarama orkestratörünü tetikle
                    await self.orchestrator.run_background_scan(universe)
                    self.last_run_status = "COMPLETED"
                    self.total_automated_runs += 1
                    print(f"✅ [CRON 01:30 TR] Otomatik Tarama Başarıyla Tamamlandı! ({len(universe)} varlık güncellendi)")
                else:
                    self.last_run_status = "NO_ASSETS_FOUND"
                    print("⚠️ [CRON] Evrende varlık bulunamadı.")

                # Aynı dakikada tekrar tetiklenmemesi için kısa bir bekleme
                await asyncio.sleep(65)

            except asyncio.CancelledError:
                print("🛑 [CRON] Zamanlayıcı görevi durduruldu.")
                break
            except Exception as e:
                print(f"❌ [CRON Hata] Zamanlayıcı döngüsünde hata: {e}")
                self.last_run_status = f"ERROR: {str(e)}"
                await asyncio.sleep(60)

    def start(self):
        """Zamanlayıcıyı başlatır"""
        if self._is_active:
            return
        self._is_active = True
        self._task = asyncio.create_task(self._scheduler_loop())

    def stop(self):
        """Zamanlayıcıyı durdurur"""
        self._is_active = False
        if self._task:
            self._task.cancel()
            self._task = None

    def get_status(self) -> Dict[str, Any]:
        """Zamanlayıcı durumunu döndürür"""
        next_run = self.get_next_run_time() if self._is_active else None
        now_tr = datetime.now(self.tr_tz)
        seconds_left = (next_run - now_tr).total_seconds() if next_run else None

        return {
            "is_active": self._is_active,
            "target_schedule": "Her Gece TR 01:30 (UTC+3)",
            "current_time_tr": now_tr.strftime("%Y-%m-%d %H:%M:%S"),
            "next_run_at_tr": next_run.strftime("%Y-%m-%d %H:%M:%S") if next_run else None,
            "seconds_until_next_run": round(seconds_left, 1) if seconds_left is not None else None,
            "last_run_at_tr": self.last_run_at.strftime("%Y-%m-%d %H:%M:%S") if self.last_run_at else None,
            "last_run_status": self.last_run_status,
            "total_automated_runs": self.total_automated_runs
        }
