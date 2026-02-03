import './MetricCard.css'

interface MetricCardProps {
  label: string
  value: string
  sub: string
}

export function MetricCard({ label, value, sub }: MetricCardProps) {
  return (
    <div className="metric-card">
      <span className="metric-label">{label}</span>
      <span className="metric-value">{value}</span>
      <span className="metric-sub">{sub}</span>
    </div>
  )
}
