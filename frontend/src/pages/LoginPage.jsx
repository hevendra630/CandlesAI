import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth.jsx'
import { TrendingUp, Eye, EyeOff, AlertCircle } from 'lucide-react'

export default function LoginPage() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState({ email: '', password: '' })
  const [showPass, setShowPass] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await login(form.email, form.password)
      navigate('/dashboard')
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex">
      {/* Left panel */}
      <div className="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-surface-800 via-surface-900 to-[#020817] flex-col justify-between p-12 relative overflow-hidden">
        <div className="absolute inset-0 opacity-20"
          style={{ backgroundImage: 'radial-gradient(circle at 20% 80%, #0ea5e9 0%, transparent 50%), radial-gradient(circle at 80% 20%, #6366f1 0%, transparent 50%)' }}
        />
        <div className="relative">
          <div className="flex items-center gap-2 mb-16">
            <TrendingUp className="text-brand-400 w-7 h-7" />
            <span className="font-mono text-xl font-semibold text-white">CandlesAI</span>
          </div>
          <h1 className="text-4xl font-bold text-white leading-tight mb-4">
            Predict markets<br />with intelligence.
          </h1>
          <p className="text-slate-400 text-lg">
            LSTM-powered predictions combined with real-time sentiment analysis.
          </p>
        </div>
        <div className="relative grid grid-cols-2 gap-3">
          {[
            { label: 'Accuracy', value: '78%', sub: 'avg prediction' },
            { label: 'Latency', value: '<300ms', sub: 'avg response' },
            { label: 'Models', value: 'LSTM + NLP', sub: 'dual engine' },
            { label: 'Data', value: 'Real-time', sub: 'via yfinance' },
          ].map((s) => (
            <div key={s.label} className="bg-white/5 border border-white/10 rounded-xl p-4">
              <p className="text-brand-400 font-mono font-semibold text-lg">{s.value}</p>
              <p className="text-white text-sm font-medium">{s.label}</p>
              <p className="text-slate-500 text-xs">{s.sub}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Right panel */}
      <div className="flex-1 flex items-center justify-center p-8">
        <div className="w-full max-w-md animate-fade-in">
          <div className="flex items-center gap-2 mb-8 lg:hidden">
            <TrendingUp className="text-brand-400 w-6 h-6" />
            <span className="font-mono text-lg font-semibold">CandlesAI</span>
          </div>

          <h2 className="text-2xl font-bold text-white mb-1">Welcome back</h2>
          <p className="text-slate-400 mb-8">Sign in to your account</p>

          {error && (
            <div className="flex items-center gap-2 bg-red-500/10 border border-red-500/30 rounded-lg px-4 py-3 mb-6 text-red-400 text-sm">
              <AlertCircle className="w-4 h-4 flex-shrink-0" />
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm text-slate-400 mb-1.5">Email</label>
              <input
                type="email"
                required
                className="input-field"
                placeholder="you@example.com"
                value={form.email}
                onChange={(e) => setForm({ ...form, email: e.target.value })}
              />
            </div>

            <div>
              <label className="block text-sm text-slate-400 mb-1.5">Password</label>
              <div className="relative">
                <input
                  type={showPass ? 'text' : 'password'}
                  required
                  className="input-field pr-10"
                  placeholder="••••••••"
                  value={form.password}
                  onChange={(e) => setForm({ ...form, password: e.target.value })}
                />
                <button
                  type="button"
                  onClick={() => setShowPass(!showPass)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300"
                >
                  {showPass ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            <button type="submit" disabled={loading} className="btn-primary w-full mt-2">
              {loading ? (
                <span className="flex items-center justify-center gap-2">
                  <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  Signing in...
                </span>
              ) : 'Sign In'}
            </button>
          </form>

          <p className="text-slate-500 text-sm text-center mt-6">
            Don't have an account?{' '}
            <Link to="/signup" className="text-brand-400 hover:text-brand-300 font-medium">
              Sign up free
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}
