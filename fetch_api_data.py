"""Module to fetch Pokémon data from the PokéAPI and save it to a parquet file."""

import os
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, Optional

import pandas as pd
import requests
from loguru import logger


def fetch_single_pokemon(url: str) -> Optional[Dict[str, Any]]:
    """Fetch data for a single Pokémon from the given PokéAPI URL.

    :param url: The API URL for a specific Pokémon.
    :type url: str
    :return: A dictionary containing filtered Pokémon attributes, or None if the fetch fails.
    :rtype: Optional[Dict[str, Any]]
    """
    try:
        # Request data from the PokeAPI
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Simplify stat structure: stats list -> dictionary mapping
        stats = {stat["stat"]["name"]: stat["base_stat"] for stat in data["stats"]}
        # Extract type names into a list
        types = [t["type"]["name"] for t in data["types"]]

        # Map API response to our flat dictionary format
        return {
            "#": data["id"],
            "Name": data["name"].replace("-", " ").title(),
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
        }
    except Exception as e:
        # Log error but don't crash; let other fetches continue
        logger.error(f"Error fetching {url}: {e}")
        return None


def fetch_all_pokemon() -> None:
    """Fetch all Pokémon entries from PokéAPI, filter, and save to parquet."""
    logger.info("Fetching list of all Pokémon entries...")
    # Get all potential results (limit=2000 covers all current generations)
    base_url = "https://pokeapi.co/api/v2/pokemon?limit=2000"
    response = requests.get(base_url)
    response.raise_for_status()
    results = response.json()["results"]

    logger.info(
        f"Total entries found: {len(results)}. Starting multi-threaded fetch..."
    )

    # Parallelize API calls to avoid bottlenecking (max 20 workers to be polite to API)
    with ThreadPoolExecutor(max_workers=20) as executor:
        pokemon_list = list(
            filter(
                None, executor.map(fetch_single_pokemon, [r["url"] for r in results])
            )
        )

    # Convert results into a DataFrame for easy manipulation
    df = pd.DataFrame(pokemon_list)

    # Filter for unique entries based on gameplay identity (Name + Stats + Types)
    # This handles PokéAPI providing separate entries for different forms/varieties.
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

    # Optimize column types (categorical is better for plotly/pandas filtering)
    df["Type 1"] = df["Type 1"].astype("category")
    df["Type 2"] = df["Type 2"].astype("category")

    # Save to disk using Parquet with high compression (ZSTD)
    os.makedirs("data", exist_ok=True)
    filepath = "data/pokemon.parquet"
    df.to_parquet(filepath, engine="pyarrow", compression="zstd")

    logger.info(
        f"Fetched {initial_count} entries. Saved {len(df)} unique entries to {filepath}."
    )


if __name__ == "__main__":
    fetch_all_pokemon()
