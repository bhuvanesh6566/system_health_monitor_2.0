import { useState } from 'react'
import { PerformanceView } from './components/PerformanceView'
import { ProcessesView } from './components/ProcessesView'
import { Overview } from './components/Overview'
import { RemoteAgents } from './components/RemoteAgents'
import { Sidebar } from './components/Sidebar'
import './App.css'

type TabId = 'overview' | 'performance' | 'processes' | 'remote'
export default function App() {
  const [tab, setTab] = useState<TabId>('processes')

  return (
    <div className="app">
      <Sidebar />
      <main className="main">
        <header className="header header-with-tabs">
          <div className="header-top">
            <h1 className="title">
              <span className="title-icon">🛡️</span>
              AIOps: Intelligent System Monitor
            </h1>
            <p className="subtitle">
              Real-time anomaly detection with <span className="accent">advanced visualization</span>
            </p>
          </div>
          <div className="tabs">
            <button
              type="button"
              className={`tab ${tab === 'processes' ? 'tab-active' : ''}`}
              onClick={() => setTab('processes')}
            >
              Processes
            </button>
            <button
              type="button"
              className={`tab ${tab === 'performance' ? 'tab-active' : ''}`}
              onClick={() => setTab('performance')}
            >
              Performance
            </button>
            <button
              type="button"
              className={`tab ${tab === 'overview' ? 'tab-active' : ''}`}
              onClick={() => setTab('overview')}
            >
              Overview
            </button>
            <button
              type="button"
              className={`tab ${tab === 'remote' ? 'tab-active' : ''}`}
              onClick={() => setTab('remote')}
            >
              Remote Agents
            </button>
          </div>
        </header>

        <div className={tab === 'performance' ? 'tab-panel' : 'tab-panel tab-panel-hidden'}>
          <PerformanceView isActive={tab === 'performance'} />
        </div>

        <div className={tab === 'processes' ? 'tab-panel' : 'tab-panel tab-panel-hidden'}>
          <ProcessesView isActive={tab === 'processes'} />
        </div>

        <div className={tab === 'overview' ? 'tab-panel' : 'tab-panel tab-panel-hidden'}>
          <Overview isActive={tab === 'overview'} />
        </div>

        <div className={tab === 'remote' ? 'tab-panel' : 'tab-panel tab-panel-hidden'}>
          <RemoteAgents isActive={tab === 'remote'} />
        </div>
      </main>
    </div>
  )

}
