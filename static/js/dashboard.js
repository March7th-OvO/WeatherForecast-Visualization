async function loadDashboard() {
  const response = await fetch("/api/dashboard");
  const payload = await response.json();

  document.getElementById("total-records").textContent = payload.overview.total_records;
  document.getElementById("total-cities").textContent = payload.overview.total_cities;
  document.getElementById("highest-temp").textContent = payload.overview.highest_temp;
  document.getElementById("lowest-temp").textContent = payload.overview.lowest_temp;

  const trendChart = echarts.init(document.getElementById("trend-chart"));
  trendChart.setOption({
    title: { text: "近 30 天平均最高温趋势" },
    tooltip: {},
    xAxis: { type: "category", data: payload.trend.map((item) => item.weather_date) },
    yAxis: { type: "value" },
    series: [{ type: "line", data: payload.trend.map((item) => item.avg_high_temp), smooth: true }],
  });

  const typeChart = echarts.init(document.getElementById("type-chart"));
  typeChart.setOption({
    title: { text: "天气类型分布" },
    tooltip: {},
    xAxis: { type: "category", data: payload.weather_types.map((item) => item.weather_type) },
    yAxis: { type: "value" },
    series: [{ type: "bar", data: payload.weather_types.map((item) => item.count), itemStyle: { color: "#4a90e2" } }],
  });
}

loadDashboard();
