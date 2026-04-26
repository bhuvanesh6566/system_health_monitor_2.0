import { useEffect, useState, useCallback } from 'react'
import { fetchPerformance } from '../api'
import type { PerformanceSnapshot } from '../types'
import { Sparkline } from './Sparkline'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Area,
  AreaChart,
} from 'recharts'
import './PerformanceView.css'

const REFRESH_MS = 1000
const REFRESH_MS_PRELOAD = 3000
const HISTORY_LEN = 60

export type ResourceId =
  | 'cpu'
  | 'memory'
  | `disk-${number}`
  | `network-${string}`
  | 'gpu'

interface HistoryPoint {
  time: string
  value: number
  send_kbps?: number
  recv_kbps?: number
}

function formatTime() {
  return new Date().toLocaleTimeString('en-GB', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false,
  })
}

function buildResourceList(perf: PerformanceSnapshot | null): { id: ResourceId; label: string; value: string; color: string }[] {
  if (!perf) return []
  const list: { id: ResourceId; label: string; value: string; color: string }[] = [
    { id: 'cpu', label: 'CPU', value: `${perf.cpu.percent}%`, color: 'var(--accent-cyan)' },
    { id: 'memory', label: 'Memory', value: `${perf.memory.used_gb} / ${perf.memory.total_gb} GB`, color: 'var(--accent-cyan)' },
  ]
  perf.disks.forEach((d, i) => {
    list.push({
      id: `disk-${i}`,
      label: `Disk ${i} (${d.name})`,
      value: `${d.percent}%`,
      color: '#22c55e',
    })
  })
  perf.network.forEach((n) => {
    list.push({
      id: `network-${n.name}`,
      label: n.name,
      value: `S: ${n.send_kbps} R: ${n.recv_kbps} Kbps`,
      color: '#d946ef',
    })
  })
  if (perf.gpu) {
    list.push({
      id: 'gpu',
      label: `GPU 0`,
      value: `${perf.gpu.utilization_percent}%`,
      color: '#a855f7',
    })
  }
  return list
}

interface PerformanceViewProps {
  isActive: boolean
}

