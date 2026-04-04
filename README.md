# 🤖 StockAI — AI-Powered Stock Market Prediction System

A fully dockerized stock prediction platform with JWT auth, LSTM predictions, real-time data via yfinance, and HuggingFace sentiment analysis.

---

## 🗂️ Project Structure

```
stock-ai/
├── backend/          FastAPI — auth, stock, prediction, sentiment APIs
├── ai_service/       Python ML service — LSTM + HuggingFace NLP
├── frontend/         React + Vite + Tailwind dashboard
├── docker-compose.yml
└── .env
```

---

## 🚀 Run Everything (One Command)

```bash
# 1. Clone / unzip the project
cd stock-ai

# 2. (Optional) Add your NewsAPI key for real news headlines
#    Get one free at https://newsapi.org/register
#    Edit .env → NEWS_API_KEY=your_key_here

# 3. Launch
docker-compose up --build
```

**First build takes 5–10 min** (downloads ML models). Subsequent starts are fast.

| Service    | URL                        |
|------------|----------------------------|
| Frontend   | http://localhost:3000       |
| Backend API| http://localhost:3000/api   |
| API Docs   | http://localhost:3000/api/docs |

---

## 🧪 Testing the API

### 1. Signup
```bash
curl -X POST http://localhost:3000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","username":"trader1","password":"secret123"}'
```
Expected: `{"access_token":"eyJ...","token_type":"bearer","user":{...}}`

### 2. Login
```bash
curl -X POST http://localhost:3000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"secret123"}'

# Save the token:
TOKEN="eyJ..."
```

### 3. Get Stock Data
```bash
curl http://localhost:3000/api/stock/AAPL \
  -H "Authorization: Bearer $TOKEN"
```

### 4. Get AI Prediction
```bash
curl http://localhost:3000/api/predict/TSLA \
  -H "Authorization: Bearer $TOKEN"
```
Expected: `{"symbol":"TSLA","current_price":...,"predicted_price":...,"confidence":0.73,"direction":"UP",...}`

### 5. Get News Sentiment
```bash
curl http://localhost:3000/api/sentiment/NVDA \
  -H "Authorization: Bearer $TOKEN"
```
Expected: `{"sentiment_label":"POSITIVE","sentiment_score":0.72,...}`

---

## 🔍 Interactive API Docs

Open **http://localhost:3000/api/docs** in your browser — full Swagger UI with try-it-out for every endpoint.

---

## 🧠 AI Service

The AI service runs separately at port 8001 (internal). It provides:

- **`POST /predict`** — LSTM model (falls back to weighted linear regression if no trained model)
- **`POST /sentiment`** — DistilBERT sentiment pipeline (falls back to keyword scoring)
- **`POST /train`** — Train/retrain the LSTM on new price data

To train the LSTM model with real data:
```bash
# Get AAPL historical prices and train
curl -X POST http://localhost:8001/train \
  -H "Content-Type: application/json" \
  -d '{"symbol":"AAPL","prices":[150.1,151.2,...]}'
```

---

## ⚙️ Environment Variables (`.env`)

| Variable        | Default                          | Description                    |
|-----------------|----------------------------------|--------------------------------|
| `DATABASE_URL`  | postgres://... (auto-set)        | PostgreSQL connection string   |
| `SECRET_KEY`    | change-me-...                    | JWT signing key (change this!) |
| `NEWS_API_KEY`  | (empty)                          | newsapi.org key for headlines  |
| `REDIS_URL`     | redis://redis:6379               | Redis connection               |
| `AI_SERVICE_URL`| http://ai_service:8001           | Internal AI service URL        |

---

## 🐳 Docker Services

| Container          | Image           | Port  | Purpose                  |
|--------------------|-----------------|-------|--------------------------|
| stockai_postgres   | postgres:15     | —     | User data + sessions     |
| stockai_redis      | redis:7         | —     | API response cache       |
| stockai_ai         | custom python   | 8001  | LSTM + NLP inference     |
| stockai_backend    | custom python   | 8000  | FastAPI REST API         |
| stockai_frontend   | nginx + react   | 3000  | React SPA                |

---

## 🛑 Stopping

```bash
docker-compose down          # Stop containers
docker-compose down -v       # Stop + delete DB data
```

---

## 🔐 Security Notes

- Change `SECRET_KEY` in `.env` before any production use
- JWT tokens expire after 24 hours
- Passwords are hashed with bcrypt
- Redis cache: stock data cached 5min, predictions 10min, sentiment 30min

---

## 📈 Supported Tickers

Any ticker supported by Yahoo Finance works: `AAPL`, `TSLA`, `GOOGL`, `MSFT`, `AMZN`, `NVDA`, `META`, `NFLX`, `AMD`, `INTC`, `BABA`, `UBER`, and thousands more.
