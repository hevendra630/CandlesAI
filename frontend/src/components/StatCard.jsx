import React from 'react'

export default function StatCard({ label, value, sub, accent, icon: Icon }) {
  return (
    <div className="card flex flex-col gap-2 hover:border-surface-500 transition-colors">
      <div className="flex items-center justify-between">
        <span className="text-xs text-slate-500 uppercase tracking-wider font-medium">{label}</span>
        {Icon && <Icon className="w-4 h-4 text-slate-600" />}
      </div>
      <p className={`text-2xl font-mono font-semibold ${accent || 'text-white'}`}>{value}</p>
      {sub && <p className="text-xs text-slate-500">{sub}</p>}
    </div>
  )
}
