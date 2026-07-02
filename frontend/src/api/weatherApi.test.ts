import { afterEach, beforeEach, expect, test, vi } from "vitest";

import { getDashboard, getHistory } from "./weatherApi";

const originalFetch = globalThis.fetch;

beforeEach(() => {
  globalThis.fetch = vi.fn();
});

afterEach(() => {
  globalThis.fetch = originalFetch;
  vi.restoreAllMocks();
});

test("getDashboard fetches and returns dashboard payload", async () => {
  vi.mocked(globalThis.fetch).mockResolvedValueOnce(
    new Response(
      JSON.stringify({
        overview: {
          total_records: 20550,
          total_cities: 1370,
          highest_temp: 40,
          lowest_temp: -18,
        },
        trend: [{ weather_date: "2026-07-01", avg_high_temp: 32 }],
        weather_types: [{ weather_type: "晴", count: 128 }],
      }),
      { status: 200 },
    ),
  );

  const payload = await getDashboard();

  expect(globalThis.fetch).toHaveBeenCalledWith("/api/dashboard");
  expect(payload.overview.total_records).toBe(20550);
  expect(payload.trend[0].avg_high_temp).toBe(32);
});

test("getHistory encodes city names in query string", async () => {
  vi.mocked(globalThis.fetch).mockResolvedValueOnce(
    new Response(JSON.stringify([]), { status: 200 }),
  );

  await getHistory("上海");

  expect(globalThis.fetch).toHaveBeenCalledWith(
    "/api/history?city_name=%E4%B8%8A%E6%B5%B7",
  );
});

test("api client throws a useful error for failed responses", async () => {
  vi.mocked(globalThis.fetch).mockResolvedValueOnce(
    new Response("server error", { status: 500, statusText: "Internal Server Error" }),
  );

  await expect(getDashboard()).rejects.toThrow(
    "请求 /api/dashboard 失败：500 Internal Server Error",
  );
});
