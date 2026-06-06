// App.jsx – Main SnapReport application
import React, { useState } from 'react'
import ReportResults from './components/ReportResults'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// Loading steps to display while generating report
const LOADING_STEPS = [
  { icon: '📊', text: 'Loading Redfin national market data...' },
  { icon: '🧮', text: 'Computing local market variance...' },
  { icon: '🤖', text: 'Generating AI market narrative via Groq...' },
  { icon: '📄', text: 'Creating branded PDF report...' },
]

export default function App() {
  const [form, setForm] = useState({
    agent_name: '',
    email: '',
    zip_code: '',
  })
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const [loadingStep, setLoadingStep] = useState(0)

  // Cycle through loading steps for better UX
  const startLoadingCycle = () => {
    let step = 0
    const interval = setInterval(() => {
      step = Math.min(step + 1, LOADING_STEPS.length - 1)
      setLoadingStep(step)
    }, 1800)
    return interval
  }

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value })
    if (error) setError(null)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!form.agent_name.trim() || !form.email.trim() || !form.zip_code.trim()) {
      setError('Please fill in all fields before generating the report.')
      return
    }

    setLoading(true)
    setResult(null)
    setError(null)
    setLoadingStep(0)

    const interval = startLoadingCycle()

    try {
      const response = await fetch(`${API_BASE}/generate-report`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form),
      })

      clearInterval(interval)

      if (!response.ok) {
        const errData = await response.json().catch(() => ({}))
        throw new Error(errData.detail || `Server error: ${response.status}`)
      }

      const data = await response.json()
      setResult(data)
    } catch (err) {
      clearInterval(interval)
      setError(
        err.message.includes('fetch')
          ? 'Cannot connect to backend. Make sure the FastAPI server is running on port 8000.'
          : err.message
      )
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app-wrapper">
      {/* ── Header ── */}
      <header className="header">
        <div className="header-badge">
          <span className="header-badge-dot" />
          Live · Powered by Redfin Data
        </div>

        <h1>
          <span>Snap</span>Report
        </h1>
        <p>Generate AI-powered monthly market reports in seconds</p>

        <div className="powered-by">
          <span className="powered-chip">📊 Redfin Data</span>
          <span className="powered-chip">🤖 Groq AI</span>
          <span className="powered-chip">🏠 Snaphomz</span>
          <span className="powered-chip">📄 ReportLab PDF</span>
        </div>
      </header>

      {/* ── Main ── */}
      <main className="main">

        {/* ── Form Card ── */}
        <div className="form-card">
          <div className="form-card-title">Generate Your Market Report</div>
          <div className="form-card-sub">
            Enter agent details and target area to generate a professional, data-driven market report.
          </div>

          <form onSubmit={handleSubmit} id="report-form" noValidate>
            <div className="form-grid">
              <div className="form-group">
                <label className="form-label" htmlFor="agent_name">Agent Name</label>
                <input
                  id="agent_name"
                  name="agent_name"
                  type="text"
                  className="form-input"
                  placeholder="Jane Smith"
                  value={form.agent_name}
                  onChange={handleChange}
                  disabled={loading}
                  autoComplete="name"
                />
              </div>

              <div className="form-group">
                <label className="form-label" htmlFor="email">Email Address</label>
                <input
                  id="email"
                  name="email"
                  type="email"
                  className="form-input"
                  placeholder="jane@realty.com"
                  value={form.email}
                  onChange={handleChange}
                  disabled={loading}
                  autoComplete="email"
                />
              </div>

              <div className="form-group">
                <label className="form-label" htmlFor="zip_code">Zip Code / Area</label>
                <input
                  id="zip_code"
                  name="zip_code"
                  type="text"
                  className="form-input"
                  placeholder="94025 or Menlo Park, CA"
                  value={form.zip_code}
                  onChange={handleChange}
                  disabled={loading}
                  autoComplete="postal-code"
                />
              </div>
            </div>

            {error && (
              <div className="error-card" role="alert">
                <span>⚠️</span>
                <span>{error}</span>
              </div>
            )}

            <button
              id="generate-btn"
              type="submit"
              className="btn-primary"
              disabled={loading}
            >
              {loading ? (
                <>
                  <span style={{ display: 'inline-block', width: 16, height: 16, border: '2px solid rgba(255,255,255,.4)', borderTopColor: '#fff', borderRadius: '50%', animation: 'spin .7s linear infinite' }} />
                  Generating Report...
                </>
              ) : (
                <>✨ Generate AI Report</>
              )}
            </button>
          </form>
        </div>

        {/* ── Loading Card ── */}
        {loading && (
          <div className="loading-card" role="status" aria-live="polite">
            <div className="spinner" />
            <div className="loading-title">Generating AI Market Report...</div>
            <ul className="loading-steps">
              {LOADING_STEPS.map((step, i) => (
                <li key={i} style={{ opacity: i <= loadingStep ? 1 : 0.35, transition: 'opacity .4s' }}>
                  <span className="step-icon">{step.icon}</span>
                  {step.text}
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* ── Results ── */}
        {result && !loading && (
          <ReportResults
            data={result}
            agentName={form.agent_name}
            zipCode={form.zip_code}
            pdfUrl={result.pdf_url}
          />
        )}
      </main>

      {/* ── Footer ── */}
      <footer className="footer">
        <p>
          SnapReport by <a href="#" target="_blank" rel="noopener noreferrer">Snaphomz</a> · 
          Data sourced from <strong>Redfin Housing Market Data</strong> · 
          AI by <strong>Groq</strong> · Built for real estate agents
        </p>
      </footer>
    </div>
  )
}
