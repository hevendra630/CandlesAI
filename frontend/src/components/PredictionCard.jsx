import React from 'react'
import { Brain, ArrowUpRight, ArrowDownRight, Minus } from 'lucide-react'

export default function PredictionCard({ prediction, loading }) {
  if (loading) {
    return (
      <div className="card animate-pulse">
        <div className="h-4 bg-surface-600 rounded w-1/3 mb-4" />
        <div className="h-10 bg-surface-600 rounded w-2/3 mb-3" />
        <div className="h-3 bg-surface-600 rounded w-full mb-1" />
        <div className="h-3 bg-surface-600 rounded w-3/4" />
      </div>
    )
  }

  if (!prediction) return null

  const { predicted_price, current_price, confidence, direction, change_percent, rsi, ma20, ma50, signal } = prediction
  const isUp = direction === 'UP'
  const Arrow = isUp ? ArrowUpRight : ArrowDownRight
  const color = isUp ? 'text-green-400' : 'text-red-400'
  const signalColor = signal === 'BUY' ? 'bg-green-500/20 text-green-400 border-green-500/30' : signal === 'SELL' ? 'bg-red-500/20 text-red-400 border-red-500/30' : 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30'

  return (
    <div className="card space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Brain className="w-4 h-4 text-brand-400" />
          <h3 className="text-sm font-medium text-slate-400 uppercase tracking-wider">AI Prediction</h3>
        </div>
        <span className={`text-xs font-mono font-semibold px-2 py-0.5 rounded-full border ${signalColor}`}>
          {signal}
        </span>
      </div>

      <div className="flex items-end gap-3">
        <p className="text-3xl font-mono font-bold text-white">${predicted_price?.toFixed(2)}</p>
        <div className={`flex items-center gap-0.5 mb-1 ${color}`}>
          <Arrow className="w-4 h-4" />
          <span className="font-mono text-sm font-semibold">{Math.abs(change_percent)}%</span>
        </div>
      </div>

      <p className="text-xs text-slate-500">
        Current: <span className="font-mono text-slate-300">${current_price?.toFixed(2)}</span>
        {' · '}
        Confidence: <span className="font-mono text-brand-400">{Math.round(confidence * 100)}%</span>
      </p>

      {/* Confidence bar */}
      <div className="space-y-1">
        <div className="h-1.5 bg-surface-700 rounded-full overflow-hidden">
          <div
            className="h-full bg-brand-500 rounded-full transition-all duration-700"
            style={{ width: `${Math.round(confidence * 100)}%` }}
          />
        </div>
      </div>

      {/* Technical indicators */}
      <div className="grid grid-cols-3 gap-2 pt-1">
        {[
          { label: 'RSI', value: rsi?.toFixed(1), color: rsi < 30 ? 'text-green-400' : rsi > 70 ? 'text-red-400' : 'text-slate-300' },
          { label: 'MA20', value: `$${ma20?.toFixed(0)}`, color: 'text-slate-300' },
          { label: 'MA50', value: `$${ma50?.toFixed(0)}`, color: 'text-slate-300' },
        ].map((ind) => (
          <div key={ind.label} className="bg-surface-700 rounded-lg p-2 text-center">
            <p className="text-xs text-slate-500 mb-0.5">{ind.label}</p>
            <p className={`font-mono text-sm font-semibold ${ind.color}`}>{ind.value}</p>
          </div>
        ))}
      </div>
    </div>
  )
}
