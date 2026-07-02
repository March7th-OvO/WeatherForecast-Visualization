export interface Overview {
  total_records: number;
  total_cities: number;
  highest_temp: number;
  lowest_temp: number;
}

export interface TemperatureTrendPoint {
  weather_date: string;
  avg_high_temp: number;
}

export interface WeatherTypeCount {
  weather_type: string;
  count: number;
}

export interface DashboardPayload {
  overview: Overview;
  trend: TemperatureTrendPoint[];
  weather_types: WeatherTypeCount[];
}

export interface ProvinceTemperature {
  province_name: string;
  avg_high_temp: number;
}

export interface MapPayload {
  provinces: ProvinceTemperature[];
}

export interface CityAverageTemperature {
  city_name: string;
  avg_high_temp: number;
  avg_low_temp: number;
}

export interface AnalysisPayload {
  high_top10: CityAverageTemperature[];
  low_top10: CityAverageTemperature[];
  weather_types: WeatherTypeCount[];
}

export interface WeatherHistoryRow {
  city_name: string;
  weather_date: string;
  weather_type: string;
  high_temp: number;
  low_temp: number;
  wind_level: string;
}
