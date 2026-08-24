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
    """Model Portföy kalıcı veritabanı CRUD & Otomatik Senkronizasyon katmanı (Supabase & SQLite)"""

    @staticmethod
    def get_all() -> List[Dict[str, Any]]:
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT symbol, name, entry_price, quantity, target_weight_percent, sector, is_auto_managed, entry_timestamp, created_at 
                FROM portfolio_positions 
                ORDER BY created_at ASC
            """)
            rows = cursor.fetchall()
            positions = []
            for r in rows:
                positions.append({
                    "symbol": r["symbol"],
                    "name": r["name"],
                    "entry_price": float(r["entry_price"]),
                    "quantity": float(r["quantity"]),
                    "target_weight_percent": float(r["target_weight_percent"]) if "target_weight_percent" in r and r["target_weight_percent"] is not None else 10.0,
                    "sector": r["sector"] if "sector" in r else "Genel",
                    "is_auto_managed": bool(r["is_auto_managed"]) if "is_auto_managed" in r and r["is_auto_managed"] is not None else False,
                    "entry_timestamp": str(r["entry_timestamp"] if "entry_timestamp" in r and r["entry_timestamp"] else r["created_at"])
                })
            return positions
        except Exception:
            # Sütun uyumluluğu için temel fallback
            try:
                cursor.execute("SELECT symbol, name, entry_price, quantity, sector FROM portfolio_positions")
                rows = cursor.fetchall()
                return [{
                    "symbol": r["symbol"], "name": r["name"], "entry_price": float(r["entry_price"]),
                    "quantity": float(r["quantity"]), "target_weight_percent": 10.0,
                    "sector": r["sector"], "is_auto_managed": False, "entry_timestamp": ""
                } for r in rows]
            except Exception:
                return []
        finally:
            conn.close()

    @staticmethod
    def save_position(
        symbol: str, 
        name: str, 
        entry_price: float, 
        quantity: float = 100.0, 
        target_weight_percent: float = 10.0,
        sector: Optional[str] = None,
        is_auto_managed: bool = False
    ):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            if conn.is_postgres:
                cursor.execute("""
                INSERT INTO portfolio_positions (symbol, name, entry_price, quantity, target_weight_percent, sector, is_auto_managed, entry_timestamp, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                ON CONFLICT (symbol) DO UPDATE SET
                    name = EXCLUDED.name,
                    entry_price = EXCLUDED.entry_price,
                    quantity = EXCLUDED.quantity,
                    target_weight_percent = EXCLUDED.target_weight_percent,
                    sector = EXCLUDED.sector,
                    is_auto_managed = EXCLUDED.is_auto_managed,
                    updated_at = NOW()
                """, (symbol, name, entry_price, quantity, target_weight_percent, sector, is_auto_managed))

                cursor.execute("""
                INSERT INTO portfolio_trades (symbol, name, action, price, quantity, total_amount, realized_pnl, reason)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (symbol, name, "AUTO_BUY" if is_auto_managed else "BUY", entry_price, quantity, entry_price * quantity, 0.0, "Model Portföye Alım"))
            else:
                cursor.execute("""
                INSERT OR REPLACE INTO portfolio_positions (symbol, name, entry_price, quantity, target_weight_percent, sector, is_auto_managed, entry_timestamp, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                """, (symbol, name, entry_price, quantity, target_weight_percent, sector, 1 if is_auto_managed else 0))

                cursor.execute("""
                INSERT INTO portfolio_trades (symbol, name, action, price, quantity, total_amount, realized_pnl, reason)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (symbol, name, "AUTO_BUY" if is_auto_managed else "BUY", entry_price, quantity, entry_price * quantity, 0.0, "Model Portföye Alım"))
            conn.commit()
        finally:
            conn.close()

    @staticmethod
    def partial_sell(symbol: str, sell_percent: float, current_price: float) -> Dict[str, Any]:
        """Kısmi veya tam satış gerçekleştirir ve gerçekleşen kâr/zararı kaydeder"""
        conn = get_db_connection()
        cursor = conn.cursor()
        ph = "%s" if conn.is_postgres else "?"
        try:
            cursor.execute(f"SELECT * FROM portfolio_positions WHERE UPPER(symbol) = UPPER({ph})", (symbol,))
            row = cursor.fetchone()
            if not row:
                return {"success": False, "message": "Pozisyon bulunamadı"}

            entry_price = float(row["entry_price"])
            current_qty = float(row["quantity"])
            name = row["name"]
            
            sell_ratio = max(0.01, min(1.0, sell_percent / 100.0))
            sold_qty = current_qty * sell_ratio
            remaining_qty = current_qty - sold_qty

            realized_pnl = (current_price - entry_price) * sold_qty
            total_sell_amount = current_price * sold_qty

            # İşlem geçmişine kaydet
            trade_action = "FULL_SELL" if sell_ratio >= 0.99 else f"PARTIAL_SELL_%{int(sell_percent)}"
            if conn.is_postgres:
                cursor.execute("""
                INSERT INTO portfolio_trades (symbol, name, action, price, quantity, total_amount, realized_pnl, reason)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (symbol, name, trade_action, current_price, sold_qty, total_sell_amount, realized_pnl, f"Kâr Realizasyonu (%{sell_percent})"))
            else:
                cursor.execute("""
                INSERT INTO portfolio_trades (symbol, name, action, price, quantity, total_amount, realized_pnl, reason)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (symbol, name, trade_action, current_price, sold_qty, total_sell_amount, realized_pnl, f"Kâr Realizasyonu (%{sell_percent})"))

            if remaining_qty <= 0.001 or sell_ratio >= 0.99:
                # Tamamen satıldı, pozisyonu kapat
                cursor.execute(f"DELETE FROM portfolio_positions WHERE UPPER(symbol) = UPPER({ph})", (symbol,))
            else:
                # Kalan miktarı güncelle
                if conn.is_postgres:
                    cursor.execute("UPDATE portfolio_positions SET quantity = %s, updated_at = NOW() WHERE UPPER(symbol) = UPPER(%s)", (remaining_qty, symbol))
                else:
                    cursor.execute("UPDATE portfolio_positions SET quantity = ?, updated_at = CURRENT_TIMESTAMP WHERE UPPER(symbol) = UPPER(?)", (remaining_qty, symbol))

            conn.commit()
            return {
                "success": True,
                "symbol": symbol,
                "sold_quantity": sold_qty,
                "remaining_quantity": remaining_qty,
                "realized_pnl": realized_pnl,
                "is_closed": remaining_qty <= 0.001 or sell_ratio >= 0.99
            }
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

    @staticmethod
    def get_trades() -> List[Dict[str, Any]]:
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM portfolio_trades ORDER BY created_at DESC LIMIT 50")
            rows = cursor.fetchall()
            return [{
                "id": r["id"],
                "symbol": r["symbol"],
                "name": r["name"],
                "action": r["action"],
                "price": float(r["price"]),
                "quantity": float(r["quantity"]),
                "total_amount": float(r["total_amount"]),
                "realized_pnl": float(r["realized_pnl"]) if "realized_pnl" in r and r["realized_pnl"] is not None else 0.0,
                "reason": r["reason"] if "reason" in r else "",
                "created_at": str(r["created_at"])
            } for r in rows]
        except Exception:
            return []
        finally:
            conn.close()

    @staticmethod
    def sync_auto_signals(top_potential: List[Dict[str, Any]], most_risky: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Tarama Sonu Otomatik Portföy Yönetimi:
        1. En Riskli/Sat listesine düşen portföy hisselerini otomatik satar.
        2. En Güçlü Potansiyel tablosundaki ilk 10 hisseyi Strong Buy (%10) veya Buy (%7) olarak portföye ekler.
        """
        current_positions = {p["symbol"].upper(): p for p in PortfolioRepository.get_all()}
        auto_sold = []
        auto_bought = []

        # 1. Otomatik Satış: En Riskli Listesinde olan mevcut portföy hisseleri
        risky_symbols = {r["symbol"].upper(): r for r in most_risky if r.get("signal") in ["SELL", "STRONG_SELL"]}
        for sym_upper, pos in current_positions.items():
            if sym_upper in risky_symbols:
                risk_info = risky_symbols[sym_upper]
                cur_price = risk_info.get("current_price") or pos["entry_price"]
                PortfolioRepository.partial_sell(pos["symbol"], 100.0, cur_price)
                auto_sold.append(pos["symbol"])

        # 2. Otomatik Alım: En Güçlü Potansiyel Liderleri (İlk 10)
        current_positions_after_sell = {p["symbol"].upper(): p for p in PortfolioRepository.get_all()}
        
        for item in top_potential[:10]:
            sym = item.get("symbol")
            if not sym or sym.upper() in current_positions_after_sell:
                continue

            sig = item.get("signal", "BUY")
            cur_price = item.get("current_price") or 100.0
            
            # Ağırlık Kuralları: Strong Buy %10, Buy %7
            target_weight = 10.0 if sig == "STRONG_BUY" else 7.0
            qty = max(1.0, round(10000.0 / cur_price, 2))  # Varsayılan simüle lot
            
            PortfolioRepository.save_position(
                symbol=sym,
                name=item.get("name") or sym,
                entry_price=cur_price,
                quantity=qty,
                target_weight_percent=target_weight,
                sector=item.get("sector") or "Genel",
                is_auto_managed=True
            )
            auto_bought.append(sym)

        return {
            "auto_sold": auto_sold,
            "auto_bought": auto_bought
        }


