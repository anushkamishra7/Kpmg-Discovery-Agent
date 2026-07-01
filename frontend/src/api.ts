const API_BASE = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000';

export interface ImageSearchResult {
  asset_path: string;
  asset_url: string;
  score: number;
  metadata?: Record<string, unknown> | null;
}

export interface ImageSearchResponse {
  query: string;
  count: number;
  latency_ms: number;
  results: ImageSearchResult[];
}

export async function searchAssets(
  query: string,
  topK = 10,
  scoreThreshold = 0.2,
): Promise<ImageSearchResponse> {
  const res = await fetch(`${API_BASE}/search/images`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query, top_k: topK, score_threshold: scoreThreshold }),
  });

  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail ?? res.statusText);
  }

  return res.json();
}
