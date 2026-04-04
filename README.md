# 🤖 CandlesAI — AI-Powered Stock Market Prediction System

A fully dockerized stock prediction platform with JWT authentication, LSTM-based predictions, real-time stock data (via Alpaca/YFinance), and sentiment analysis using HuggingFace models.

---

## 🗂️ Project Structure

candles-ai/
├── backend/          FastAPI — auth, stock, prediction, sentiment APIs  
├── ai_service/       Python ML service — LSTM + HuggingFace NLP  
├── frontend/         React + Vite + Tailwind dashboard  
├── docker-compose.yml  
└── .env  

---

## 🚀 Run Everything (One Command)

# 1. Clone the project
git clone <your-repo>
cd candles-ai

# 2. (Optional) Add your NewsAPI key
# Get one free at https://newsapi.org/register
# Edit .env → NEWS_API_KEY=your_key_here

# 3. Launch all services
docker-compose up --build

First build takes 5–10 min (downloads ML models).

---

## 🌐 Access the Application

Frontend       → http://localhost:3000  
Backend API    → http://localhost:3000/api  
API Docs       → http://localhost:3000/api/docs  

---

## 🧪 API Testing

Signup:
curl -X POST http://localhost:3000/api/auth/signup \
-H "Content-Type: application/json" \
-d '{"email":"test@example.com","username":"trader1","password":"secret123"}'

Login:
curl -X POST http://localhost:3000/api/auth/login \
-H "Content-Type: application/json" \
-d '{"email":"test@example.com","password":"secret123"}'

Get Stock:
curl http://localhost:3000/api/stock/AAPL \
-H "Authorization: Bearer <TOKEN>"

Prediction:
curl http://localhost:3000/api/predict/TSLA \
-H "Authorization: Bearer <TOKEN>"

Sentiment:
curl http://localhost:3000/api/sentiment/NVDA \
-H "Authorization: Bearer <TOKEN>"

---

## 🧠 AI Service

Runs internally on port 8001:

POST /predict   → LSTM prediction (fallback regression)  
POST /sentiment → NLP sentiment analysis  
POST /train     → Train model  

Example:
curl -X POST http://localhost:8001/train \
-H "Content-Type: application/json" \
-d '{"symbol":"AAPL","prices":[150.1,151.2,152.3]}'

---

## ⚙️ Environment Variables

DATABASE_URL   → PostgreSQL connection  
SECRET_KEY     → JWT secret  
NEWS_API_KEY   → News API key  
REDIS_URL      → Redis connection  
AI_SERVICE_URL → AI service URL  

---

## 🐳 Docker Services

postgres   → database  
redis      → caching  
ai_service → ML inference  
backend    → API  
frontend   → UI  

---

## 🛑 Stop Services

docker-compose down  
docker-compose down -v  

---

## 🔐 Security

- Change SECRET_KEY before production  
- JWT expires in 24 hours  
- Passwords hashed using bcrypt  

---

## 📈 Features

- Real-time stock data (Alpaca / Yahoo Finance)  
- LSTM price prediction  
- NLP sentiment analysis  
- JWT authentication  
- Redis caching  
- Microservices architecture  

---

## 📊 Supported Stocks

AAPL, TSLA, GOOGL, MSFT, AMZN, NVDA, etc.

---

## 💡 Summary

CandlesAI is a full-stack AI system where:
- ML models are served via APIs  
- FastAPI backend handles business logic  
- React frontend provides visualization  
- Docker ensures reproducibility and deployment  

---

## 🚀 Future Improvements

- Real-time streaming  
- Advanced models (Transformers, RL)  
- Portfolio optimization  
- Cloud deployment (AWS/Kubernetes)  
