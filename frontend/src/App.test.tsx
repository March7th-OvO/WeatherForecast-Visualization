import { render, screen } from "@testing-library/react";
import { afterEach, beforeEach, expect, test, vi } from "vitest";

import { App } from "./App";

const originalFetch = globalThis.fetch;

beforeEach(() => {
  globalThis.fetch = vi.fn().mockResolvedValue(
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
});

afterEach(() => {
  globalThis.fetch = originalFetch;
  vi.restoreAllMocks();
});

test("renders navigation for the four weather views", () => {
  render(<App />);

  expect(screen.getByText("气象数据观测台")).toBeInTheDocument();
  expect(screen.getByRole("link", { name: /首页/ })).toHaveAttribute("href", "/");
  expect(screen.getByRole("link", { name: /天气地图/ })).toHaveAttribute("href", "/map");
  expect(screen.getByRole("link", { name: /天气分析/ })).toHaveAttribute("href", "/analysis");
  expect(screen.getByRole("link", { name: /15日天气/ })).toHaveAttribute("href", "/history");
});

test("loads dashboard metrics on the home route", async () => {
  render(<App />);

  expect(await screen.findByText("20,550")).toBeInTheDocument();
  expect(screen.getByText("已采集城市")).toBeInTheDocument();
});
