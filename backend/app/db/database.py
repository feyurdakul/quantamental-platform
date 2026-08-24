"""
Veritabanı Bağlantı ve Tablo Yöneticisi (SQLite & Supabase PostgreSQL Hibrit Uyumlu)
DATABASE_URL ortam değişkeni varsa Supabase PostgreSQL'e, yoksa yerel SQLite'a bağlanır.
"""

import os
import sqlite3
from typing import Optional, Any
from pathlib import Path

DATABASE_URL = os.getenv("DATABASE_URL")
DB_PATH = os.getenv("SQLITE_DB_PATH", str(Path(__file__).parent.parent.parent / "quantamental.db"))


class DBConnectionWrapper:
    """PostgreSQL ve SQLite bağlantılarını ortak arayüzle sarmalar"""
    def __init__(self, raw_conn, is_postgres: bool = False):
        self.raw_conn = raw_conn
        self.is_postgres = is_postgres

    def cursor(self):
        if self.is_postgres:
            import psycopg2.extras
            return self.raw_conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        return self.raw_conn.cursor()

    def commit(self):
        self.raw_conn.commit()

    def close(self):
        self.raw_conn.close()


def get_db_connection():
    """Ortam değişkenine göre PostgreSQL veya SQLite bağlantısı döner (Hata durumunda SQLite fallback)"""
    db_url = os.getenv("DATABASE_URL")
    if db_url and db_url.startswith("postgres"):
        try:
            import psycopg2
            from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
            # Prisma query parametrelerini temizle ve sslmode=require ekle
            parsed = urlparse(db_url)
            # Query parametrelerinden pgbouncer'ı kaldır
            clean_url = urlunparse((parsed.scheme, parsed.netloc, parsed.path, '', '', ''))
            raw_conn = psycopg2.connect(clean_url, sslmode="require")
            return DBConnectionWrapper(raw_conn, is_postgres=True)
        except Exception as e:
            print(f"PostgreSQL bağlantı hatası ({e}), yerel SQLite veritabanına geçiliyor...")
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row
            return DBConnectionWrapper(conn, is_postgres=False)
    else:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return DBConnectionWrapper(conn, is_postgres=False)


