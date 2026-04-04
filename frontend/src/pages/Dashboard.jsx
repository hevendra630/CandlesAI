import React, { useState, useCallback } from 'react'
import { useAuth } from '../hooks/useAuth.jsx'
import { stockAPI } from '../services/api.js'
import StockChart from '../components/StockChart.jsx'
import StatCard from '../components/StatCard.jsx'
import SentimentCard from '../components/SentimentCard.jsx'
import PredictionCard from '../components/PredictionCard.jsx'
import {
  TrendingUp, Search, LogOut, RefreshCw, AlertCircle,
  DollarSign, BarChart2, Activity, ArrowUpRight
} from 'lucide-react'

const POPULAR = ['AAPL', 'TSLA', 'GOOGL', 'MSFT', 'AMZN', 'NVDA', 'META', 'NFLX']

export default function Dashboard() {
  const { user, logout } = useAuth()
  const [symbol, setSymbol] = useState('')
  const [activeSymbol, setActiveSymbol] = useState(null)

  const [stockData, setStockData] = useState(null)
  const [prediction, setPrediction] = useState(null)
  const [sentiment, setSentiment] = useState(null)

  const [loadingStock, setLoadingStock] = useState(false)
  const [loadingPred, setLoadingPred] = useState(false)
  const [loadingSent, setLoadingSent] = useState(false)
  const [error, setError] = useState('')

  const fetchAll = useCallback(async (sym) => {
    const s = sym.toUpperCase().trim()
    if (!s) return
    setError('')
    setActiveSymbol(s)
    setStockData(null)
    setPrediction(null)
    setSentiment(null)

    // Fetch stock data
    setLoadingStock(true)
    try {
      const res = await stockAPI.getStock(s)
      setStockData(res.data)
    } catch (err) {
      setError(err.response?.data?.detail || `Could not load data for "${s}"`)
      setLoadingStock(false)
      return
    } finally {
      setLoadingStock(false)
    }

    // Fetch prediction and sentiment in parallel
    setLoadingPred(true)
    setLoadingSent(true)

    stockAPI.getPrediction(s)
      .then((r) => setPrediction(r.data))
      .catch((e) => console.warn('Prediction error:', e.message))
      .finally(() => setLoadingPred(false))

    stockAPI.getSentiment(s)
      .then((r) => setSentiment(r.data))
      .catch((e) => console.warn('Sentiment error:', e.message))
      .finally(() => setLoadingSent(false))

  }, [])

  const handleSearch = (e) => {
    e.preventDefault()
    if (symbol.trim()) fetchAll(symbol)
  }

  const priceChange = stockData
    ? stockData.current_price - stockData.open_price
    : 0
  const priceChangePct = stockData && stockData.open_price
    ? ((priceChange / stockData.open_price) * 100).toFixed(2)
    : '0.00'
  const isUp = priceChange >= 0

  return (
    <div className="min-h-screen bg-surface-900">
      {/* Navbar */}
      <header className="border-b border-surface-700 bg-surface-800/80 backdrop-blur sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 h-14 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <TrendingUp className="text-brand-400 w-5 h-5" />
            <span className="font-mono font-semibold text-white">CandlesAI</span>
          </div>
          <div className="flex items-center gap-3">
            <span className="text-sm text-slate-400 hidden sm:block">
              Hi, <span className="text-slate-200">{user?.username}</span>
            </span>
            <button onClick={logout} className="flex items-center gap-1.5 text-slate-400 hover:text-white text-sm transition-colors">
              <LogOut className="w-4 h-4" />
              <span className="hidden sm:block">Logout</span>
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8 space-y-6">
        {/* Search */}
        <div className="space-y-3">
          <form onSubmit={handleSearch} className="flex gap-3">
            <div className="relative flex-1 max-w-lg">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
              <input
                type="text"
                value={symbol}
                onChange={(e) => setSymbol(e.target.value.toUpperCase())}
                className="input-field pl-9 font-mono uppercase"
                placeholder="AAPL, TSLA, NVDA..."
              />
            </div>
            <button type="submit" disabled={loadingStock} className="btn-primary flex items-center gap-2">
              {loadingStock
                ? <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                : <Search className="w-4 h-4" />}
              Analyze
            </button>
          </form>

          {/* Popular tickers */}
          <div className="flex flex-wrap gap-2">
            {POPULAR.map((s) => (
              <button
                key={s}
                onClick={() => { setSymbol(s); fetchAll(s) }}
                className={`font-mono text-xs px-3 py-1.5 rounded-lg border transition-all ${
                  activeSymbol === s
                    ? 'border-brand-500 text-brand-400 bg-brand-500/10'
                    : 'border-surface-600 text-slate-400 hover:border-surface-500 hover:text-slate-200'
                }`}
              >
                {s}
              </button>
            ))}
          </div>
        </div>

        {/* Error */}
        {error && (
          <div className="flex items-center gap-2 bg-red-500/10 border border-red-500/30 rounded-lg px-4 py-3 text-red-400 text-sm animate-fade-in">
            <AlertCircle className="w-4 h-4 flex-shrink-0" />
            {error}
          </div>
        )}

        {/* Stock header */}
        {stockData && (
          <div className="flex flex-wrap items-center justify-between gap-4 animate-slide-up">
            <div>
              <div className="flex items-center gap-3">
                <h1 className="text-3xl font-mono font-bold text-white">{stockData.symbol}</h1>
                <span className={`flex items-center gap-1 text-sm font-mono font-semibold px-2 py-0.5 rounded-full ${isUp ? 'text-green-400 bg-green-400/10' : 'text-red-400 bg-red-400/10'}`}>
                  <ArrowUpRight className={`w-3.5 h-3.5 ${!isUp && 'rotate-180'}`} />
                  {priceChangePct}%
                </span>
              </div>
              <p className="text-slate-400 text-sm">{stockData.name}</p>
            </div>
            <div className="text-right">
              <p className="text-4xl font-mono font-bold text-white">${stockData.current_price?.toFixed(2)}</p>
              <p className={`text-sm font-mono ${isUp ? 'text-green-400' : 'text-red-400'}`}>
                {isUp ? '+' : ''}{priceChange.toFixed(2)} today
              </p>
            </div>
          </div>
        )}

        {/* Loading skeleton for stock */}
        {loadingStock && (
          <div className="animate-pulse space-y-4">
            <div className="h-8 bg-surface-700 rounded w-48" />
            <div className="h-4 bg-surface-700 rounded w-32" />
          </div>
        )}

        {/* Stats row */}
        {stockData && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 animate-fade-in">
            <StatCard label="Open" value={`$${stockData.open_price?.toFixed(2)}`} icon={DollarSign} />
            <StatCard label="High" value={`$${stockData.high_price?.toFixed(2)}`} accent="text-green-400" icon={Activity} />
            <StatCard label="Low" value={`$${stockData.low_price?.toFixed(2)}`} accent="text-red-400" icon={Activity} />
            <StatCard
              label="Volume"
              value={stockData.volume > 1e6 ? `${(stockData.volume / 1e6).toFixed(1)}M` : stockData.volume?.toLocaleString()}
              icon={BarChart2}
            />
          </div>
        )}

        {/* Chart */}
        {stockData && (
          <div className="card animate-fade-in">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-sm font-medium text-slate-400 uppercase tracking-wider">6 Month Price History</h2>
              <button
                onClick={() => fetchAll(activeSymbol)}
                className="flex items-center gap-1.5 text-xs text-slate-500 hover:text-slate-300 transition-colors"
              >
                <RefreshCw className="w-3.5 h-3.5" />
                Refresh
              </button>
            </div>
            <StockChart
              history={stockData.history}
              symbol={stockData.symbol}
              predictedPrice={prediction?.predicted_price}
            />
          </div>
        )}

        {/* Prediction + Sentiment */}
        {(stockData || loadingPred || loadingSent) && (
          <div className="grid md:grid-cols-2 gap-4 animate-fade-in">
            <PredictionCard prediction={prediction} loading={loadingPred} />
            <SentimentCard sentiment={sentiment} loading={loadingSent} />
          </div>
        )}

        {/* 52-week range */}
        {stockData?.fifty_two_week_high && (
          <div className="card animate-fade-in">
            <h3 className="text-sm font-medium text-slate-400 uppercase tracking-wider mb-4">52-Week Range</h3>
            <div className="space-y-2">
              <div className="flex justify-between text-sm font-mono">
                <span className="text-red-400">${stockData.fifty_two_week_low?.toFixed(2)}</span>
                <span className="text-green-400">${stockData.fifty_two_week_high?.toFixed(2)}</span>
              </div>
              <div className="h-2 bg-surface-700 rounded-full overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-red-500 via-yellow-500 to-green-500 rounded-full"
                  style={{
                    width: `${Math.round(
                      ((stockData.current_price - stockData.fifty_two_week_low) /
                        (stockData.fifty_two_week_high - stockData.fifty_two_week_low)) * 100
                    )}%`
                  }}
                />
              </div>
              <p className="text-xs text-center text-slate-500">
                Current ${stockData.current_price?.toFixed(2)} · {Math.round(
                  ((stockData.current_price - stockData.fifty_two_week_low) /
                    (stockData.fifty_two_week_high - stockData.fifty_two_week_low)) * 100
                )}% of range
              </p>
            </div>
          </div>
        )}

        {/* Empty state */}
        {!activeSymbol && !loadingStock && (
          <div className="flex flex-col items-center justify-center py-24 text-center animate-fade-in">
            <div className="w-16 h-16 rounded-2xl bg-surface-700 flex items-center justify-center mb-4">
              <TrendingUp className="w-8 h-8 text-brand-400" />
            </div>
            <h2 className="text-xl font-semibold text-white mb-2">Search a stock to begin</h2>
            <p className="text-slate-400 max-w-sm">
              Enter a ticker symbol above or pick from popular stocks to see real-time data, AI predictions, and news sentiment.
            </p>
          </div>
        )}
      </main>
    </div>
  )
}
