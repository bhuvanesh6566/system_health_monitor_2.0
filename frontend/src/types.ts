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

// Task Manager–style performance snapshot
export interface PerformanceSnapshot {
  cpu: {
    percent: number;
    frequency_mhz: number;
    frequency_ghz: number;
    base_speed_mhz: number;
    base_speed_ghz: number;
    processes: number;
    threads: number;
    cores: number;
    logical_processors: number;
  };
  memory: {
    percent: number;
    used_gb: number;
    total_gb: number;
    available_gb: number;
  };
  disks: Array<{
    name: string;
    mountpoint: string;
    percent: number;
    total_gb: number;
    used_gb: number;
    free_gb: number;
    type_label: string;
  }>;
  disk_io: { read_mb_s: number; write_mb_s: number };
  network: Array<{ name: string; send_kbps: number; recv_kbps: number }>;
  gpu: {
    name: string;
    utilization_percent: number;
    memory_used_mb?: number;
    memory_total_mb?: number;
  } | null;
  uptime_seconds: number;
  uptime_formatted: string;
}

// Remote agent
export interface AgentMetrics {
  agent_name: string;
  cpu: number;
  ram: number;
  disk_percent: number;
  net_sent_mb: number;
  net_recv_mb: number;
  last_seen: string;
}

export interface RemoteAgentsSnapshot {
  agents: AgentMetrics[];
}

// Processes view (Task Manager–style)
export interface ProcessesSnapshot {
  summary: {
    cpu_percent: number;
    memory_percent: number;
    disk_percent: number;
    network_percent: number;
  };
  processes: Array<{
    name: string;
    display_name: string;
    count: number;
    exe_path: string | null;
    cpu_percent: number;
    memory_mb: number;
    disk_mb_s: number;
    network_mbps: number;
  }>;
}
