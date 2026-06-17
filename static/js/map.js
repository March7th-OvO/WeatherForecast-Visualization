async function loadMap() {
  const response = await fetch("/api/map");
  const payload = await response.json();
  const chart = echarts.init(document.getElementById("map-chart"));

  chart.setOption({
    title: { text: "全国各省平均最高温分布" },
    visualMap: { min: -20, max: 40, left: "left", bottom: 24 },
    series: [
      {
        type: "map",
        map: "china",
        roam: true,
        data: payload.provinces.map((item) => ({ name: item.province_name, value: item.avg_high_temp })),
      },
    ],
  });
}

loadMap();
