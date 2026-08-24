"""
Finansal Snapshot Geçerlilik ve Koruma Doğrulayıcısı (sistem_mimari.md Bölüm 4.1 & İlke 4)
"""

from typing import Optional
from app.models.financials import FinancialSnapshot, SnapshotStatus


class FinancialValidator:
    """
    sistem_mimari.md Bölüm 4.1 ve Değişmez İlke 4:
    'Yeni boş/hatalı veri, son geçerli finansal snapshot’ı ezmez.'
    """

    @classmethod
    def validate_snapshot(cls, snapshot: FinancialSnapshot) -> bool:
        """
        Bir finansal snapshot'ın geçerlilik kapısından geçip geçmediğini doğrular.
        - Kaynak, para birimi ve period_end mevcut olmalı
        - En az iki anlamlı ana finansal kalem bulunmalı
        - Sayısal alanlar geçerli olmalı
        """
        if not snapshot.source_name or not snapshot.currency or not snapshot.period_end:
            snapshot.status = SnapshotStatus.INVALID
            return False

        if not snapshot.is_valid_financial_snapshot():
            snapshot.status = SnapshotStatus.INSUFFICIENT_DATA
            return False

        snapshot.status = SnapshotStatus.VALID
        return True

    @classmethod
    def should_replace_existing_snapshot(
        cls,
        current_valid_snapshot: Optional[FinancialSnapshot],
        incoming_snapshot: Optional[FinancialSnapshot]
    ) -> bool:
        """
        Mevcut geçerli snapshot ile yeni gelen snapshot'ı karşılaştırır.
        Eğer yeni snapshot geçersiz veya yetersizse, ESKİ GEÇERLİ SNAPSHOT KORUNUR.
        """
        if incoming_snapshot is None:
            return False

        is_incoming_valid = cls.validate_snapshot(incoming_snapshot)
        if not is_incoming_valid:
            # Yeni veri geçersiz -> Asla eskisini ezme!
            return False

        if current_valid_snapshot is None:
            # Eski veri yok ve yeni veri geçerli -> Kabul et
            return True

        # Her iki veri de geçerli -> Yeni verinin dönemi daha güncel veya eşitse güncelle
        return incoming_snapshot.period_end >= current_valid_snapshot.period_end