def init_db():
    """Tabloları veritabanında oluşturur"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        if conn.is_postgres:
            # PostgreSQL DDL
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS assets (
                symbol VARCHAR(50) PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                asset_class VARCHAR(50) NOT NULL,
                exchange VARCHAR(50) NOT NULL,
                sector VARCHAR(100),
                industry VARCHAR(100),
                currency VARCHAR(10) NOT NULL DEFAULT 'TRY',
                is_active BOOLEAN NOT NULL DEFAULT TRUE,
                requires_financials BOOLEAN NOT NULL DEFAULT TRUE,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            );

            CREATE TABLE IF NOT EXISTS score_results (
                symbol VARCHAR(50) PRIMARY KEY REFERENCES assets(symbol) ON DELETE CASCADE,
                composite_score NUMERIC(5, 2) NOT NULL,
                confidence_level VARCHAR(20) NOT NULL,
                signal VARCHAR(30) NOT NULL,
                coverage NUMERIC(5, 4) NOT NULL,
                category_scores_json JSONB NOT NULL,
                altman_z_score NUMERIC(8, 4),
                piotroski_f_score INTEGER,
                formula_version VARCHAR(20) NOT NULL DEFAULT '1.0.0',
                flags_json JSONB NOT NULL DEFAULT '[]'::jsonb,
                as_of_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            );

            CREATE TABLE IF NOT EXISTS portfolio_positions (
                symbol VARCHAR(50) PRIMARY KEY,
                name VARCHAR(200) NOT NULL,
                entry_price NUMERIC(15, 4) NOT NULL,
                quantity NUMERIC(15, 4) NOT NULL DEFAULT 100,
                target_weight_percent NUMERIC(5, 2) NOT NULL DEFAULT 10.0,
                sector VARCHAR(100),
                is_auto_managed BOOLEAN NOT NULL DEFAULT FALSE,
                entry_timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            );

            CREATE TABLE IF NOT EXISTS portfolio_trades (
                id SERIAL PRIMARY KEY,
                symbol VARCHAR(50) NOT NULL,
                name VARCHAR(200) NOT NULL,
                action VARCHAR(30) NOT NULL,
                price NUMERIC(15, 4) NOT NULL,
                quantity NUMERIC(15, 4) NOT NULL,
                total_amount NUMERIC(15, 4) NOT NULL,
                realized_pnl NUMERIC(15, 4) DEFAULT 0,
                reason VARCHAR(200),
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            );
            """)
        else:
            # SQLite DDL
            cursor.executescript("""
            CREATE TABLE IF NOT EXISTS assets (
                symbol TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                asset_class TEXT NOT NULL,
                exchange TEXT NOT NULL,
                sector TEXT,
                industry TEXT,
                currency TEXT NOT NULL DEFAULT 'TRY',
                is_active INTEGER NOT NULL DEFAULT 1,
                requires_financials INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS score_results (
                symbol TEXT PRIMARY KEY,
                composite_score REAL NOT NULL,
                confidence_level TEXT NOT NULL,
                signal TEXT NOT NULL,
                coverage REAL NOT NULL,
                category_scores_json TEXT NOT NULL,
                altman_z_score REAL,
                piotroski_f_score INTEGER,
                formula_version TEXT NOT NULL DEFAULT '1.0.0',
                flags_json TEXT NOT NULL DEFAULT '[]',
                as_of_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (symbol) REFERENCES assets(symbol) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS portfolio_positions (
                symbol TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                entry_price REAL NOT NULL,
                quantity REAL NOT NULL DEFAULT 100,
                target_weight_percent REAL NOT NULL DEFAULT 10.0,
                sector TEXT,
                is_auto_managed INTEGER NOT NULL DEFAULT 0,
                entry_timestamp TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS portfolio_trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                name TEXT NOT NULL,
                action TEXT NOT NULL,
                price REAL NOT NULL,
                quantity REAL NOT NULL,
                total_amount REAL NOT NULL,
                realized_pnl REAL DEFAULT 0,
                reason TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            """)

        # Tablo şema kolon güncellemeleri (Migration garantisi)
        try:
            if conn.is_postgres:
                cursor.execute("ALTER TABLE portfolio_positions ADD COLUMN IF NOT EXISTS target_weight_percent NUMERIC(5, 2) NOT NULL DEFAULT 10.0")
                cursor.execute("ALTER TABLE portfolio_positions ADD COLUMN IF NOT EXISTS is_auto_managed BOOLEAN NOT NULL DEFAULT FALSE")
                cursor.execute("ALTER TABLE portfolio_positions ADD COLUMN IF NOT EXISTS entry_timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW()")
            else:
                cursor.execute("PRAGMA table_info(portfolio_positions)")
                cols = [c[1] for c in cursor.fetchall()]
                if 'target_weight_percent' not in cols:
                    cursor.execute("ALTER TABLE portfolio_positions ADD COLUMN target_weight_percent REAL NOT NULL DEFAULT 10.0")
                if 'is_auto_managed' not in cols:
                    cursor.execute("ALTER TABLE portfolio_positions ADD COLUMN is_auto_managed INTEGER NOT NULL DEFAULT 0")
                if 'entry_timestamp' not in cols:
                    cursor.execute("ALTER TABLE portfolio_positions ADD COLUMN entry_timestamp TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP")
            conn.commit()
        except Exception:
            pass

        # ETF ve Kriptolar temel analiz yapılamadığı için evrenden temizlenir
        try:
            cursor.execute("DELETE FROM assets WHERE asset_class IN ('ETF', 'CRYPTO')")
            cursor.execute("DELETE FROM score_results WHERE symbol LIKE 'AMEX:%' OR symbol LIKE 'BINANCE:%'")
            conn.commit()
        except Exception:
            pass

        # Eğer assets tablosu boşsa (ilk kurulum/deployment), hisse senedi evrenini otomatik yükle
        cursor.execute("SELECT count(*) as cnt FROM assets")
        row = cursor.fetchone()
        count = row[0] if isinstance(row, tuple) else (row["cnt"] if row else 0)
        conn.close()

        if count == 0:
            print("🚀 Veritabanı ilk kurulumu: Varlık evreni otomatik yükleniyor...")
            try:
                from app.db.seed_universe import build_711_universe
                from app.db.repositories import AssetRepository
                universe = build_711_universe()
                AssetRepository.save_many(universe)
                print(f"✅ Başarıyla {len(universe)} varlık veritabanına yüklendi.")
            except Exception as se:
                print(f"Seed uyarısı: {se}")

    except Exception as e:
        print(f"init_db uyarısı: {e}")



# Uygulama başlatıldığında tabloları ve varlıkları hazırla
init_db()

