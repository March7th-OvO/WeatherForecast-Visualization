import type {
  AnalysisPayload,
  DashboardPayload,
  MapPayload,
  WeatherHistoryRow,
} from "./types";

async function requestJson<TPayload>(url: string): Promise<TPayload> {
  const response = await fetch(url);

  if (!response.ok) {
    throw new Error(`请求 ${url} 失败：${response.status} ${response.statusText}`);
  }

  return response.json() as Promise<TPayload>;
}

export function getDashboard(): Promise<DashboardPayload> {
  return requestJson<DashboardPayload>("/api/dashboard");
}

export function getMapData(): Promise<MapPayload> {
  return requestJson<MapPayload>("/api/map");
}

export function getAnalysis(): Promise<AnalysisPayload> {
  return requestJson<AnalysisPayload>("/api/analysis");
}

export function getHistory(cityName: string): Promise<WeatherHistoryRow[]> {
  return requestJson<WeatherHistoryRow[]>(
    `/api/history?city_name=${encodeURIComponent(cityName)}`,
  );
}
