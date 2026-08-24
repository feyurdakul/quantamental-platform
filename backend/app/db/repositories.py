"""
Veritabanı CRUD Repository Modülü (PostgreSQL & SQLite Uyumlu)
"""

import json
from typing import List, Optional, Dict, Any
from app.db.database import get_db_connection
from app.models.asset import Asset, AssetClass


class AssetRepository:
    """Varlık tablosu erişim katmanı"""

    @staticmethod
    def get_all(asset_class: Optional[str] = None, exchange: Optional[str] = None) -> List[Asset]:
        conn = get_db_connection()
        cursor = conn.cursor()

        ph = "%s" if conn.is_postgres else "?"
        query = "SELECT * FROM assets WHERE is_active = " + ("TRUE" if conn.is_postgres else "1")
        params = []

        if asset_class:
            query += f" AND asset_class = {ph}"
            params.append(asset_class)
        if exchange:
            query += f" AND exchange = {ph}"
            params.append(exchange)

        query += " ORDER BY symbol ASC"
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        assets = []
        for r in rows:
            assets.append(Asset(
                symbol=r["symbol"],
                name=r["name"],
                asset_class=AssetClass(r["asset_class"]),
                exchange=r["exchange"],
                sector=r["sector"],
                industry=r["industry"],
                currency=r["currency"],
                is_active=bool(r["is_active"]),
                requires_financials=bool(r["requires_financials"])
            ))
        return assets

    @staticmethod
    def get_by_symbol(symbol: str) -> Optional[Asset]:
        conn = get_db_connection()
        cursor = conn.cursor()
        ph = "%s" if conn.is_postgres else "?"
        cursor.execute(f"SELECT * FROM assets WHERE UPPER(symbol) = UPPER({ph})", (symbol,))
        r = cursor.fetchone()
        conn.close()

        if not r:
            return None

        return Asset(
            symbol=r["symbol"],
            name=r["name"],
            asset_class=AssetClass(r["asset_class"]),
            exchange=r["exchange"],
            sector=r["sector"],
            industry=r["industry"],
            currency=r["currency"],
            is_active=bool(r["is_active"]),
            requires_financials=bool(r["requires_financials"])
        )

    @staticmethod
    def save_many(assets: List[Asset]):
        conn = get_db_connection()
        cursor = conn.cursor()

        if conn.is_postgres:
            cursor.executemany("""
            INSERT INTO assets (
                symbol, name, asset_class, exchange, sector, industry, currency, is_active, requires_financials
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (symbol) DO UPDATE SET
                name = EXCLUDED.name,
                asset_class = EXCLUDED.asset_class,
                exchange = EXCLUDED.exchange,
                sector = EXCLUDED.sector,
                industry = EXCLUDED.industry,
                currency = EXCLUDED.currency,
                is_active = EXCLUDED.is_active,
                requires_financials = EXCLUDED.requires_financials
            """, [
                (
                    a.symbol, a.name, a.asset_class.value, a.exchange,
                    a.sector, a.industry, a.currency, a.is_active,
                    a.requires_financials
                )
                for a in assets
            ])
        else:
            cursor.executemany("""
            INSERT OR REPLACE INTO assets (
                symbol, name, asset_class, exchange, sector, industry, currency, is_active, requires_financials
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, [
                (
                    a.symbol, a.name, a.asset_class.value, a.exchange,
                    a.sector, a.industry, a.currency, 1 if a.is_active else 0,
                    1 if a.requires_financials else 0
                )
                for a in assets
            ])

        conn.commit()
        conn.close()
