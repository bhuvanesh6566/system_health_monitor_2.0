import {
  ComposedChart,
  Line,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts'
import './ChartsRow.css'

interface DataPoint {
  time: string
  cpu: number
  algo_ms: number
}

interface ChartsRowProps {
  cpuData: { time: string; cpu: number }[]
  algoData: { time: string; algo_ms: number }[]
}

function mergeData(
  cpuData: { time: string; cpu: number }[],
  algoData: { time: string; algo_ms: number }[]
): DataPoint[] {
  const len = Math.min(cpuData.length, algoData.length)
  if (len === 0) return []
  return Array.from({ length: len }, (_, i) => ({
    time: cpuData[i].time,
    cpu: cpuData[i].cpu,
    algo_ms: algoData[i]?.algo_ms ?? 0,
  }))
}

export function ChartsRow({ cpuData, algoData }: ChartsRowProps) {
  const data = mergeData(cpuData, algoData)

  return (
    <div className="chart-card chart-card--single">
      <h3 className="chart-title">Performance trends — CPU & algorithm latency</h3>
      <div className="chart-legend-inline">
        <span className="legend-item legend-item--cpu">CPU %</span>
        <span className="legend-item legend-item--algo">Latency (ms)</span>
      </div>
      <div className="chart-inner">
        <ResponsiveContainer width="100%" height={320}>
          <ComposedChart data={data} margin={{ top: 16, right: 56, left: 8, bottom: 8 }}>
            <defs>
              <linearGradient id="algoGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="var(--accent-magenta)" stopOpacity={0.4} />
                <stop offset="100%" stopColor="var(--accent-magenta)" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
            <XAxis
              dataKey="time"
              stroke="var(--text-muted)"
              fontSize={11}
              tickLine={false}
              axisLine={{ stroke: 'var(--border)' }}
            />
            <YAxis
              yAxisId="left"
              orientation="left"
              stroke="var(--accent-cyan)"
              fontSize={11}
              tickLine={false}
              axisLine={{ stroke: 'var(--border)' }}
              domain={[0, 100]}
              tickFormatter={(v) => `${v}%`}
            />
            <YAxis
              yAxisId="right"
              orientation="right"
              stroke="var(--accent-magenta)"
              fontSize={11}
              tickLine={false}
              axisLine={{ stroke: 'var(--border)' }}
              tickFormatter={(v) => `${v}`}
            />
            <Tooltip
              contentStyle={{
                background: 'var(--bg-elevated)',
                border: '1px solid var(--border)',
                borderRadius: 10,
                boxShadow: '0 8px 24px rgba(0,0,0,0.4)',
              }}
              labelStyle={{ color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}
              formatter={(value: number, name: string) => {
                if (name === 'cpu') return [value, 'CPU %']
                return [value, 'Latency (ms)']
              }}
              labelFormatter={(label) => `Time: ${label}`}
            />
            <ReferenceLine yAxisId="left" y={80} stroke="var(--accent-cyan)" strokeDasharray="4 4" strokeOpacity={0.5} />
            <Area
              yAxisId="right"
              type="monotone"
              dataKey="algo_ms"
              fill="url(#algoGrad)"
              stroke="var(--accent-magenta)"
              strokeWidth={2}
            />
            <Line
              yAxisId="left"
              type="monotone"
              dataKey="cpu"
              stroke="var(--accent-cyan)"
              strokeWidth={2.5}
              dot={false}
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
