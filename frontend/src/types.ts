export interface HealthSnapshot {
  cpu: number;
  ram: number;
  disk_mb_s: number;
  db_threads: number;
  algo_ms: number;
  is_healthy: boolean | null;
  error?: string;
}

export interface ChartPoint {
  time: string;
  cpu?: number;
  algo_ms?: number;
}
