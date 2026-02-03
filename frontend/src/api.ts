import type { HealthSnapshot } from './types';

const API_BASE = '/api';

export async function fetchHealth(): Promise<HealthSnapshot> {
  const res = await fetch(`${API_BASE}/health`);
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

export async function ping(): Promise<{ status: string }> {
  const res = await fetch(`${API_BASE}/ping`);
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}
