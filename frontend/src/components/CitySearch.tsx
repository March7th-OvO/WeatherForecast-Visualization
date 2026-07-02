import { Search } from "lucide-react";
import { FormEvent, useState } from "react";

interface CitySearchProps {
  defaultCity: string;
  onSearch: (cityName: string) => void;
}

export function CitySearch({ defaultCity, onSearch }: CitySearchProps) {
  const [cityName, setCityName] = useState(defaultCity);

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    onSearch(cityName.trim() || defaultCity);
  }

  return (
    <form className="search-row" onSubmit={handleSubmit}>
      <input
        aria-label="城市名称"
        value={cityName}
        onChange={(event) => setCityName(event.target.value)}
        placeholder="请输入城市名，如上海"
      />
      <button type="submit" aria-label="查询天气">
        <Search size={18} />
        <span>查询</span>
      </button>
    </form>
  );
}
