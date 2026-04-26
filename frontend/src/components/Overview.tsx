import { useEffect, useState, useRef, useCallback } from 'react'
import { fetchLive } from '../api'
import type { HealthSnapshot } from '../types'
import { StatusBanner } from './StatusBanner'
import { MetricCard } from './MetricCard'
import { ChartsRow } from './ChartsRow'

const REFRESH_MS = 1000
const HISTORY_LEN = 40

function formatTime() {
    return new Date().toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false })
}

interface OverviewProps {
    isActive: boolean
}

export function Overview({ isActive }: OverviewProps) {
    const [health, setHealth] = useState<HealthSnapshot>({ cpu: 0, ram: 0, disk_mb_s: 0, db_threads: 1, algo_ms: 0, is_healthy: true })
    const [error, setError] = useState<string | null>(null)
    const [cpuHistory, setCpuHistory] = useState<{ time: string; cpu: number }[]>([])
    const [algoHistory, setAlgoHistory] = useState<{ time: string; algo_ms: number }[]>([])
    const intervalRef = useRef<number | null>(null)

    const poll = useCallback(async () => {
        try {
            const controller = new AbortController()
            const timeoutId = setTimeout(() => controller.abort(), 500)
            
            const data = await fetchLive()
            clearTimeout(timeoutId)
            
            setHealth(data)
            setError(null)

            const t = formatTime()
            setCpuHistory((prev) => [...prev.slice(-(HISTORY_LEN - 1)), { time: t, cpu: data.cpu }])
            setAlgoHistory((prev) => [...prev.slice(-(HISTORY_LEN - 1)), { time: t, algo_ms: data.algo_ms }])
        } catch (e) {
            if (e.name !== 'AbortError') {
                setError('Connection issue')
            }
        }
    }, [])

    useEffect(() => {
        if (!isActive) {
            if (intervalRef.current) {
                clearInterval(intervalRef.current)
                intervalRef.current = null
            }
            return
        }

        poll()
        intervalRef.current = window.setInterval(() => {
            poll().catch(() => {})
        }, REFRESH_MS)

        return () => {
            if (intervalRef.current) {
                clearInterval(intervalRef.current)
                intervalRef.current = null
            }
        }
    }, [isActive, poll])

    return (
        <div className="overview-container">
            {error && (
                <div className="error-banner">
                    {error}
                </div>
            )}

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
        </div>
    )
}
