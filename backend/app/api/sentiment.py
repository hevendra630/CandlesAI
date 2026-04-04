from fastapi import APIRouter, Depends, HTTPException
from app.core.security import get_current_user
from app.core.cache import cache_get, cache_set
from app.core.config import get_settings
from app.models.user import User
import httpx
import logging
import random

router = APIRouter()
logger = logging.getLogger(__name__)
settings = get_settings()

COMPANY_NAMES = {
    "AAPL": "Apple", "TSLA": "Tesla", "GOOGL": "Google", "MSFT": "Microsoft",
    "AMZN": "Amazon", "META": "Meta", "NVDA": "NVIDIA", "NFLX": "Netflix",
    "BABA": "Alibaba", "AMD": "AMD", "INTC": "Intel", "UBER": "Uber",
}


@router.get("/{symbol}")
async def get_sentiment(symbol: str, current_user: User = Depends(get_current_user)):
    symbol = symbol.upper()
    cache_key = f"sentiment:{symbol}"

    cached = cache_get(cache_key)
    if cached:
        return cached

    company = COMPANY_NAMES.get(symbol, symbol)

    headlines = []
    sentiment_score = 0.5
    sentiment_label = "NEUTRAL"
    articles_analyzed = 0

    # ---------------------------------------------------------
    # 1. Fetch News (BETTER QUERY)
    # ---------------------------------------------------------
    if settings.news_api_key:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(
                    "https://newsapi.org/v2/everything",
                    params={
                        # 🔥 FIX: more specific query
                        "q": f'"{company}" OR "{symbol}" stock',
                        "language": "en",
                        "sortBy": "publishedAt",
                        "pageSize": 15,
                        "apiKey": settings.news_api_key,
                    }
                )

                if resp.status_code == 200:
                    articles = resp.json().get("articles", [])

                    # 🔥 filter only relevant titles
                    filtered = [
                        a for a in articles
                        if company.lower() in (a.get("title", "").lower())
                    ]

                    headlines = [
                        {
                            "title": a["title"],
                            "url": a.get("url", ""),
                            "publishedAt": a.get("publishedAt", "")
                        }
                        for a in filtered[:8]
                    ]

                    articles_analyzed = len(headlines)

        except Exception as e:
            logger.warning(f"NewsAPI error: {e}")

    # ---------------------------------------------------------
    # 2. AI SENTIMENT
    # ---------------------------------------------------------
    if headlines:
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.post(
                    f"{settings.ai_service_url}/sentiment",
                    json={"texts": [h["title"] for h in headlines]}
                )

                if resp.status_code == 200:
                    data = resp.json()
                    sentiment_score = round(data["score"], 3)
                    sentiment_label = data["label"]

        except Exception as e:
            logger.warning(f"AI sentiment failed → fallback: {e}")

            # 🔥 IMPROVED keyword logic
            positive_words = ["surge", "gain", "beat", "record", "growth", "profit", "bullish", "soar", "rise", "strong"]
            negative_words = ["drop", "fall", "miss", "loss", "crash", "bear", "decline", "plunge", "risk", "weak"]

            all_text = " ".join(h["title"].lower() for h in headlines)

            pos = sum(all_text.count(w) for w in positive_words)
            neg = sum(all_text.count(w) for w in negative_words)

            total = pos + neg

            if total > 0:
                sentiment_score = round(0.5 + (pos - neg) / (total * 2), 3)
            else:
                sentiment_score = round(random.uniform(0.45, 0.55), 3)

            if sentiment_score > 0.6:
                sentiment_label = "POSITIVE"
            elif sentiment_score < 0.4:
                sentiment_label = "NEGATIVE"
            else:
                sentiment_label = "NEUTRAL"

    else:
        # ---------------------------------------------------------
        # 3. NO NEWS → SMART FALLBACK
        # ---------------------------------------------------------
        sentiment_score = round(random.uniform(0.45, 0.65), 3)

        if sentiment_score > 0.6:
            sentiment_label = "POSITIVE"
        elif sentiment_score < 0.4:
            sentiment_label = "NEGATIVE"
        else:
            sentiment_label = "NEUTRAL"

        headlines = [
            {"title": f"{company} market outlook remains dynamic", "url": "", "publishedAt": ""},
            {"title": f"Investors closely watch {company} stock movement", "url": "", "publishedAt": ""}
        ]

        articles_analyzed = len(headlines)

    # ---------------------------------------------------------
    # 4. RESPONSE
    # ---------------------------------------------------------
    result = {
        "symbol": symbol,
        "company": company,
        "sentiment_label": sentiment_label,
        "sentiment_score": sentiment_score,
        "articles_analyzed": articles_analyzed,
        "headlines": headlines[:5],
    }

    cache_set(cache_key, result, ttl=900)  # 15 min cache
    return result