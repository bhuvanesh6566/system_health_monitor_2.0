import { useEffect, useRef, useState } from 'react'
import { fetchRemoteAgents } from '../api'
import type { AgentMetrics } from '../types'
import './RemoteAgents.css'

const REFRESH_MS = 5000

interface Props { isActive: boolean }

function AgentCard({ a }: { a: AgentMetrics }) {
  const age = Math.round((Date.now() - new Date(a.last_seen).getTime()) / 1000)
  const stale = age > 15

  return (
    <div className={`agent-card ${stale ? 'agent-stale' : 'agent-live'}`}>
      <div className="agent-header">
        <span className="agent-dot" />
        <span className="agent-name">{a.agent_name}</span>
        <span className="agent-age">{stale ? `⚠ ${age}s ago` : `${age}s ago`}</span>
      </div>
      <div className="agent-metrics">
        <div className="agent-metric">
          <span className="am-label">CPU</span>
          <div className="am-bar-wrap"><div className="am-bar" style={{ width: `${a.cpu}%`, background: a.cpu > 80 ? '#ef4444' : '#6366f1' }} /></div>
          <span className="am-val">{a.cpu}%</span>
        </div>
        <div className="agent-metric">
          <span className="am-label">RAM</span>
          <div className="am-bar-wrap"><div className="am-bar" style={{ width: `${a.ram}%`, background: a.ram > 85 ? '#ef4444' : '#22d3ee' }} /></div>
          <span className="am-val">{a.ram}%</span>
        </div>
        <div className="agent-metric">
          <span className="am-label">Disk</span>
          <div className="am-bar-wrap"><div className="am-bar" style={{ width: `${a.disk_percent}%`, background: a.disk_percent > 90 ? '#ef4444' : '#f59e0b' }} /></div>
          <span className="am-val">{a.disk_percent}%</span>
        </div>
      </div>
      <div className="agent-net">
        ↑ {a.net_sent_mb} MB &nbsp;|&nbsp; ↓ {a.net_recv_mb} MB
      </div>
    </div>
  )
}

export function RemoteAgents({ isActive }: Props) {
  const [agents, setAgents] = useState<AgentMetrics[]>([])
  const [error, setError] = useState<string | null>(null)
  const timerRef = useRef<number | null>(null)

  useEffect(() => {
    if (!isActive) {
      if (timerRef.current) clearInterval(timerRef.current)
      return
    }

    const poll = async () => {
      try {
        const data = await fetchRemoteAgents()
        setAgents(data.agents)
        setError(null)
      } catch {
        setError('Cannot reach API')
      }
    }

    poll()
    timerRef.current = window.setInterval(poll, REFRESH_MS)
    return () => { if (timerRef.current) clearInterval(timerRef.current) }
  }, [isActive])

  return (
    <div className="remote-agents-container">
      <h2 className="section-title">Remote Agents</h2>
      {error && <div className="error-banner">{error}</div>}
      {agents.length === 0 && !error && (
        <div className="agent-empty">
          No agents connected yet.<br />
          Run <code>python agent.py --server http://&lt;YOUR_IP&gt;:8000 --name "Friend Laptop"</code> on a remote machine.
        </div>
      )}
      <div className="agent-grid">
        {agents.map(a => <AgentCard key={a.agent_name} a={a} />)}
      </div>
    </div>
  )
}
