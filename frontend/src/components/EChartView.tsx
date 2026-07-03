import * as echarts from "echarts";
import { useEffect, useRef } from "react";

declare global {
  interface Window {
    echarts?: typeof echarts;
  }
}

interface EChartViewProps {
  option: Record<string, unknown>;
  className?: string;
  requiresChinaMap?: boolean;
  onEvents?: Record<string, (params: unknown) => void>;
}

let chinaMapPromise: Promise<void> | null = null;

function ensureChinaMap(): Promise<void> {
  if (echarts.getMap("china")) {
    return Promise.resolve();
  }

  if (!chinaMapPromise) {
    window.echarts = echarts;
    chinaMapPromise = new Promise((resolve, reject) => {
      const script = document.createElement("script");
      script.src = "/vendor/china.js";
      script.async = true;
      script.onload = () => resolve();
      script.onerror = () => reject(new Error("中国地图资源加载失败"));
      document.head.appendChild(script);
    });
  }

  return chinaMapPromise;
}

export function EChartView({
  option,
  className = "",
  requiresChinaMap = false,
  onEvents,
}: EChartViewProps) {
  const chartRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (import.meta.env.MODE === "test" || !chartRef.current) {
      return;
    }

    let disposed = false;
    let chart: echarts.ECharts | null = null;

    async function renderChart() {
      if (requiresChinaMap) {
        await ensureChinaMap();
      }

      if (!chartRef.current || disposed) {
        return;
      }

      chart = echarts.init(chartRef.current);
      chart.setOption(option as echarts.EChartsOption);
      Object.entries(onEvents ?? {}).forEach(([eventName, handler]) => {
        chart?.on(eventName, handler);
      });
    }

    renderChart();

    const handleResize = () => chart?.resize();
    window.addEventListener("resize", handleResize);

    return () => {
      disposed = true;
      window.removeEventListener("resize", handleResize);
      Object.entries(onEvents ?? {}).forEach(([eventName, handler]) => {
        chart?.off(eventName, handler);
      });
      chart?.dispose();
    };
  }, [option, requiresChinaMap, onEvents]);

  return <div className={`chart-canvas ${className}`} ref={chartRef} />;
}
