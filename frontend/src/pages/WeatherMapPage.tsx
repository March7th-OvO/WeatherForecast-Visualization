import { useMemo } from "react";

import { getMapData } from "../api/weatherApi";
import { ChartPanel } from "../components/ChartPanel";
import { EChartView } from "../components/EChartView";
import { ErrorState, LoadingState } from "../components/PageState";
import { useAsyncData } from "../hooks/useAsyncData";

export function WeatherMapPage() {
  const { data, error, loading } = useAsyncData(getMapData, []);

  const mapOption = useMemo(
    () => ({
      tooltip: {
        trigger: "item",
        formatter: "{b}: {c}°C",
        backgroundColor: "rgba(16, 32, 51, 0.92)",
        borderColor: "rgba(255, 255, 255, 0.12)",
        textStyle: { color: "#ffffff" },
      },
      visualMap: {
        min: -20,
        max: 40,
        left: 18,
        bottom: 18,
        calculable: true,
        textStyle: { color: "#5f6e82" },
        inRange: { color: ["#2f80ed", "#03a9d8", "#f2b705", "#e8590c", "#d92d20"] },
      },
      series: [
        {
          type: "map",
          map: "china",
          roam: true,
          label: { color: "#5f6e82" },
          itemStyle: {
            borderColor: "#ffffff",
            borderWidth: 0.8,
            areaColor: "#e8f1ff",
          },
          emphasis: {
            label: { show: true, color: "#172033", fontWeight: 700 },
            itemStyle: { areaColor: "#9fd2ff" },
          },
          data:
            data?.provinces.map((item) => ({
              name: item.province_name,
              value: item.avg_high_temp,
            })) ?? [],
        },
      ],
    }),
    [data],
  );

  if (loading) {
    return <LoadingState message="正在加载地图数据" />;
  }

  if (error || !data) {
    return <ErrorState message={error ?? "地图数据不可用"} />;
  }

  return (
    <section className="page-section">
      <header className="page-header">
        <div>
          <p>Map</p>
          <h2>天气地图</h2>
        </div>
      </header>
      <ChartPanel title="全国各省平均最高温分布" className="map-panel">
        <EChartView option={mapOption} className="map-canvas" requiresChinaMap />
      </ChartPanel>
    </section>
  );
}
