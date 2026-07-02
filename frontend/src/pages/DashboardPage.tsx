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
      tooltip: { trigger: "axis" },
      grid: { left: 42, right: 24, top: 34, bottom: 34 },
      xAxis: { type: "category", data: data?.trend.map((item) => item.weather_date) ?? [] },
      yAxis: { type: "value" },
      series: [
        {
          type: "line",
          data: data?.trend.map((item) => item.avg_high_temp) ?? [],
          smooth: true,
          symbolSize: 7,
          lineStyle: { width: 3, color: "#1c7ed6" },
          itemStyle: { color: "#1c7ed6" },
          areaStyle: { color: "rgba(28, 126, 214, 0.12)" },
        },
      ],
    }),
    [data],
  );

  const typeOption = useMemo(
    () => ({
      tooltip: { trigger: "axis" },
      grid: { left: 42, right: 24, top: 34, bottom: 42 },
      xAxis: { type: "category", data: data?.weather_types.map((item) => item.weather_type) ?? [] },
      yAxis: { type: "value" },
      series: [
        {
          type: "bar",
          data: data?.weather_types.map((item) => item.count) ?? [],
          itemStyle: { color: "#2f9e44", borderRadius: [4, 4, 0, 0] },
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
          tone="green"
          icon={ThermometerSun}
        />
        <StatCard
          label="最低温"
          value={`${data.overview.lowest_temp}°C`}
          tone="red"
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
