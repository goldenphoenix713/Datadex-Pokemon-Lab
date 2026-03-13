"""Module to fetch Pokémon data from the PokéAPI and save it to a parquet file."""

import os
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, Optional

import pandas as pd
import requests
from loguru import logger


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


def fetch_single_pokemon(url: str) -> Optional[Dict[str, Any]]:
    """Fetch data for a single Pokémon from the given PokéAPI URL."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        stats = {stat["stat"]["name"]: stat["base_stat"] for stat in data["stats"]}
        types = [t["type"]["name"] for t in data["types"]]

        # Fetch species data for legendary/mythical status
        species_info = fetch_species_data(data["species"]["url"])

        return {
            "#": data["id"],
            "Name": data["name"].replace("-", " ").title(),
            "Species_Name": data["species"][
                "name"
            ],  # Useful for matching evolution chains
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


def fetch_all_pokemon() -> None:
    """Fetch all Pokémon entries from PokéAPI, filter, and save to parquet."""
    logger.info("Fetching list of all Pokémon entries...")
    base_url = "https://pokeapi.co/api/v2/pokemon?limit=2000"
    response = requests.get(base_url)
    response.raise_for_status()
    results = response.json()["results"]

    logger.info(
        f"Total entries found: {len(results)}. Starting multi-threaded fetch..."
    )

    with ThreadPoolExecutor(max_workers=20) as executor:
        pokemon_list = list(
            filter(
                None, executor.map(fetch_single_pokemon, [r["url"] for r in results])
            )
        )

    # Convert results into a DataFrame
    df = pd.DataFrame(pokemon_list)

    # Get final evolutions set
    final_evolutions = get_final_evolutions()
    # Mark final evolutions by species name
    df["Is_Final_Evolution"] = df["Species_Name"].isin(final_evolutions)

    # Filter for unique entries
    initial_count = len(df)
    df = df.drop_duplicates(
        subset=[
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
    )

    # Standardize data types
    df["Type 1"] = df["Type 1"].astype("category")
    df["Type 2"] = df["Type 2"].astype("category")

    # Save to disk
    os.makedirs("data", exist_ok=True)
    filepath = "data/pokemon.parquet"
    df.to_parquet(filepath, engine="pyarrow", compression="zstd")

    logger.info(
        f"Fetched {initial_count} entries. Saved {len(df)} unique entries to {filepath}."
    )


if __name__ == "__main__":
    fetch_all_pokemon()
