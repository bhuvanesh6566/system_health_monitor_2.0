import './StatusBanner.css'

interface StatusBannerProps {
  isHealthy: boolean | null
}

export function StatusBanner({ isHealthy }: StatusBannerProps) {
  if (isHealthy === null) return null

  const healthy = isHealthy === true

  return (
    <div className={`status-banner ${healthy ? 'status-healthy' : 'status-anomaly'}`}>
      {healthy ? (
        <>✅ SYSTEM HEALTHY (Normal behavior)</>
      ) : (
        <>🚨 CRITICAL ALERT: ANOMALY DETECTED!</>
      )}
    </div>
  )
}
