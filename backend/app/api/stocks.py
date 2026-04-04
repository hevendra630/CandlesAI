from fastapi import APIRouter, Depends, HTTPException
from app.core.security import get_current_user
from app.core.cache import cache_get, cache_set
from app.models.user import User
import logging
import time
import os
from datetime import datetime, timedelta

# 🔥 NEW: Alpaca Imports
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest, StockSnapshotRequest
from alpaca.data.timeframe import TimeFrame

router = APIRouter()
logger = logging.getLogger(__name__)

# 🔥 FIX: Paste your new Alpaca keys right here!
import os

ALPACA_API_KEY = os.getenv("APCA_API_KEY_ID")
ALPACA_SECRET_KEY = os.getenv("APCA_API_SECRET_KEY")

if not ALPACA_API_KEY or not ALPACA_SECRET_KEY:
    raise Exception("Alpaca API keys not loaded!")

# Initialize the Alpaca Client
data_client = StockHistoricalDataClient(
    ALPACA_API_KEY,
    ALPACA_SECRET_KEY
)
def safe_float(val, default=0.0):
    try:
        if val is None:
            return default
        f = float(val)
        return f if f == f else default
    except Exception:
        return default

def safe_int(val, default=0):
    try:
        return int(val) if val is not None else default
    except Exception:
        return default


@router.get("/{symbol}")
def get_stock(symbol: str, current_user: User = Depends(get_current_user)):
    symbol = symbol.upper().strip()
    cache_key = f"stock:{symbol}"
    cached = cache_get(cache_key)
    if cached:
        return cached

    last_error = None
    for attempt in range(3):
        try:
            if attempt > 0:
                time.sleep(2)

            # ---------------------------------------------------------
            # 1. Fetch Historical Data
            # ---------------------------------------------------------
            start_date = datetime.now() - timedelta(days=180)
            bars_req = StockBarsRequest(
                symbol_or_symbols=symbol,
                timeframe=TimeFrame.Day,
                start=start_date
            )
            bars_response = data_client.get_stock_bars(bars_req)
            
            hist_bars = []
            if bars_response.data and symbol in bars_response.data:
                hist_bars = bars_response.data[symbol]

            history_data = []
            for bar in hist_bars:
                history_data.append({
                    "date": bar.timestamp.strftime("%Y-%m-%d"),
                    "open": safe_float(bar.open),
                    "high": safe_float(bar.high),
                    "low": safe_float(bar.low),
                    "close": safe_float(bar.close),
                    "price": safe_float(bar.close),
                    "volume": safe_int(bar.volume),
                })

            # ---------------------------------------------------------
            # 2. Fetch Live Snapshot
            # ---------------------------------------------------------
            snap_req = StockSnapshotRequest(symbol_or_symbols=symbol)
            snapshot = data_client.get_stock_snapshot(snap_req)
            
            if symbol not in snapshot:
                raise Exception("No snapshot data returned for this symbol.")
                
            stock_snap = snapshot[symbol]
            current_price = safe_float(stock_snap.latest_trade.price if stock_snap.latest_trade else None)
            last_open = safe_float(stock_snap.daily_bar.open)
            last_high = safe_float(stock_snap.daily_bar.high)
            last_low = safe_float(stock_snap.daily_bar.low)
            last_vol = safe_int(stock_snap.daily_bar.volume)

            # ---------------------------------------------------------
            # 3. AI PREDICTION (1 DAY)
            # ---------------------------------------------------------
            prediction_data = []
            predicted_price = None

            if history_data:
                last_price = history_data[-1]["close"]

                predicted_price = round(last_price * 1.01, 2)

                prediction_data.append({
                    "date": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
                    "price": predicted_price
                })

            # ---------------------------------------------------------
            # 4. 🔥 AI SIGNAL (BUY / SELL / HOLD)
            # ---------------------------------------------------------
            ai_signal = "HOLD"
            confidence = 50

            if history_data and predicted_price:
                last_price = history_data[-1]["close"]
                change_pct = ((predicted_price - last_price) / last_price) * 100

                if change_pct > 1:
                    ai_signal = "BUY"
                    confidence = min(90, 60 + abs(change_pct) * 5)
                elif change_pct < -1:
                    ai_signal = "SELL"
                    confidence = min(90, 60 + abs(change_pct) * 5)
                else:
                    ai_signal = "HOLD"
                    confidence = 50

            # ---------------------------------------------------------
            # 5. Final Response
            # ---------------------------------------------------------
            result = {
                "symbol": symbol,
                "name": symbol,
                "current_price": round(current_price, 2),
                "open_price": round(last_open, 2),
                "high_price": round(last_high, 2),
                "low_price": round(last_low, 2),
                "volume": last_vol,
                "market_cap": None,
                "pe_ratio": None,
                "fifty_two_week_high": None,
                "fifty_two_week_low": None,
                "history": history_data,
                "prediction": prediction_data,

                # 🔥 THIS WILL BRING BACK YOUR BOX
                "ai_prediction": {
                    "signal": ai_signal,
                    "confidence": round(confidence, 2)
                }
            }

            cache_set(cache_key, result, ttl=300)
            return result

        except HTTPException:
            raise
        except Exception as e:
            last_error = e
            logger.warning(f"Attempt {attempt+1} failed for {symbol}: {e}")
            continue

    raise HTTPException(
        status_code=500,
        detail=f"Failed to fetch data for '{symbol}' using Alpaca API. Error: {last_error}"
    )