import pyarrow as pa
import pyarrow.compute as pc
from typing import Any, List

# Manual cache to avoid hashing the Arrow table directly
_averages_cache: dict[tuple[int, str], list[dict[str, Any]]] = {}
_global_avg_cache: dict[tuple[int, str], float] = {}
MAX_CACHE_SIZE = 32


def compute_type_averages(pokemon_table: Any, stat_column: str) -> List[dict]:
    """Compute average of a stat grouped by type using PyArrow with manual caching."""
    cache_key = (id(pokemon_table), stat_column)
    if cache_key in _averages_cache:
        return _averages_cache[cache_key]

    # PyArrow implementation of the type-averaging logic:
    # 1. Select Primary Type + stat
    t1 = pokemon_table.select(["Primary Type", stat_column]).rename_columns(
        ["itype", "stat"]
    )

    # 2. Select Secondary Type + stat, filtering out 'None'
    mask = pc.not_equal(pokemon_table["Secondary Type"], "None")
    t2 = (
        pokemon_table.filter(mask)
        .select(["Secondary Type", stat_column])
        .rename_columns(["itype", "stat"])
    )

    # 3. Concatenate (equivalent to UNION ALL)
    all_types = pa.concat_tables([t1, t2])

    # 4. Group by type and compute mean
    agg_table = all_types.group_by("itype").aggregate([("stat", "mean")])

    # 5. Rename columns and sort descending by average
    agg_table = agg_table.rename_columns(["Primary Type", "avg_stat"])
    agg_table = agg_table.sort_by([("avg_stat", "descending")])

    result = agg_table.to_pylist()

    # Simple LRU-like cleanup
    if len(_averages_cache) >= MAX_CACHE_SIZE:
        _averages_cache.pop(next(iter(_averages_cache)))
    _averages_cache[cache_key] = result
    return result


def get_global_avg(pokemon_table: Any, stat_column: str) -> float:
    """Compute the global average for a stat within the filtered dataset with manual caching."""
    cache_key = (id(pokemon_table), stat_column)
    if cache_key in _global_avg_cache:
        return _global_avg_cache[cache_key]

    # Native PyArrow mean calculation
    result = pc.mean(pokemon_table[stat_column]).as_py() or 0.0

    if len(_global_avg_cache) >= MAX_CACHE_SIZE:
        _global_avg_cache.pop(next(iter(_global_avg_cache)))
    _global_avg_cache[cache_key] = result
    return result
