import React from 'react'
import { MessageSquare, TrendingUp, TrendingDown, Minus } from 'lucide-react'

export default function SentimentCard({ sentiment, loading }) {
  if (loading) {
    return (
      <div className="card animate-pulse">
        <div className="h-4 bg-surface-600 rounded w-1/3 mb-4" />
        <div className="h-8 bg-surface-600 rounded w-1/2 mb-2" />
        <div className="h-3 bg-surface-600 rounded w-full mb-1" />
        <div className="h-3 bg-surface-600 rounded w-4/5" />
      </div>
    )
  }

  if (!sentiment) return null

  const { sentiment_label, sentiment_score, articles_analyzed, headlines } = sentiment
  const isPositive = sentiment_label === 'POSITIVE'
  const isNegative = sentiment_label === 'NEGATIVE'

  const Icon = isPositive ? TrendingUp : isNegative ? TrendingDown : Minus
  const color = isPositive ? 'text-green-400' : isNegative ? 'text-red-400' : 'text-yellow-400'
  const bg = isPositive ? 'bg-green-400/10 border-green-400/20' : isNegative ? 'bg-red-400/10 border-red-400/20' : 'bg-yellow-400/10 border-yellow-400/20'

  const pct = Math.round(sentiment_score * 100)

  return (
    <div className="card space-y-4">
      <div className="flex items-center gap-2">
        <MessageSquare className="w-4 h-4 text-slate-500" />
        <h3 className="text-sm font-medium text-slate-400 uppercase tracking-wider">News Sentiment</h3>
      </div>

      <div className="flex items-center gap-3">
        <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full border ${bg}`}>
          <Icon className={`w-4 h-4 ${color}`} />
          <span className={`font-mono font-semibold text-sm ${color}`}>{sentiment_label}</span>
        </div>
        <span className="font-mono text-2xl font-semibold text-white">{pct}%</span>
      </div>

      {/* Score bar */}
      <div className="space-y-1">
        <div className="h-2 bg-surface-700 rounded-full overflow-hidden">
          <div
            className={`h-full rounded-full transition-all duration-700 ${isPositive ? 'bg-green-400' : isNegative ? 'bg-red-400' : 'bg-yellow-400'}`}
            style={{ width: `${pct}%` }}
          />
        </div>
        <p className="text-xs text-slate-500">{articles_analyzed} articles analyzed</p>
      </div>

      {headlines && headlines.length > 0 && (
        <div className="space-y-2">
          <p className="text-xs text-slate-500 uppercase tracking-wider">Latest Headlines</p>
          {headlines.slice(0, 3).map((h, i) => (
            <div key={i} className="text-xs text-slate-400 border-l-2 border-surface-600 pl-2 leading-relaxed truncate">
              {h.title}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
