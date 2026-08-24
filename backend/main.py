"""
Quantamental Platform — Ana FastAPI Uygulaması
sistem_mimari.md Spesifikasyonu Tam Uyumu (7 Sağlayıcılı Hibrit Mimari)
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router as api_router, daily_scheduler
from app.api.routes_portfolio import portfolio_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Uygulama başladığında 01:30 TR Günlük Otomatik Tarama Zamanlayıcısını Başlat
    daily_scheduler.start()
    yield
    # Kapanışta zamanlayıcıyı güvenle durdur
    daily_scheduler.stop()


app = FastAPI(
    title="Quantamental Platform API",
    description="7 Sağlayıcılı Kurumsal Finansal Analiz ve Skorlama Platformu",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Ayarları (Frontend bağlantısı için)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)
app.include_router(portfolio_router)


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "Quantamental Platform Backend",
        "version": "1.0.0",
        "providers_active": [
            "isyatirimhisse", "yfinance", "FMP",
            "Finnhub", "GoogleFinance", "TradingView", "fredapi"
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
