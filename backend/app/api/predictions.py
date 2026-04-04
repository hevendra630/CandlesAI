from fastapi import APIRouter, Depends, HTTPException
from app.core.security import get_current_user
from app.core.cache import cache_get, cache_set
from app.core.config import get_settings
from app.models.user import User
import httpx
import numpy as np
import logging
import os
from datetime import datetime, timedelta

# 🔥 Alpaca Imports
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame

router = APIRouter()
logger = logging.getLogger(__name__)
settings = get_settings()

# ✅ Load from environment (SECURE)
ALPACA_API_KEY = os.getenv("APCA_API_KEY_ID")
ALPACA_SECRET_KEY = os.getenv("APCA_API_SECRET_KEY")

if not ALPACA_API_KEY or not ALPACA_SECRET_KEY:
    raise Exception("Alpaca API keys not loaded!")

data_client = StockHistoricalDataClient(
    ALPACA_API_KEY,
    ALPACA_SECRET_KEY
)

# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------
def compute_rsi(prices: list, period: int = 14) -> float:
    if len(prices) < period + 1:
        return 50.0
    deltas = np.diff(prices)
    gains = np.where(deltas > 0, deltas, 0)
    losses = np.where(deltas < 0, -deltas, 0)
    avg_gain = np.mean(gains[-period:])
    avg_loss = np.mean(losses[-period:])
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return round(100 - (100 / (1 + rs)), 2)


def compute_moving_averages(prices: list):
    arr = np.array(prices)
    ma20 = float(np.mean(arr[-20:])) if len(arr) >= 20 else float(np.mean(arr))
    ma50 = float(np.mean(arr[-50:])) if len(arr) >= 50 else float(np.mean(arr))
    return round(ma20, 2), round(ma50, 2)


# ---------------------------------------------------------
# Main Prediction Route
# ---------------------------------------------------------
@router.get("/{symbol}")
async def predict_stock(symbol: str, current_user: User = Depends(get_current_user)):
    symbol = symbol.upper().strip()
    cache_key = f"predict:{symbol}"

    cached = cache_get(cache_key)
    if cached:
        return cached

    try:
        # ---------------------------------------------------------
        # 1. Fetch Historical Data (Alpaca)
        # ---------------------------------------------------------
        start_date = datetime.now() - timedelta(days=180)

        bars_req = StockBarsRequest(
            symbol_or_symbols=symbol,
            timeframe=TimeFrame.Day,
            start=start_date
        )

        bars_response = data_client.get_stock_bars(bars_req)

        if not bars_response.data or symbol not in bars_response.data:
            raise HTTPException(status_code=404, detail=f"No data for '{symbol}'")

        hist_bars = bars_response.data[symbol]

        if len(hist_bars) < 30:
            raise HTTPException(status_code=404, detail=f"Not enough data for '{symbol}'")

        prices = [float(bar.close) for bar in hist_bars]
        current_price = round(prices[-1], 2)

        # ---------------------------------------------------------
        # 2. Indicators
        # ---------------------------------------------------------
        rsi = compute_rsi(prices)
        ma20, ma50 = compute_moving_averages(prices)

        # ---------------------------------------------------------
        # 3. AI Prediction (external service or fallback)
        # ---------------------------------------------------------
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{settings.ai_service_url}/predict",
                    json={"symbol": symbol, "prices": prices[-60:]}
                )

                if response.status_code == 200:
                    ai_result = response.json()
                    predicted_price = round(float(ai_result["predicted_price"]), 2)

                    # ✅ FIXED: convert to percentage
                    confidence = round(float(ai_result["confidence"]) * 100, 2)

                else:
                    raise Exception("AI service error")

        except Exception as ai_err:
            logger.warning(f"AI fallback triggered: {ai_err}")

            recent = np.array(prices[-30:])
            x = np.arange(len(recent))

            slope, intercept = np.polyfit(x, recent, 1)
            predicted_price = round(float(intercept + slope * len(recent)), 2)

            trend_strength = abs(slope) / np.std(recent) if np.std(recent) > 0 else 0

            # ✅ FIXED: convert to %
            confidence = round(
                min(0.85, max(0.45, 0.6 + trend_strength * 0.1)) *100, 2
            )

        # ---------------------------------------------------------
        # 4. AI SIGNAL (BETTER LOGIC)
        # ---------------------------------------------------------
        change = predicted_price - current_price
        change_percent = round((change / current_price) , 2)
        direction = "UP" if change > 0 else "DOWN"

        if predicted_price > current_price * 1.01:
            signal = "BUY"
        elif predicted_price < current_price * 0.99:
            signal = "SELL"
        else:
            signal = "HOLD"

        # ---------------------------------------------------------
        # 5. Final Response
        # ---------------------------------------------------------
        result = {
            "symbol": symbol,
            "current_price": current_price,
            "predicted_price": predicted_price,
            "confidence": confidence,   # ✅ 0–100
            "direction": direction,
            "change_percent": change_percent,
            "rsi": rsi,
            "ma20": ma20,
            "ma50": ma50,
            "signal": signal
        }

        cache_set(cache_key, result, ttl=600)
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Prediction error for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")