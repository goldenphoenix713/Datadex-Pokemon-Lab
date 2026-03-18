import pyarrow as pa
import pyarrow.compute as pc
import threading
from data_manager import load_and_clean_data
from src.constants import STAT_OPTIONS
from typing import Any

# Load and prepare data on startup
pokemon_table = load_and_clean_data()
pokemon_names = sorted(pokemon_table["Name"].to_pylist())

# Thread lock for shared DuckDB connection access
db_lock = threading.Lock()

# Pre-calculate global max stat for progress bars once (instead of per callback)
MAX_BASE_STAT = pc.max(
    pa.array([pc.max(pokemon_table[name]) for name in STAT_OPTIONS])
).as_py()

# Preparation for themed dropdowns with sprites
pokemon_sprites = dict(
    zip(pokemon_table["Name"].to_pylist(), pokemon_table["Sprite_URL"].to_pylist())
)
pokemon_ids = dict(
    zip(pokemon_table["Name"].to_pylist(), pokemon_table["id"].to_pylist())
)

# Phase 3: Pre-process evolution chains into a species-to-forms map
# This avoids doing SQL queries per click in the evolution lineage UI.
evolution_map: dict[str, list[dict[str, Any]]] = {}
name_to_pokemon: dict[str, dict[str, Any]] = {}
for row in pokemon_table.to_pylist():
    species = row["Species_Name"]
    if species not in evolution_map:
        evolution_map[species] = []
    evolution_map[species].append(row)
    name_to_pokemon[row["Name"]] = row
