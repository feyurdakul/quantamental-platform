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

        if not rows and not asset_class and not exchange:
            # Otomatik fail-safe tohumlama
            from app.db.seed_universe import build_711_universe
            universe = build_711_universe()
            AssetRepository.save_many(universe)
            return universe

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
            # Eğer tablo boşsa tohumla ve tekrar ara
            from app.db.seed_universe import build_711_universe
            universe = build_711_universe()
            AssetRepository.save_many(universe)
            for a in universe:
                if a.symbol.upper() == symbol.upper():
                    return a
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


class PortfolioRepository:
    """Model Portföy kalıcı veritabanı CRUD katmanı (Supabase & SQLite)"""

    @staticmethod
    def get_all() -> List[Dict[str, Any]]:
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT symbol, name, entry_price, quantity, sector FROM portfolio_positions ORDER BY created_at ASC")
            rows = cursor.fetchall()
            positions = []
            for r in rows:
                positions.append({
                    "symbol": r["symbol"],
                    "name": r["name"],
                    "entry_price": float(r["entry_price"]),
                    "quantity": float(r["quantity"]),
                    "sector": r["sector"]
                })
            return positions
        except Exception:
            return []
        finally:
            conn.close()

    @staticmethod
    def save_position(symbol: str, name: str, entry_price: float, quantity: float = 100.0, sector: Optional[str] = None):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            if conn.is_postgres:
                cursor.execute("""
                INSERT INTO portfolio_positions (symbol, name, entry_price, quantity, sector, updated_at)
                VALUES (%s, %s, %s, %s, %s, NOW())
                ON CONFLICT (symbol) DO UPDATE SET
                    name = EXCLUDED.name,
                    entry_price = EXCLUDED.entry_price,
                    quantity = EXCLUDED.quantity,
                    sector = EXCLUDED.sector,
                    updated_at = NOW()
                """, (symbol, name, entry_price, quantity, sector))
            else:
                cursor.execute("""
                INSERT OR REPLACE INTO portfolio_positions (symbol, name, entry_price, quantity, sector, updated_at)
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                """, (symbol, name, entry_price, quantity, sector))
            conn.commit()
        finally:
            conn.close()

    @staticmethod
    def delete_position(symbol: str) -> bool:
        conn = get_db_connection()
        cursor = conn.cursor()
        ph = "%s" if conn.is_postgres else "?"
        try:
            cursor.execute(f"DELETE FROM portfolio_positions WHERE UPPER(symbol) = UPPER({ph})", (symbol,))
            conn.commit()
            return True
        except Exception:
            return False
        finally:
            conn.close()

