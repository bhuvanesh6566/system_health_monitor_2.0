import './Sidebar.css'

export function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        <img src="/shield.svg" alt="Shield" className="sidebar-icon" />
      </div>
      <h2 className="sidebar-title">Control panel</h2>
      <hr className="sidebar-divider" />
      <ul className="sidebar-meta">
        <li><span className="meta-label">System status</span> <span className="meta-value online">ONLINE</span></li>
        <li><span className="meta-label">AI model</span> <span className="meta-value">Isolation Forest</span></li>
        <li><span className="meta-label">Version</span> <span className="meta-value">v2.0.1</span></li>
      </ul>
      <hr className="sidebar-divider" />
      <div className="sidebar-threshold">
        <label htmlFor="threshold">Anomaly threshold</label>
        <input id="threshold" type="range" min="0" max="1" step="0.1" defaultValue="0.8" className="threshold-slider" />
        <span className="threshold-value">0.8</span>
      </div>
    </aside>
  )
}
