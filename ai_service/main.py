from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import numpy as np
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI Stock Prediction Service", version="1.0.0")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# Lazy-load heavy models
_lstm_model = None
_sentiment_pipeline = None


def get_lstm_model():
    global _lstm_model
    if _lstm_model is None:
        try:
            from tensorflow import keras  # noqa
            model_path = "/app/models/lstm_model.h5"
            if os.path.exists(model_path):
                _lstm_model = keras.models.load_model(model_path)
                logger.info("LSTM model loaded from disk")
            else:
                logger.info("No saved model found, will use statistical fallback")
        except Exception as e:
            logger.warning(f"Could not load LSTM model: {e}")
    return _lstm_model


def get_sentiment_pipeline():
    global _sentiment_pipeline
    if _sentiment_pipeline is None:
        try:
            from transformers import pipeline
            _sentiment_pipeline = pipeline(
                "sentiment-analysis",
                model="distilbert-base-uncased-finetuned-sst-2-english",
                truncation=True,
                max_length=512,
            )
            logger.info("Sentiment pipeline loaded")
        except Exception as e:
            logger.warning(f"Could not load sentiment model: {e}")
    return _sentiment_pipeline


class PredictRequest(BaseModel):
    symbol: str
    prices: List[float]


class SentimentRequest(BaseModel):
    texts: List[str]


@app.get("/")
def root():
    return {"status": "ok", "service": "AI Stock Prediction"}


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/predict")
def predict(req: PredictRequest):
    prices = req.prices
    if len(prices) < 10:
        return {"predicted_price": prices[-1], "confidence": 0.5}

    model = get_lstm_model()

    if model is not None:
        try:
            import numpy as np
            arr = np.array(prices[-60:], dtype=np.float32)
            min_p, max_p = arr.min(), arr.max()
            normalized = (arr - min_p) / (max_p - min_p + 1e-8)
            x = normalized.reshape(1, -1, 1)
            if x.shape[1] < 60:
                pad = np.zeros((1, 60 - x.shape[1], 1))
                x = np.concatenate([pad, x], axis=1)
            pred_norm = float(model.predict(x, verbose=0)[0][0])
            predicted_price = round(float(pred_norm * (max_p - min_p) + min_p), 2)
            confidence = 0.78
            return {"predicted_price": predicted_price, "confidence": confidence}
        except Exception as e:
            logger.error(f"LSTM prediction error: {e}")

    # Statistical fallback: weighted linear regression on last 30 days
    arr = np.array(prices[-30:])
    x = np.arange(len(arr))
    weights = np.exp(np.linspace(0, 1, len(arr)))  # exponential weighting
    coeffs = np.polyfit(x, arr, 1, w=weights)
    predicted = float(coeffs[0] * len(arr) + coeffs[1])
    predicted_price = round(predicted, 2)

    # Confidence based on R²
    y_pred = np.polyval(coeffs, x)
    ss_res = np.sum((arr - y_pred) ** 2)
    ss_tot = np.sum((arr - np.mean(arr)) ** 2)
    r2 = 1 - ss_res / (ss_tot + 1e-8)
    confidence = round(max(0.40, min(0.82, 0.5 + r2 * 0.32)), 3)

    return {"predicted_price": predicted_price, "confidence": confidence}


@app.post("/sentiment")
def analyze_sentiment(req: SentimentRequest):
    if not req.texts:
        return {"label": "NEUTRAL", "score": 0.5}

    pipeline = get_sentiment_pipeline()

    if pipeline is not None:
        try:
            results = pipeline(req.texts[:10])
            scores = []
            for r in results:
                if r["label"] == "POSITIVE":
                    scores.append(r["score"])
                else:
                    scores.append(1 - r["score"])
            avg_score = float(np.mean(scores))
            label = "POSITIVE" if avg_score > 0.6 else ("NEGATIVE" if avg_score < 0.4 else "NEUTRAL")
            return {"label": label, "score": round(avg_score, 3)}
        except Exception as e:
            logger.error(f"Sentiment pipeline error: {e}")

    # Keyword fallback
    positive = ["surge", "gain", "beat", "record", "growth", "profit", "soar", "rise", "bullish", "strong"]
    negative = ["drop", "fall", "miss", "loss", "crash", "decline", "plunge", "risk", "bear", "weak"]
    text = " ".join(req.texts).lower()
    pos = sum(text.count(w) for w in positive)
    neg = sum(text.count(w) for w in negative)
    total = pos + neg
    score = round(0.5 + (pos - neg) / (total * 2), 3) if total > 0 else 0.5
    label = "POSITIVE" if score > 0.6 else ("NEGATIVE" if score < 0.4 else "NEUTRAL")
    return {"label": label, "score": score}


@app.post("/train")
def train_model(req: PredictRequest):
    """Train or fine-tune the LSTM model on provided data"""
    try:
        import tensorflow as tf
        from tensorflow import keras

        prices = np.array(req.prices, dtype=np.float32)
        if len(prices) < 70:
            return {"status": "error", "message": "Need at least 70 data points to train"}

        min_p, max_p = prices.min(), prices.max()
        normalized = (prices - min_p) / (max_p - min_p + 1e-8)

        seq_len = 60
        X, y = [], []
        for i in range(len(normalized) - seq_len):
            X.append(normalized[i:i + seq_len])
            y.append(normalized[i + seq_len])

        X = np.array(X).reshape(-1, seq_len, 1)
        y = np.array(y)

        model = keras.Sequential([
            keras.layers.LSTM(64, return_sequences=True, input_shape=(seq_len, 1)),
            keras.layers.Dropout(0.2),
            keras.layers.LSTM(32),
            keras.layers.Dropout(0.2),
            keras.layers.Dense(16, activation="relu"),
            keras.layers.Dense(1),
        ])
        model.compile(optimizer="adam", loss="mse")
        model.fit(X, y, epochs=10, batch_size=32, verbose=0)

        os.makedirs("/app/models", exist_ok=True)
        model.save("/app/models/lstm_model.h5")
        global _lstm_model
        _lstm_model = model
        return {"status": "success", "message": "Model trained and saved"}
    except Exception as e:
        logger.error(f"Training error: {e}")
        return {"status": "error", "message": str(e)}
