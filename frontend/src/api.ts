import type { HealthSnapshot, PerformanceSnapshot, ProcessesSnapshot, RemoteAgentsSnapshot } from './types';

const API_BASE = '/api';

export async function fetchLive(): Promise<HealthSnapshot> {
  const res = await fetch(`${API_BASE}/live`);
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

export async function fetchHealth(): Promise<HealthSnapshot> {
  const res = await fetch(`${API_BASE}/health`);
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

export async function fetchPerformance(): Promise<PerformanceSnapshot> {
  const res = await fetch(`${API_BASE}/performance`);
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

export async function fetchProcesses(): Promise<ProcessesSnapshot> {
  const res = await fetch(`${API_BASE}/processes`);
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

export async function fetchRemoteAgents(): Promise<RemoteAgentsSnapshot> {
  const res = await fetch(`${API_BASE}/remote-agents`);
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

export async function ping(): Promise<{ status: string }> {
  const res = await fetch(`${API_BASE}/ping`);
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

