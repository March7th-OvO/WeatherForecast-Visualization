import { useCallback, useMemo, useState } from "react";

import { getAnalysis } from "../api/weatherApi";
import { ChartPanel } from "../components/ChartPanel";
import { EChartView } from "../components/EChartView";
import { ErrorState, LoadingState } from "../components/PageState";
import { useAsyncData } from "../hooks/useAsyncData";

interface WeatherTypeFocus {
  name: string;
  value: string;
  percent: string;
}

export function AnalysisPage() {
  const { data, error, loading } = useAsyncData(getAnalysis, []);
  const [focusedWeatherType, setFocusedWeatherType] = useState<WeatherTypeFocus | null>(null);

  const handleWeatherTypeFocus = useCallback((params: unknown) => {
    const event = params as {
      componentType?: string;
      seriesType?: string;
      name?: unknown;
      value?: unknown;
      percent?: unknown;
    };

    if (event.componentType !== "series" || event.seriesType !== "pie") {
      return;
    }

    const percent =
      typeof event.percent === "number" ? event.percent.toFixed(1) : String(event.percent ?? "-");

    setFocusedWeatherType({
      name: String(event.name ?? "-"),
      value: String(event.value ?? "-"),
      percent,
    });
  }, []);

  const handleWeatherTypeLeave = useCallback(() => {
    setFocusedWeatherType(null);
  }, []);

  const weatherTypeEvents = useMemo(
    () => ({
      mouseover: handleWeatherTypeFocus,
      globalout: handleWeatherTypeLeave,
    }),
    [handleWeatherTypeFocus, handleWeatherTypeLeave],
  );

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
      baseOption: {
        animation: true,
        animationDuration: 700,
        animationDurationUpdate: 420,
        animationEasing: "cubicOut",
        animationEasingUpdate: "cubicInOut",
        color: ["#0f62fe", "#03a9d8", "#2f9e44", "#f2b705", "#e8590c", "#d92d20"],
        stateAnimation: {
          duration: 320,
          easing: "cubicOut",
        },
        tooltip: { show: false },
        legend: {
          type: "scroll",
          orient: "vertical",
          right: 8,
          top: 22,
          bottom: 16,
          width: 260,
          itemGap: 10,
          pageIconColor: "#0f62fe",
          pageIconInactiveColor: "#b8c7d9",
          pageTextStyle: { color: "#5f6e82" },
          textStyle: { color: "#5f6e82" },
        },
        series: [
          {
            type: "pie",
            radius: [130, 224],
            center: ["34%", "50%"],
            avoidLabelOverlap: true,
            minShowLabelAngle: 8,
            label: { show: false },
            emphasis: {
              scale: true,
              scaleSize: 8,
              focus: "self",
              label: { show: false },
              itemStyle: {
                shadowBlur: 18,
                shadowColor: "rgba(17, 35, 60, 0.18)",
              },
            },
            blur: {
              itemStyle: {
                opacity: 0.72,
              },
            },
            labelLine: { show: false },
            itemStyle: { borderWidth: 0 },
            data:
              data?.weather_types.map((item) => ({
                name: item.weather_type,
                value: item.count,
              })) ?? [],
          },
        ],
      },
      media: [
        {
          query: { maxWidth: 760 },
          option: {
            legend: {
              orient: "horizontal",
              left: 0,
              right: 0,
              top: "auto",
              bottom: 0,
              width: "auto",
              height: 64,
            },
            series: [
              {
                radius: [112, 196],
                center: ["50%", "38%"],
              },
            ],
          },
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
        <ChartPanel title="天气类型占比" className="wide-panel weather-type-panel">
          <div className="weather-type-chart">
            <EChartView option={pieOption} onEvents={weatherTypeEvents} />
            <div
              className={`weather-type-center${focusedWeatherType ? " active" : ""}`}
              aria-live="polite"
            >
              {focusedWeatherType ? (
                <div
                  key={`${focusedWeatherType.name}-${focusedWeatherType.value}-${focusedWeatherType.percent}`}
                  className="weather-type-center-content"
                >
                  <strong>{focusedWeatherType.name}</strong>
                  <span>{focusedWeatherType.value} 条</span>
                  <em>{focusedWeatherType.percent}%</em>
                </div>
              ) : (
                <div className="weather-type-center-placeholder">悬停查看</div>
              )}
            </div>
          </div>
        </ChartPanel>
      </div>
    </section>
  );
}
