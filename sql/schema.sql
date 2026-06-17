CREATE DATABASE IF NOT EXISTS weather_visualization DEFAULT CHARACTER SET utf8mb4;
USE weather_visualization;

DROP TABLE IF EXISTS weather_daily;

CREATE TABLE weather_daily (
    id INT PRIMARY KEY AUTO_INCREMENT,
    city_name VARCHAR(50) NOT NULL,
    weather_date DATE NOT NULL,
    weather_type VARCHAR(30) NOT NULL,
    high_temp INT NOT NULL,
    low_temp INT NOT NULL,
    wind_level VARCHAR(20) NOT NULL,
    UNIQUE KEY uniq_city_date (city_name, weather_date)
);
