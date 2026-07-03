import { render, screen } from "@testing-library/react";
import { expect, test } from "vitest";

import { HistoryTable } from "./HistoryTable";

test("applies staggered reveal delays to history rows", () => {
  render(
    <HistoryTable
      rows={[
        {
          city_name: "北京",
          weather_date: "2026-07-01",
          weather_type: "晴",
          high_temp: 34,
          low_temp: 24,
          wind_level: "3级",
        },
        {
          city_name: "北京",
          weather_date: "2026-07-02",
          weather_type: "多云",
          high_temp: 32,
          low_temp: 23,
          wind_level: "2级",
        },
      ]}
    />,
  );

  const firstRow = screen.getByText("2026-07-01").closest("tr");
  const secondRow = screen.getByText("2026-07-02").closest("tr");

  expect(firstRow).toHaveClass("history-row");
  expect(firstRow).toHaveStyle({ animationDelay: "0ms" });
  expect(secondRow).toHaveStyle({ animationDelay: "55ms" });
});
