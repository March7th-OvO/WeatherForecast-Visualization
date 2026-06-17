async function loadHistory(cityName = "北京") {
  const response = await fetch(`/api/history?city_name=${encodeURIComponent(cityName)}`);
  const rows = await response.json();
  const tbody = document.getElementById("history-body");

  tbody.innerHTML = rows
    .map(
      (row) => `
        <tr>
          <td>${row.city_name}</td>
          <td>${row.weather_date}</td>
          <td>${row.weather_type}</td>
          <td>${row.high_temp}</td>
          <td>${row.low_temp}</td>
          <td>${row.wind_level}</td>
        </tr>
      `
    )
    .join("");
}

document.getElementById("search-button").addEventListener("click", () => {
  const cityName = document.getElementById("city-input").value.trim() || "北京";
  loadHistory(cityName);
});

loadHistory();
