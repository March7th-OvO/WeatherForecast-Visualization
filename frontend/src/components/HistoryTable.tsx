import type { WeatherHistoryRow } from "../api/types";

interface HistoryTableProps {
  rows: WeatherHistoryRow[];
}

export function HistoryTable({ rows }: HistoryTableProps) {
  if (rows.length === 0) {
    return <div className="empty-state">暂无天气记录</div>;
  }

  return (
    <div className="table-wrap">
      <table className="history-table">
        <thead>
          <tr>
            <th>城市</th>
            <th>日期</th>
            <th>天气</th>
            <th>最高温</th>
            <th>最低温</th>
            <th>风力</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={`${row.city_name}-${row.weather_date}`}>
              <td>{row.city_name}</td>
              <td>{row.weather_date}</td>
              <td>{row.weather_type}</td>
              <td>{row.high_temp}</td>
              <td>{row.low_temp}</td>
              <td>{row.wind_level}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
