import React, { useRef, useEffect } from 'react'
import {
  Chart as ChartJS,
  CategoryScale, LinearScale, PointElement, LineElement,
  Title, Tooltip, Legend, Filler
} from 'chart.js'
import { Line } from 'react-chartjs-2'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, Filler)

export default function StockChart({ history, symbol, predictedPrice }) {
  if (!history || history.length === 0) return null

  const recent = history.slice(-90)
  const labels = recent.map((d) => {
    const date = new Date(d.date)
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
  })

  const prices = recent.map((d) => d.close)
  const lastPrice = prices[prices.length - 1]
  const isUp = lastPrice >= prices[0]

  const predLabel = 'Tomorrow'
  const allLabels = [...labels, predLabel]
  const allPrices = [...prices, null]
  const predLine = [...Array(prices.length).fill(null), predictedPrice]

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: { mode: 'index', intersect: false },
    plugins: {
      legend: {
        display: true,
        labels: { color: '#94a3b8', font: { family: 'JetBrains Mono', size: 11 }, boxWidth: 12, padding: 16 },
      },
      tooltip: {
        backgroundColor: '#1e293b',
        borderColor: '#334155',
        borderWidth: 1,
        titleColor: '#94a3b8',
        bodyColor: '#e2e8f0',
        padding: 10,
        callbacks: {
          label: (ctx) => {
            const val = ctx.parsed.y
            return val != null ? ` $${val.toFixed(2)}` : null
          },
        },
      },
    },
    scales: {
      x: {
        grid: { color: '#1e293b', drawBorder: false },
        ticks: {
          color: '#64748b',
          font: { family: 'JetBrains Mono', size: 10 },
          maxTicksLimit: 10,
          maxRotation: 0,
        },
      },
      y: {
        grid: { color: '#1e293b', drawBorder: false },
        ticks: {
          color: '#64748b',
          font: { family: 'JetBrains Mono', size: 11 },
          callback: (v) => `$${v.toFixed(0)}`,
        },
        position: 'right',
      },
    },
  }

  const color = isUp ? '#22c55e' : '#ef4444'
  const colorAlpha = isUp ? 'rgba(34,197,94,0.08)' : 'rgba(239,68,68,0.08)'

  const data = {
    labels: allLabels,
    datasets: [
      {
        label: symbol,
        data: allPrices,
        borderColor: color,
        backgroundColor: colorAlpha,
        borderWidth: 2,
        pointRadius: 0,
        pointHoverRadius: 4,
        fill: true,
        tension: 0.3,
        spanGaps: false,
      },
      {
        label: 'AI Prediction',
        data: predLine,
        borderColor: '#0ea5e9',
        backgroundColor: 'transparent',
        borderWidth: 2,
        borderDash: [6, 3],
        pointRadius: (ctx) => (ctx.dataIndex === allLabels.length - 1 ? 6 : 0),
        pointBackgroundColor: '#0ea5e9',
        pointHoverRadius: 6,
        fill: false,
        tension: 0,
      },
    ],
  }

  return (
    <div style={{ height: '320px' }}>
      <Line options={options} data={data} />
    </div>
  )
}