export function PerformanceView({ isActive }: PerformanceViewProps) {
  const [perf, setPerf] = useState<PerformanceSnapshot | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [selected, setSelected] = useState<ResourceId>('cpu')
  const [history, setHistory] = useState<Record<string, HistoryPoint[]>>({
    cpu: [],
    memory: [],
    gpu: [],
  })
  const [diskHistories, setDiskHistories] = useState<Record<number, HistoryPoint[]>>({})
  const [networkHistories, setNetworkHistories] = useState<Record<string, HistoryPoint[]>>({})

  const poll = useCallback(async () => {
    try {
      const data = await fetchPerformance()
      setPerf(data)
      setError(null)
      const t = formatTime()
      setHistory((prev) => {
        const next = { ...prev }
        const push = (key: string, value: number, extra?: Partial<HistoryPoint>) => {
          const arr = [...(next[key] || []).slice(-(HISTORY_LEN - 1)), { time: t, value, ...extra }]
          next[key] = arr
        }
        push('cpu', data.cpu.percent)
        push('memory', data.memory.percent)
        if (data.gpu) push('gpu', data.gpu.utilization_percent)
        return next
      })
      setDiskHistories((prev) => {
        const next = { ...prev }
        data.disks.forEach((d, i) => {
          const arr = [...(next[i] || []).slice(-(HISTORY_LEN - 1)), { time: t, value: d.percent }]
          next[i] = arr
        })
        return next
      })
      setNetworkHistories((prev) => {
        const next = { ...prev }
        data.network.forEach((n) => {
          const arr = [
            ...(next[n.name] || []).slice(-(HISTORY_LEN - 1)),
            { time: t, value: n.send_kbps + n.recv_kbps, send_kbps: n.send_kbps, recv_kbps: n.recv_kbps },
          ]
          next[n.name] = arr
        })
        return next
      })
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to fetch performance')
    }
  }, [isActive])

  useEffect(() => {
    poll()
    const intervalMs = isActive ? REFRESH_MS : REFRESH_MS_PRELOAD
    const id = setInterval(poll, intervalMs)
    return () => clearInterval(id)
  }, [isActive, poll])

  const resourceList = buildResourceList(perf)
  const getSparklineData = (id: ResourceId): number[] => {
    if (id === 'cpu') return history.cpu.map((p) => p.value)
    if (id === 'memory') return history.memory.map((p) => p.value)
    if (id === 'gpu') return history.gpu.map((p) => p.value)
    if (id.startsWith('disk-')) {
      const i = parseInt(id.replace('disk-', ''), 10)
      return (diskHistories[i] || []).map((p) => p.value)
    }
    if (id.startsWith('network-')) {
      const name = id.replace('network-', '')
      return (networkHistories[name] || []).map((p) => p.value)
    }
    return []
  }

  if (error && !perf) {
    const isServerDown =
      String(error).includes('ECONNREFUSED') ||
      String(error).includes('Failed to fetch') ||
      String(error).includes('NetworkError')
    return (
      <div className="performance-error">
        <p><strong>API error</strong> — {error}</p>
        {isServerDown && (
          <p className="performance-error-hint">
            Server not running. In the project folder run: <code>python -m uvicorn api:app --host 127.0.0.1 --port 8000</code>
            <br />Or double‑click <code>start_api.bat</code>, then refresh.
          </p>
        )}
      </div>
    )
  }

  if (!perf && !error) {
    return (
      <div className="performance-loading">
        <div className="performance-loading-spinner" aria-hidden />
        <p>Loading performance data…</p>
      </div>
    )
  }

  return (
    <div className="performance-layout">
      <nav className="performance-nav">
        <h2 className="performance-nav-title">Performance</h2>
        {resourceList.map((r) => (
          <button
            key={r.id}
            type="button"
            className={`resource-item ${selected === r.id ? 'active' : ''}`}
            onClick={() => setSelected(r.id)}
          >
            <div className="resource-item-graph">
              <Sparkline data={getSparklineData(r.id)} color={r.color} />
            </div>
            <span className="resource-item-label">{r.label}</span>
            <span className="resource-item-value">{r.value}</span>
          </button>
        ))}
      </nav>
      <div className="performance-detail">
        {perf && isActive && (
          <ResourceDetail
            resourceId={selected}
            perf={perf}
            history={history}
            diskHistories={diskHistories}
            networkHistories={networkHistories}
          />
        )}
      </div>
    </div>
  )
}

interface ResourceDetailProps {
  resourceId: ResourceId
  perf: PerformanceSnapshot
  history: Record<string, HistoryPoint[]>
  diskHistories: Record<number, HistoryPoint[]>
  networkHistories: Record<string, HistoryPoint[]>
}

