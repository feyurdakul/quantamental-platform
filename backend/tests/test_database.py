"""
Veritabanı ve Evren Seed Testleri
"""

import pytest
from app.db.repositories import AssetRepository
from app.models.asset import AssetClass


def test_database_seeded_assets():
    """Veritabanındaki seed varlıkların varlığı ve filtreleme doğrulaması"""
    # 1. Tüm varlıkları oku
    all_assets = AssetRepository.get_all()
    assert len(all_assets) >= 500

    # 2. BIST hisselerini filtrele
    bist_assets = AssetRepository.get_all(asset_class=AssetClass.BIST_STOCK.value)
    assert len(bist_assets) >= 50

    # 3. ABD hisselerini filtrele
    us_assets = AssetRepository.get_all(asset_class=AssetClass.US_STOCK.value)
    assert len(us_assets) >= 400

    # 4. Kripto paraları filtrele
    crypto_assets = AssetRepository.get_all(asset_class=AssetClass.CRYPTO.value)
    assert len(crypto_assets) >= 10

    # 5. Tek bir sembolü getir
    thyao = AssetRepository.get_by_symbol("BIST:THYAO")
    assert thyao is not None
    assert thyao.name == "Türk Hava Yolları"
    assert thyao.currency == "TRY"
