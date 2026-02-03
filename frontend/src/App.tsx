import { useEffect, useState } from 'react'
import { fetchHealth } from './api'
import type { HealthSnapshot } from './types'
import './App.css'
import { StatusBanner } from './components/StatusBanner'
import { MetricCard } from './components/MetricCard'
import { ChartsRow } from './components/ChartsRow'
import { Sidebar } from './components/Sidebar'

const REFRESH_MS = 1000
const REFRESH_MS_WHEN_DISCONNECTED = 5000
const HISTORY_LEN = 50

function formatTime() {
  return new Date().toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false })
}

export default function App() {
  const [health, setHealth] = useState<HealthSnapshot | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [cpuHistory, setCpuHistory] = useState<{ time: string; cpu: number }[]>([])
  const [algoHistory, setAlgoHistory] = useState<{ time: string; algo_ms: number }[]>([])

  useEffect(() => {
    let cancelled = false
    let timeoutId: ReturnType<typeof setTimeout>

    const scheduleNext = (delayMs: number) => {
      if (cancelled) return
      timeoutId = setTimeout(poll, delayMs)
    }

    const poll = async () => {
      try {
        const data = await fetchHealth()
        if (cancelled) return
        setHealth(data)
        setError(data.error ?? null)

        const t = formatTime()
        if (data.error == null) {
          setCpuHistory((prev) => [...prev.slice(-(HISTORY_LEN - 1)), { time: t, cpu: data.cpu }])
          setAlgoHistory((prev) => [...prev.slice(-(HISTORY_LEN - 1)), { time: t, algo_ms: data.algo_ms }])
        }
        scheduleNext(REFRESH_MS)
      } catch (e) {
        if (!cancelled) {
          const msg = e instanceof Error ? e.message : 'Failed to fetch'
          setError(
            msg.includes('ECONNREFUSED') || msg.includes('Failed to fetch')
              ? 'Backend not running. Start it from the project root: uvicorn api:app --reload --host 127.0.0.1 --port 8000'
              : msg
          )
          setHealth(null)
        }
        scheduleNext(REFRESH_MS_WHEN_DISCONNECTED)
      }
    }

    poll()
    return () => {
      cancelled = true
      clearTimeout(timeoutId)
    }
  }, [])

  return (
    <div className="app">
      <Sidebar />
      <main className="main">
        <header className="header">
          <h1 className="title">
            <span className="title-icon">🛡️</span>
            AIOps: Intelligent System Monitor
          </h1>
          <p className="subtitle">
            Real-time anomaly detection with <span className="accent">advanced visualization</span>
          </p>
        </header>

        {error && (
          <div className="error-banner">
            {error}
          </div>
        )}

        {health && !health.error && (
          <>
            <StatusBanner isHealthy={health.is_healthy} />
            <section className="metrics-section">
              <h2 className="section-title">Live metrics</h2>
              <div className="metrics-grid">
                <MetricCard label="CPU usage" value={`${health.cpu}%`} sub="Usage" />
                <MetricCard label="Active DB threads" value={String(health.db_threads)} sub="Connections" />
                <MetricCard label="Algorithm speed" value={`${health.algo_ms} ms`} sub="Execution time" />
              </div>
            </section>
            <section className="charts-section">
              <h2 className="section-title">Performance trends</h2>
              <ChartsRow
                cpuData={cpuHistory}
                algoData={algoHistory}
              />
            </section>
          </>
        )}

        {health?.error && !error && (
          <div className="error-banner">
            {health.error}
          </div>
        )}
      </main>
    </div>
  )
}
