import { useId } from 'react'
import './Sparkline.css'

interface SparklineProps {
  data: number[]
  color?: string
  height?: number
  max?: number
}

export function Sparkline({ data, color = 'var(--accent-cyan)', height = 28, max }: SparklineProps) {
  const uid = useId().replace(/:/g, '')
  if (data.length === 0) return <div className="sparkline" style={{ height }} />
  const cap = max ?? Math.max(1, ...data)
  const w = 48
  const h = height - 4
  const padding = 2
  const points = data.slice(-60).map((v, i) => {
    const x = padding + (i / Math.max(1, data.length - 1)) * (w - 2 * padding)
    const y = padding + h - (v / cap) * h
    return `${x},${y}`
  })
  const pathD = points.length ? `M ${points.join(' L ')}` : ''
  const gradId = `spark-fill-${uid}`

  return (
    <div className="sparkline" style={{ height }}>
      <svg width="100%" height={height} viewBox={`0 0 ${w} ${height}`} preserveAspectRatio="none meet">
        {pathD && (
          <>
            <defs>
              <linearGradient id={gradId} x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor={color} stopOpacity={0.4} />
                <stop offset="100%" stopColor={color} stopOpacity={0} />
              </linearGradient>
            </defs>
            <path
              fill={`url(#${gradId})`}
              d={pathD + ` L ${w - padding},${height} L ${padding},${height} Z`}
            />
            <path fill="none" stroke={color} strokeWidth="1.2" d={pathD} />
          </>
        )}
      </svg>
    </div>
  )
}
