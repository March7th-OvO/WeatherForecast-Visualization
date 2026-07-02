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
      tooltip: { trigger: "item", formatter: "{b}: {c}°C" },
      visualMap: {
        min: -20,
        max: 40,
        left: 18,
        bottom: 18,
        calculable: true,
        inRange: { color: ["#4dabf7", "#ffd43b", "#e03131"] },
      },
      series: [
        {
          type: "map",
          map: "china",
          roam: true,
          emphasis: { label: { show: true } },
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
