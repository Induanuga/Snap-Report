// StatCard.jsx – Reusable metric card component
import React from 'react'

/**
 * @param {string} icon - emoji icon
 * @param {string} label - metric label
 * @param {string} value - primary display value
 * @param {string|null} change - YOY change string (e.g. "+2.37%")
 * @param {string} accentColor - CSS color for the top border accent
 */
export default function StatCard({ icon, label, value, change, accentColor = '#2563EB' }) {
  const changeClass = !change
    ? ''
    : change.startsWith('+') || change.startsWith('▲') || parseFloat(change) > 0
      ? 'positive'
      : change.startsWith('-') || change.startsWith('▼') || parseFloat(change) < 0
        ? 'negative'
        : 'neutral'

  return (
    <div className="stat-card" style={{ '--stat-accent': accentColor }}>
      <span className="stat-icon">{icon}</span>
      <div className="stat-label">{label}</div>
      <div className="stat-value">{value}</div>
      {change && (
        <span className={`stat-change ${changeClass}`}>
          {change} YOY
        </span>
      )}
    </div>
  )
}
