import { useEffect, useState, useMemo } from 'react'
import { fetchProcesses } from '../api'
import type { ProcessesSnapshot } from '../types'
import './ProcessesView.css'

const REFRESH_MS = 2000
const REFRESH_MS_PRELOAD = 4000

type SortKey = 'name' | 'cpu_percent' | 'memory_mb' | 'disk_mb_s' | 'network_mbps'
type SortDir = 'asc' | 'desc'

interface ProcessesViewProps {
  isActive: boolean
}

export function ProcessesView({ isActive }: ProcessesViewProps) {
  const [data, setData] = useState<ProcessesSnapshot | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [sortKey, setSortKey] = useState<SortKey>('memory_mb')
  const [sortDir, setSortDir] = useState<SortDir>('desc')

  useEffect(() => {
    let cancelled = false
    const poll = async () => {
      try {
        const res = await fetchProcesses()
        if (!cancelled) {
          setData(res)
          setError(null)
        }
      } catch (e) {
        if (!cancelled) {
          setError(e instanceof Error ? e.message : 'Failed to fetch processes')
          setData(null)
        }
      }
    }
    poll()
    const intervalMs = isActive ? REFRESH_MS : REFRESH_MS_PRELOAD
    const id = setInterval(poll, intervalMs)
    return () => {
      cancelled = true
      clearInterval(id)
    }
  }, [isActive])

  const sortedProcesses = useMemo(() => {
    if (!data?.processes) return []
    const arr = [...data.processes]
    const k = sortKey
    const d = sortDir === 'asc' ? 1 : -1
    arr.sort((a, b) => {
      const aVal = a[k as keyof typeof a]
      const bVal = b[k as keyof typeof b]
      if (typeof aVal === 'string' && typeof bVal === 'string') {
        return d * aVal.localeCompare(bVal, undefined, { sensitivity: 'base' })
      }
      return d * (Number(aVal) - Number(bVal))
    })
    return arr
  }, [data?.processes, sortKey, sortDir])

  const handleSort = (key: SortKey) => {
    if (sortKey === key) {
      setSortDir((d) => (d === 'asc' ? 'desc' : 'asc'))
    } else {
      setSortKey(key)
      setSortDir(key === 'name' ? 'asc' : 'desc')
    }
  }

  const isServerDown =
    error &&
    (String(error).includes('ECONNREFUSED') ||
      String(error).includes('Failed to fetch') ||
      String(error).includes('NetworkError'))

  if (error && !data) {
    return (
      <div className="processes-view">
        <div className="processes-error">
          <p><strong>API error</strong> — {error}</p>
          {isServerDown && (
            <div className="processes-server-hint">
              <p><strong>Server is not running.</strong> Do this first:</p>
              <ol>
                <li>Open a terminal in the project folder: <code>system_health_moniter</code></li>
                <li>Run: <code>python -m uvicorn api:app --host 127.0.0.1 --port 8000</code></li>
                <li>Or double‑click <code>start_api.bat</code> in the project folder</li>
              </ol>
              <p>Keep that window open, then refresh this page.</p>
            </div>
          )}
        </div>
      </div>
    )
  }

  if (!data && !error) {
    return (
      <div className="processes-view">
        <div className="processes-loading">
          <div className="processes-loading-spinner" aria-hidden />
          <p>Loading processes…</p>
        </div>
      </div>
    )
  }

  const s = data?.summary

  return (
    <div className="processes-view">
      <div className="processes-header">
        <h2 className="processes-title">Processes</h2>
        <div className="processes-summary">
          <div className="processes-summary-item">
            <span className="processes-summary-label">CPU</span>
            <span className="processes-summary-value">{(s?.cpu_percent ?? 0).toFixed(1)}%</span>
          </div>
          <div className="processes-summary-item">
            <span className="processes-summary-label">Memory</span>
            <span className={`processes-summary-value ${sortKey === 'memory_mb' ? 'sorted' : ''}`}>
              {(s?.memory_percent ?? 0).toFixed(1)}%
            </span>
            {sortKey === 'memory_mb' && (
              <span className="sort-icon" aria-hidden>
                {sortDir === 'desc' ? '▼' : '▲'}
              </span>
            )}
          </div>
          <div className="processes-summary-item">
            <span className="processes-summary-label">Disk</span>
            <span className="processes-summary-value">{(s?.disk_percent ?? 0).toFixed(1)}%</span>
          </div>
          <div className="processes-summary-item">
            <span className="processes-summary-label">Network</span>
            <span className="processes-summary-value">{(s?.network_percent ?? 0).toFixed(1)}%</span>
          </div>
        </div>
      </div>

      <div className="processes-table-wrap">
        <table className="processes-table">
          <thead>
            <tr>
              <th onClick={() => handleSort('name')} className={sortKey === 'name' ? 'sorted' : ''}>
                Name
                {sortKey === 'name' && <span className="sort-icon">{sortDir === 'desc' ? '▼' : '▲'}</span>}
              </th>
              <th className="col-status">Status</th>
              <th onClick={() => handleSort('cpu_percent')} className={`col-num ${sortKey === 'cpu_percent' ? 'sorted' : ''}`}>
                CPU
                {sortKey === 'cpu_percent' && <span className="sort-icon">{sortDir === 'desc' ? '▼' : '▲'}</span>}
              </th>
              <th onClick={() => handleSort('memory_mb')} className={`col-num ${sortKey === 'memory_mb' ? 'sorted' : ''}`}>
                Memory
                {sortKey === 'memory_mb' && <span className="sort-icon">{sortDir === 'desc' ? '▼' : '▲'}</span>}
              </th>
              <th onClick={() => handleSort('disk_mb_s')} className={`col-num ${sortKey === 'disk_mb_s' ? 'sorted' : ''}`}>
                Disk
                {sortKey === 'disk_mb_s' && <span className="sort-icon">{sortDir === 'desc' ? '▼' : '▲'}</span>}
              </th>
              <th onClick={() => handleSort('network_mbps')} className={`col-num ${sortKey === 'network_mbps' ? 'sorted' : ''}`}>
                Network
                {sortKey === 'network_mbps' && <span className="sort-icon">{sortDir === 'desc' ? '▼' : '▲'}</span>}
              </th>
            </tr>
          </thead>
            <tbody>
            {sortedProcesses.map((proc, idx) => (
              <tr key={`${proc.name}-${idx}`}>
                <td className="col-name">
                  <span className="processes-expand" aria-hidden>›</span>
                  <span className="process-icon-wrap">
                    {proc.exe_path ? (
                      <img
                        src={`/api/process-icon?path=${encodeURIComponent(proc.exe_path)}`}
                        alt=""
                        className="process-icon"
                        width={20}
                        height={20}
                        onError={(e) => {
                          const el = e.currentTarget
                          el.style.display = 'none'
                          const fallback = el.nextElementSibling as HTMLElement
                          if (fallback) fallback.style.display = 'inline-block'
                        }}
                      />
                    ) : null}
                    <span
                      className="process-icon process-icon-default"
                      aria-hidden
                      style={proc.exe_path ? { display: 'none' } : undefined}
                    />
                  </span>
                  {proc.display_name}
                </td>
                <td className="col-status">
                  {proc.count > 1 && proc.memory_mb < 200 ? (
                    <span className="processes-status-leaf" title="Efficiency mode">🌱</span>
                  ) : null}
                </td>
                <td className="col-num">{proc.cpu_percent.toFixed(1)}%</td>
                <td className="col-num">{proc.memory_mb.toFixed(1)} MB</td>
                <td className="col-num">{proc.disk_mb_s.toFixed(1)} MB/s</td>
                <td className="col-num">{proc.network_mbps?.toFixed(1) ?? '0'} Mbps</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
