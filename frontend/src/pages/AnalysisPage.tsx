import { useMemo } from "react";

import { getAnalysis } from "../api/weatherApi";
import { ChartPanel } from "../components/ChartPanel";
import { EChartView } from "../components/EChartView";
import { ErrorState, LoadingState } from "../components/PageState";
import { useAsyncData } from "../hooks/useAsyncData";

export function AnalysisPage() {
  const { data, error, loading } = useAsyncData(getAnalysis, []);

  const highOption = useMemo(
    () => ({
      color: ["#e8590c"],
      tooltip: { trigger: "axis", valueFormatter: (value: number) => `${value}°C` },
      grid: { left: 42, right: 24, top: 28, bottom: 42 },
      xAxis: {
        type: "category",
        data: data?.high_top10.map((item) => item.city_name) ?? [],
        axisLine: { lineStyle: { color: "#b8c7d9" } },
        axisLabel: { color: "#5f6e82" },
      },
      yAxis: {
        type: "value",
        axisLabel: { color: "#5f6e82", formatter: "{value}°C" },
        splitLine: { lineStyle: { color: "#edf2f7" } },
      },
      series: [
        {
          type: "bar",
          name: "平均最高温",
          data: data?.high_top10.map((item) => item.avg_high_temp) ?? [],
          itemStyle: { color: "#e8590c", borderRadius: [4, 4, 0, 0] },
        },
      ],
    }),
    [data],
  );

  const lowOption = useMemo(
    () => ({
      color: ["#2f80ed"],
      tooltip: { trigger: "axis", valueFormatter: (value: number) => `${value}°C` },
      grid: { left: 42, right: 24, top: 28, bottom: 42 },
      xAxis: {
        type: "category",
        data: data?.low_top10.map((item) => item.city_name) ?? [],
        axisLine: { lineStyle: { color: "#b8c7d9" } },
        axisLabel: { color: "#5f6e82" },
      },
      yAxis: {
        type: "value",
        axisLabel: { color: "#5f6e82", formatter: "{value}°C" },
        splitLine: { lineStyle: { color: "#edf2f7" } },
      },
      series: [
        {
          type: "bar",
          name: "平均最低温",
          data: data?.low_top10.map((item) => item.avg_low_temp) ?? [],
          itemStyle: { color: "#2f80ed", borderRadius: [4, 4, 0, 0] },
        },
      ],
    }),
    [data],
  );

  const pieOption = useMemo(
    () => ({
      color: ["#0f62fe", "#03a9d8", "#2f9e44", "#f2b705", "#e8590c", "#d92d20"],
      tooltip: { trigger: "item" },
      legend: { bottom: 0, textStyle: { color: "#5f6e82" } },
      series: [
        {
          type: "pie",
          radius: ["42%", "70%"],
          center: ["50%", "45%"],
          label: { color: "#5f6e82" },
          itemStyle: { borderColor: "#ffffff", borderWidth: 2 },
          data:
            data?.weather_types.map((item) => ({
              name: item.weather_type,
              value: item.count,
            })) ?? [],
        },
      ],
    }),
    [data],
  );

  if (loading) {
    return <LoadingState message="正在加载分析数据" />;
  }

  if (error || !data) {
    return <ErrorState message={error ?? "分析数据不可用"} />;
  }

  return (
    <section className="page-section">
      <header className="page-header">
        <div>
          <p>Analysis</p>
          <h2>天气分析</h2>
        </div>
      </header>
      <div className="chart-grid">
        <ChartPanel title="城市平均最高温 Top10">
          <EChartView option={highOption} />
        </ChartPanel>
        <ChartPanel title="城市平均最低温 Top10">
          <EChartView option={lowOption} />
        </ChartPanel>
        <ChartPanel title="天气类型占比" className="wide-panel">
          <EChartView option={pieOption} />
        </ChartPanel>
      </div>
    </section>
  );
}
