import { Building2, Database, ThermometerSnowflake, ThermometerSun } from "lucide-react";
import { useMemo } from "react";

import { getDashboard } from "../api/weatherApi";
import { ChartPanel } from "../components/ChartPanel";
import { EChartView } from "../components/EChartView";
import { ErrorState, LoadingState } from "../components/PageState";
import { StatCard } from "../components/StatCard";
import { useAsyncData } from "../hooks/useAsyncData";

const numberFormatter = new Intl.NumberFormat("zh-CN");

export function DashboardPage() {
  const { data, error, loading } = useAsyncData(getDashboard, []);

  const trendOption = useMemo(
    () => ({
      color: ["#0f62fe"],
      tooltip: { trigger: "axis", valueFormatter: (value: number) => `${value}°C` },
      grid: { left: 42, right: 24, top: 34, bottom: 34 },
      xAxis: {
        type: "category",
        data: data?.trend.map((item) => item.weather_date) ?? [],
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
          type: "line",
          name: "平均最高温",
          data: data?.trend.map((item) => item.avg_high_temp) ?? [],
          smooth: true,
          symbolSize: 7,
          lineStyle: { width: 3, color: "#0f62fe" },
          itemStyle: { color: "#0f62fe" },
          areaStyle: { color: "rgba(15, 98, 254, 0.12)" },
        },
      ],
    }),
    [data],
  );

  const typeOption = useMemo(
    () => ({
      color: ["#03a9d8"],
      tooltip: { trigger: "axis" },
      grid: { left: 42, right: 24, top: 34, bottom: 42 },
      xAxis: {
        type: "category",
        data: data?.weather_types.map((item) => item.weather_type) ?? [],
        axisLine: { lineStyle: { color: "#b8c7d9" } },
        axisLabel: { color: "#5f6e82" },
      },
      yAxis: {
        type: "value",
        axisLabel: { color: "#5f6e82" },
        splitLine: { lineStyle: { color: "#edf2f7" } },
      },
      series: [
        {
          type: "bar",
          name: "记录数",
          data: data?.weather_types.map((item) => item.count) ?? [],
          itemStyle: { color: "#03a9d8", borderRadius: [4, 4, 0, 0] },
        },
      ],
    }),
    [data],
  );

  if (loading) {
    return <LoadingState message="正在加载首页数据" />;
  }

  if (error || !data) {
    return <ErrorState message={error ?? "首页数据不可用"} />;
  }

  return (
    <section className="page-section">
      <header className="page-header">
        <div>
          <p>Dashboard</p>
          <h2>首页总览</h2>
        </div>
      </header>

      <div className="stats-grid">
        <StatCard
          label="总记录数"
          value={numberFormatter.format(data.overview.total_records)}
          tone="blue"
          icon={Database}
        />
        <StatCard
          label="已采集城市"
          value={numberFormatter.format(data.overview.total_cities)}
          tone="amber"
          icon={Building2}
        />
        <StatCard
          label="最高温"
          value={`${data.overview.highest_temp}°C`}
          tone="hot"
          icon={ThermometerSun}
        />
        <StatCard
          label="最低温"
          value={`${data.overview.lowest_temp}°C`}
          tone="cold"
          icon={ThermometerSnowflake}
        />
      </div>

      <div className="chart-grid">
        <ChartPanel title="近 30 天平均最高温趋势">
          <EChartView option={trendOption} />
        </ChartPanel>
        <ChartPanel title="天气类型分布">
          <EChartView option={typeOption} />
        </ChartPanel>
      </div>
    </section>
  );
}
