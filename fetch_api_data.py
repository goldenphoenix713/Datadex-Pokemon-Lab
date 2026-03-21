"""Module to fetch Pokémon data from the PokéAPI and save it to a parquet file."""

import argparse
import os
import threading
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, List, Optional, Set

import requests  # type: ignore[import]
from loguru import logger
import pyarrow as pa
import duckdb


def fetch_species_data(species_url: str) -> Dict[str, Any]:
    """Fetch legendaries, mythicals, and evolution chain URL from species endpoint."""
    try:
        response = requests.get(species_url, timeout=10)
        response.raise_for_status()
        data = response.json()
        return {
            "is_legendary": data["is_legendary"],
            "is_mythical": data["is_mythical"],
            "evolution_chain_url": data["evolution_chain"]["url"],
        }
    except Exception as e:
        logger.error(f"Error fetching species data {species_url}: {e}")
        return {
            "is_legendary": False,
            "is_mythical": False,
            "evolution_chain_url": None,
        }


# Cache to store evolution chain members to avoid redundant API calls.
# Guarded by a Lock so concurrent threads can read/write safely.
EVOLUTION_CHAIN_CACHE: Dict[str, List[str]] = {}
_evo_cache_lock = threading.Lock()


def fetch_evolution_members(url: str) -> List[str]:
    """Fetch and parse evolution chain members from the given URL (thread-safe)."""
    if not url:
        return []

    # Fast path: check cache under lock
    with _evo_cache_lock:
        if url in EVOLUTION_CHAIN_CACHE:
            return EVOLUTION_CHAIN_CACHE[url]

    # Slow path: fetch from API (done outside the lock so we don't block other threads)
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        members: List[str] = []

        def parse_node(node: Dict[str, Any]) -> None:
            members.append(node["species"]["name"])
            for evolution in node["evolves_to"]:
                parse_node(evolution)

        parse_node(data["chain"])

        # Write back under lock (another thread may have populated this in the meantime;
        # writing the same value is harmless)
        with _evo_cache_lock:
            EVOLUTION_CHAIN_CACHE[url] = members

        return members
    except Exception as e:
        logger.error(f"Error fetching evolution chain {url}: {e}")
        return []


SHINY_ARTWORK_BASE_URL = (
    "https://raw.githubusercontent.com/PokeAPI/sprites/"
    "master/sprites/pokemon/other/official-artwork/shiny/"
)


def _check_shiny_exists(pokemon_id: int) -> bool:
    """Check if a shiny official artwork exists on the CDN for the given Pokémon ID."""
    url = f"{SHINY_ARTWORK_BASE_URL}{pokemon_id}.png"
    try:
        response = requests.head(url, timeout=5)
        return response.status_code == 200
    except Exception as e:
        logger.error(f"Error checking shiny for ID {pokemon_id}: {e}")
        return False


def fetch_single_pokemon(url: str) -> Optional[Dict[str, Any]]:
    """Fetch data for a single Pokémon from the given PokéAPI URL."""
    logger.info(f"Fetching data for {url}")
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        stats = {stat["stat"]["name"]: stat["base_stat"] for stat in data["stats"]}
        types = [t["type"]["name"] for t in data["types"]]

        # Fetch species data for legendary/mythical status and evolution chain
        species_info = fetch_species_data(data["species"]["url"])

        # Fetch all members of the evolution chain
        chain_members = fetch_evolution_members(species_info["evolution_chain_url"])
        # Store as a comma-separated string for easy storage in Parquet/CSV
        chain_members_str = ",".join(chain_members)

        # Check shiny artwork availability at build time so runtime never needs to
        pokemon_id = data["id"]
        has_shiny = _check_shiny_exists(pokemon_id)

        return {
            "#": pokemon_id,
            "Name": data["name"].replace("-", " ").title(),
            "Species_Name": data["species"]["name"],
            "Type 1": types[0].capitalize(),
            "Type 2": types[1].capitalize() if len(types) > 1 else None,
            "HP": stats["hp"],
            "Attack": stats["attack"],
            "Defense": stats["defense"],
            "Sp. Atk": stats["special-attack"],
            "Sp. Def": stats["special-defense"],
            "Speed": stats["speed"],
            "Height": data["height"],
            "Weight": data["weight"],
            "Is_Legendary": species_info["is_legendary"],
            "Is_Mythical": species_info["is_mythical"],
            "Evolution_Chain_URL": species_info["evolution_chain_url"],
            "Evolution_Chain_Members": chain_members_str,
            "Has_Shiny": has_shiny,
        }
    except Exception as e:
        logger.error(f"Error fetching {url}: {e}")
        return None


def get_final_evolutions() -> set:
    """Identify all species that are at the end of their evolution chain."""
    logger.info("Fetching and parsing evolution chains...")
    base_url = "https://pokeapi.co/api/v2/evolution-chain?limit=1000"
    try:
        response = requests.get(base_url, timeout=10)
        response.raise_for_status()
        chains_refs = response.json()["results"]

        final_species = set()

        def parse_chain(node):
            if not node["evolves_to"]:
                # This is a leaf node (final evolution)
                final_species.add(node["species"]["name"])
            else:
                for sub_node in node["evolves_to"]:
                    parse_chain(sub_node)

        def fetch_and_parse(url):
            try:
                res = requests.get(url, timeout=10)
                if res.status_code == 200:
                    parse_chain(res.json()["chain"])
            except Exception as e:
                logger.error(f"Error parsing chain {url}: {e}")

        with ThreadPoolExecutor(max_workers=20) as executor:
            executor.map(fetch_and_parse, [ref["url"] for ref in chains_refs])

        return final_species
    except Exception as e:
        logger.error(f"Error fetching evolution chains: {e}")
        return set()


