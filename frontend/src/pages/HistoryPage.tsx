import { useState } from "react";

import { getHistory } from "../api/weatherApi";
import { CitySearch } from "../components/CitySearch";
import { ErrorState, LoadingState } from "../components/PageState";
import { HistoryTable } from "../components/HistoryTable";
import { useAsyncData } from "../hooks/useAsyncData";

const DEFAULT_CITY = "北京";

export function HistoryPage() {
  const [cityName, setCityName] = useState(DEFAULT_CITY);
  const { data, error, loading } = useAsyncData(() => getHistory(cityName), [cityName]);

  return (
    <section className="page-section">
      <header className="page-header">
        <div>
          <p>History</p>
          <h2>15日天气</h2>
        </div>
      </header>

      <CitySearch defaultCity={DEFAULT_CITY} onSearch={setCityName} />

      {loading && <LoadingState message="正在加载历史天气" />}
      {error && <ErrorState message={error} />}
      {!loading && !error && <HistoryTable rows={data ?? []} />}
    </section>
  );
}
