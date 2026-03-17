from typing import Any, List


def compute_type_averages(df: Any, stat_column: str) -> List[dict]:
    """Compute average of a stat grouped by type using DuckDB."""
    from src.data import conn, db_lock

    try:
        with db_lock:
            conn.register("current_filtered", df)
            query = f"""
            WITH all_types AS (
                SELECT "Primary Type" as itype, "{stat_column}" as stat FROM current_filtered
                UNION ALL
                SELECT "Secondary Type" as itype, "{stat_column}" as stat FROM current_filtered WHERE "Secondary Type" != 'None'
            )
            SELECT itype as "Primary Type", AVG(stat) as avg_stat
            FROM all_types GROUP BY itype ORDER BY avg_stat DESC
            """
            return conn.execute(query).to_arrow_table().to_pylist()
    finally:
        with db_lock:
            try:
                conn.unregister("current_filtered")
            except Exception:
                pass


def get_global_avg(df: Any, stat_column: str) -> float:
    """Compute the global average for a stat within the filtered dataset."""
    from src.data import conn, db_lock

    try:
        with db_lock:
            conn.register("current_filtered", df)
            res = (
                conn.execute(f'SELECT AVG("{stat_column}") FROM current_filtered')
                .to_arrow_table()
                .to_pylist()
            )
            return res[0][list(res[0].keys())[0]] if res and res[0] else 0.0
    finally:
        with db_lock:
            try:
                conn.unregister("current_filtered")
            except Exception:
                pass


def get_max_stat_value(table: Any, categories: List[str]) -> float:
    """Find the global maximum value across specific stat categories."""
    from src.data import conn, db_lock

    stat_columns = ", ".join([f'"{c}"' for c in categories])
    try:
        with db_lock:
            conn.register("radar_set_max", table)
            res = (
                conn.execute(f"SELECT MAX(GREATEST({stat_columns})) FROM radar_set_max")
                .to_arrow_table()
                .to_pylist()
            )
            if res and res[0]:
                val = list(res[0].values())[0]
                return float(val) if val is not None else 255.0
            return 255.0
    finally:
        with db_lock:
            try:
                conn.unregister("radar_set_max")
            except Exception:
                pass
