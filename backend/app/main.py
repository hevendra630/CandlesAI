from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth, stocks, predictions, sentiment
from app.core.database import engine, Base
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Stock Prediction API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,  # 🔥 FIXED: Must be False when allow_origins is "*"
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(stocks.router, prefix="/stock", tags=["Stocks"])
app.include_router(predictions.router, prefix="/predict", tags=["Predictions"])
app.include_router(sentiment.router, prefix="/sentiment", tags=["Sentiment"])


@app.get("/")
def root():
    return {"status": "ok", "message": "AI Stock Prediction API is running"}


@app.get("/health")
def health():
    return {"status": "healthy"}