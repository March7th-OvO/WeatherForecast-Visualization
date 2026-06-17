async function loadAnalysis() {
  const response = await fetch("/api/analysis");
  const payload = await response.json();

  echarts.init(document.getElementById("high-chart")).setOption({
    title: { text: "城市平均最高温 Top10" },
    xAxis: { type: "category", data: payload.high_top10.map((item) => item.city_name) },
    yAxis: { type: "value" },
    series: [{ type: "bar", data: payload.high_top10.map((item) => item.avg_high_temp) }],
  });

  echarts.init(document.getElementById("low-chart")).setOption({
    title: { text: "城市平均最低温 Top10" },
    xAxis: { type: "category", data: payload.low_top10.map((item) => item.city_name) },
    yAxis: { type: "value" },
    series: [{ type: "bar", data: payload.low_top10.map((item) => item.avg_low_temp), itemStyle: { color: "#36a2eb" } }],
  });

  echarts.init(document.getElementById("pie-chart")).setOption({
    title: { text: "天气类型占比" },
    tooltip: { trigger: "item" },
    series: [
      {
        type: "pie",
        radius: ["40%", "70%"],
        data: payload.weather_types.map((item) => ({ name: item.weather_type, value: item.count })),
      },
    ],
  });
}

loadAnalysis();
