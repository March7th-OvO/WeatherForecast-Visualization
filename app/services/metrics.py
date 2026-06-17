def build_overview(rows: list[dict]) -> dict:
    return {
        "total_records": len(rows),
        "total_cities": len({row["city_name"] for row in rows}),
        "highest_temp": max(row["high_temp"] for row in rows),
        "lowest_temp": min(row["low_temp"] for row in rows),
    }