function ResourceDetail({ resourceId, perf, history, diskHistories, networkHistories }: ResourceDetailProps) {
  if (resourceId === 'cpu') {
    const data = history.cpu.map((p) => ({ time: p.time, value: p.value }))
    return (
      <>
        <div className="detail-header">
          <h1 className="detail-title">CPU</h1>
          <p className="detail-subtitle">% Utilization</p>
        </div>
        <div className="detail-graph-wrap">
          <ResponsiveContainer width="100%" height={220} minHeight={220}>
            <AreaChart data={data} margin={{ top: 8, right: 8, left: 8, bottom: 8 }}>
              <defs>
                <linearGradient id="cpuGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="var(--accent-cyan)" stopOpacity={0.4} />
                  <stop offset="100%" stopColor="var(--accent-cyan)" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
              <XAxis dataKey="time" stroke="var(--text-muted)" fontSize={10} tickLine={false} />
              <YAxis domain={[0, 100]} stroke="var(--text-muted)" fontSize={10} tickFormatter={(v) => `${v}%`} />
              <Tooltip
                contentStyle={{ background: 'var(--bg-elevated)', border: '1px solid var(--border)', borderRadius: 8 }}
                formatter={(v: number) => [`${v}%`, 'Utilization']}
              />
              <Area type="monotone" dataKey="value" fill="url(#cpuGrad)" stroke="var(--accent-cyan)" strokeWidth={2} animationDuration={1000} animationEasing="linear" />
            </AreaChart>
          </ResponsiveContainer>
        </div>
        <div className="detail-stats">
          <Stat label="Utilization" value={`${perf.cpu.percent}%`} />
          <Stat label="Speed" value={`${perf.cpu.frequency_ghz} GHz`} />
          <Stat label="Processes" value={String(perf.cpu.processes)} dim />
          <Stat label="Threads" value={String(perf.cpu.threads)} dim />
          <Stat label="Base speed" value={`${perf.cpu.base_speed_ghz} GHz`} dim />
          <Stat label="Cores" value={String(perf.cpu.cores)} dim />
          <Stat label="Logical processors" value={String(perf.cpu.logical_processors)} dim />
          <Stat label="Up time" value={perf.uptime_formatted} dim />
        </div>
      </>
    )
  }

  if (resourceId === 'memory') {
    const data = history.memory.map((p) => ({ time: p.time, value: p.value }))
    return (
      <>
        <div className="detail-header">
          <h1 className="detail-title">Memory</h1>
          <p className="detail-subtitle">RAM usage</p>
        </div>
        <div className="detail-graph-wrap">
          <ResponsiveContainer width="100%" height={220} minHeight={220}>
            <AreaChart data={data} margin={{ top: 8, right: 8, left: 8, bottom: 8 }}>
              <defs>
                <linearGradient id="memGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="var(--accent-cyan)" stopOpacity={0.4} />
                  <stop offset="100%" stopColor="var(--accent-cyan)" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
              <XAxis dataKey="time" stroke="var(--text-muted)" fontSize={10} tickLine={false} />
              <YAxis domain={[0, 100]} stroke="var(--text-muted)" fontSize={10} tickFormatter={(v) => `${v}%`} />
              <Tooltip
                contentStyle={{ background: 'var(--bg-elevated)', border: '1px solid var(--border)', borderRadius: 8 }}
                formatter={(v: number) => [`${v}%`, 'Usage']}
              />
              <Area type="monotone" dataKey="value" fill="url(#memGrad)" stroke="var(--accent-cyan)" strokeWidth={2} animationDuration={1000} animationEasing="linear" />
            </AreaChart>
          </ResponsiveContainer>
        </div>
        <div className="detail-stats">
          <Stat label="Usage" value={`${perf.memory.used_gb} / ${perf.memory.total_gb} GB (${perf.memory.percent}%)`} />
          <Stat label="Available" value={`${perf.memory.available_gb} GB`} dim />
        </div>
      </>
    )
  }

  if (resourceId.startsWith('disk-')) {
    const i = parseInt(resourceId.replace('disk-', ''), 10)
    const disk = perf.disks[i]
    const data = (diskHistories[i] || []).map((p) => ({ time: p.time, value: p.value }))
    if (!disk) return null
    return (
      <>
        <div className="detail-header">
          <h1 className="detail-title">Disk {i} ({disk.name})</h1>
          <p className="detail-subtitle">{disk.type_label}</p>
        </div>
        <div className="detail-graph-wrap">
          <ResponsiveContainer width="100%" height={220} minHeight={220}>
            <AreaChart data={data} margin={{ top: 8, right: 8, left: 8, bottom: 8 }}>
              <defs>
                <linearGradient id="diskGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#22c55e" stopOpacity={0.4} />
                  <stop offset="100%" stopColor="#22c55e" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
              <XAxis dataKey="time" stroke="var(--text-muted)" fontSize={10} tickLine={false} />
              <YAxis domain={[0, 100]} stroke="var(--text-muted)" fontSize={10} tickFormatter={(v) => `${v}%`} />
              <Area type="monotone" dataKey="value" fill="url(#diskGrad)" stroke="#22c55e" strokeWidth={2} animationDuration={1000} animationEasing="linear" />
            </AreaChart>
          </ResponsiveContainer>
        </div>
        <div className="detail-stats">
          <Stat label="Utilization" value={`${disk.percent}%`} />
          <Stat label="Used" value={`${disk.used_gb} GB`} dim />
          <Stat label="Free" value={`${disk.free_gb} GB`} dim />
          <Stat label="Total" value={`${disk.total_gb} GB`} dim />
          <Stat label="Read" value={`${perf.disk_io.read_mb_s} MB/s`} dim />
          <Stat label="Write" value={`${perf.disk_io.write_mb_s} MB/s`} dim />
        </div>
      </>
    )
  }

  if (resourceId.startsWith('network-')) {
    const name = resourceId.replace('network-', '')
    const iface = perf.network.find((n) => n.name === name)
    const data = (networkHistories[name] || []).map((p) => ({
      time: p.time,
      send: p.send_kbps ?? 0,
      recv: p.recv_kbps ?? 0,
    }))
    if (!iface) return null
    return (
      <>
        <div className="detail-header">
          <h1 className="detail-title">{name}</h1>
          <p className="detail-subtitle">Network activity</p>
        </div>
        <div className="detail-graph-wrap">
          <ResponsiveContainer width="100%" height={220} minHeight={220}>
            <LineChart data={data} margin={{ top: 8, right: 8, left: 8, bottom: 8 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
              <XAxis dataKey="time" stroke="var(--text-muted)" fontSize={10} tickLine={false} />
              <YAxis stroke="var(--text-muted)" fontSize={10} tickFormatter={(v) => `${v}`} />
              <Tooltip
                contentStyle={{ background: 'var(--bg-elevated)', border: '1px solid var(--border)', borderRadius: 8 }}
              />
              <Line type="monotone" dataKey="send" stroke="#d946ef" strokeWidth={2} name="Send Kbps" dot={false} animationDuration={1000} animationEasing="linear" />
              <Line type="monotone" dataKey="recv" stroke="var(--accent-cyan)" strokeWidth={2} name="Recv Kbps" dot={false} animationDuration={1000} animationEasing="linear" />
            </LineChart>
          </ResponsiveContainer>
        </div>
        <div className="detail-stats">
          <Stat label="Send" value={`${iface.send_kbps} Kbps`} />
          <Stat label="Receive" value={`${iface.recv_kbps} Kbps`} />
        </div>
      </>
    )
  }

  if (resourceId === 'gpu' && perf.gpu) {
    const data = history.gpu.map((p) => ({ time: p.time, value: p.value }))
    return (
      <>
        <div className="detail-header">
          <h1 className="detail-title">GPU 0</h1>
          <p className="detail-subtitle">{perf.gpu.name}</p>
        </div>
        <div className="detail-graph-wrap">
          <ResponsiveContainer width="100%" height={220} minHeight={220}>
            <AreaChart data={data} margin={{ top: 8, right: 8, left: 8, bottom: 8 }}>
              <defs>
                <linearGradient id="gpuGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#a855f7" stopOpacity={0.4} />
                  <stop offset="100%" stopColor="#a855f7" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
              <XAxis dataKey="time" stroke="var(--text-muted)" fontSize={10} tickLine={false} />
              <YAxis domain={[0, 100]} stroke="var(--text-muted)" fontSize={10} tickFormatter={(v) => `${v}%`} />
              <Area type="monotone" dataKey="value" fill="url(#gpuGrad)" stroke="#a855f7" strokeWidth={2} animationDuration={1000} animationEasing="linear" />
            </AreaChart>
          </ResponsiveContainer>
        </div>
        <div className="detail-stats">
          <Stat label="Utilization" value={`${perf.gpu.utilization_percent}%`} />
          {perf.gpu.memory_used_mb != null && (
            <Stat label="Memory" value={`${perf.gpu.memory_used_mb} / ${perf.gpu.memory_total_mb ?? 0} MB`} dim />
          )}
        </div>
      </>
    )
  }

  return null
}

function Stat({ label, value, dim }: { label: string; value: string; dim?: boolean }) {
  return (
    <div className="detail-stat">
      <div className="detail-stat-label">{label}</div>
      <div className={`detail-stat-value ${dim ? 'dim' : ''}`}>{value}</div>
    </div>
  )
}