def _load_existing_ids(filepath: str) -> Set[int]:
    """Return the set of Pokémon IDs already present in the Parquet file."""
    import pyarrow.parquet as pq
    from pathlib import Path

    if not Path(filepath).exists():
        return set()
    try:
        table = pq.read_table(filepath, columns=["#"])
        return set(table["#"].to_pylist())
    except Exception as e:
        logger.warning(f"Could not read existing Parquet for delta check: {e}")
        return set()


def fetch_all_pokemon(force: bool = False) -> None:
    """Fetch Pokémon entries from PokéAPI and save to parquet.

    By default, only new entries not already present in the existing Parquet
    are fetched (delta/incremental mode). Pass ``force=True`` (or ``--force``
    on the CLI) to trigger a full rebuild from scratch.
    """
    filepath = "data/pokemon.parquet"

    logger.info("Fetching list of all Pokémon entries...")
    base_url = "https://pokeapi.co/api/v2/pokemon?limit=2000"
    response = requests.get(base_url)
    response.raise_for_status()
    results = response.json()["results"]

    # --- Delta filtering ---------------------------------------------------
    existing_ids: Set[int] = set()
    if not force:
        existing_ids = _load_existing_ids(filepath)
        if existing_ids:
            logger.info(
                f"Delta mode: {len(existing_ids)} existing entries found. "
                "Only fetching new/unknown entries."
            )
        else:
            logger.info("No existing Parquet found — performing full fetch.")

    if force and existing_ids:
        logger.info("--force specified: ignoring existing Parquet, full rebuild.")
        existing_ids = set()

    # Extract ID from each PokéAPI URL for pre-filtering
    def url_to_id(url: str) -> Optional[int]:
        try:
            return int(url.rstrip("/").split("/")[-1])
        except ValueError:
            return None

    urls_to_fetch = [
        r["url"]
        for r in results
        if (pid := url_to_id(r["url"])) is not None and pid not in existing_ids
    ]

    if not urls_to_fetch:
        logger.info("All entries already up-to-date. Nothing to fetch.")
        return

    logger.info(
        f"{len(urls_to_fetch)} entries to fetch (skipping {len(existing_ids)} existing). "
        "Starting multi-threaded fetch..."
    )
    # -----------------------------------------------------------------------

    with ThreadPoolExecutor(max_workers=20) as executor:
        new_pokemon = list(
            filter(None, executor.map(fetch_single_pokemon, urls_to_fetch))
        )

    if not new_pokemon:
        logger.warning("No new Pokémon data fetched. Parquet not updated.")
        return

    # If incremental: merge new rows with existing Parquet data
    if existing_ids and not force:
        import pyarrow.parquet as pq

        existing_table = pq.read_table(filepath)
        new_table = pa.Table.from_pylist(new_pokemon)
        # Align schemas before concatenating (new columns like Has_Shiny may be absent in old data)
        for col in new_table.schema.names:
            if col not in existing_table.schema.names:
                existing_table = existing_table.append_column(
                    col,
                    pa.array(
                        [None] * existing_table.num_rows,
                        type=new_table.schema.field(col).type,
                    ),
                )
        table = pa.concat_tables([existing_table, new_table], promote_options="default")
    else:
        table = pa.Table.from_pylist(new_pokemon)

    # Get final evolutions set
    final_evolutions = list(get_final_evolutions())

    # Use DuckDB for efficient transformation and deduplication
    con = duckdb.connect(":memory:")
    con.register("raw_table", table)

    species_list_str = ", ".join([f"'{s}'" for s in final_evolutions])
    initial_count = table.num_rows

    dedup_cols = [
        "Type 1",
        "Type 2",
        "HP",
        "Attack",
        "Defense",
        "Sp. Atk",
        "Sp. Def",
        "Speed",
        "Name",
    ]
    cols_str = ", ".join([f'"{c}"' for c in dedup_cols])

    query = f"""
    SELECT *,
        CASE WHEN "Species_Name" IN ({species_list_str}) THEN True ELSE False END as "Is_Final_Evolution"
    FROM raw_table
    QUALIFY row_number() OVER (PARTITION BY {cols_str} ORDER BY "#") = 1
    """

    table = con.execute(query).to_arrow_table()

    # Save to disk
    os.makedirs("data", exist_ok=True)
    import pyarrow.parquet as pq

    pq.write_table(table, filepath, compression="zstd")
    logger.info(
        f"Processed {initial_count} entries. Saved {table.num_rows} unique entries to {filepath}."
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Fetch Pokémon data from PokéAPI and save to data/pokemon.parquet."
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force a full rebuild, ignoring any existing Parquet data.",
    )
    args = parser.parse_args()
    fetch_all_pokemon(force=args.force)
