import duckdb
import threading
from data_manager import load_and_clean_data
from src.constants import STAT_OPTIONS
from typing import Any

# Load and prepare data on startup
df = load_and_clean_data()
pokemon_names = sorted(df["Name"].to_pylist())

# Thread lock for shared DuckDB connection access
db_lock = threading.Lock()

# Pre-calculate global max stat for progress bars once (instead of per callback)
conn = duckdb.connect(":memory:")
with db_lock:
    conn.register("pokemon", df)
    stat_columns = ", ".join([f'"{c}"' for c in STAT_OPTIONS])
    res = conn.execute(f"SELECT MAX(GREATEST({stat_columns})) FROM pokemon").fetchone()
    MAX_BASE_STAT = res[0] if res and res[0] is not None else 255

# Preparation for themed dropdowns with sprites
pokemon_sprites = dict(zip(df["Name"].to_pylist(), df["Sprite_URL"].to_pylist()))
pokemon_ids = dict(zip(df["Name"].to_pylist(), df["id"].to_pylist()))

# Phase 3: Pre-process evolution chains into a species-to-forms map
# This avoids doing SQL queries per click in the evolution lineage UI.
evolution_map: dict[str, list[dict[str, Any]]] = {}
for row in df.to_pylist():
    species = row["Species_Name"]
    if species not in evolution_map:
        evolution_map[species] = []
    evolution_map[species].append(row)
