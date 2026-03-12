import requests
import pandas as pd  # type: ignore[import-untyped]
import os
from concurrent.futures import ThreadPoolExecutor


def fetch_single_pokemon(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        stats = {stat["stat"]["name"]: stat["base_stat"] for stat in data["stats"]}
        types = [t["type"]["name"] for t in data["types"]]

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
        print(f"Error fetching {url}: {e}")
        return None


def fetch_all_pokemon():
    print("Fetching list of all Pokémon entries...")
    base_url = "https://pokeapi.co/api/v2/pokemon?limit=2000"
    response = requests.get(base_url)
    response.raise_for_status()
    results = response.json()["results"]

    print(f"Total entries found: {len(results)}. Starting multi-threaded fetch...")

    with ThreadPoolExecutor(max_workers=20) as executor:
        pokemon_list = list(
            filter(
                None, executor.map(fetch_single_pokemon, [r["url"] for r in results])
            )
        )

    df = pd.DataFrame(pokemon_list)

    # User's request: "all pokemon forms with any statistical differences or types"
    # We drop duplicates where stats, types, and the base name ID are identical,
    # but the API's /pokemon endpoint usually already only contains significant variety.
    # However, some 'forms' have the same stats as base.
    # Let's keep one entry per unique set of stats + types + name.

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

    # Store cleaning renames logic here or in data_manager
    df["Type 1"] = df["Type 1"].astype("category")
    df["Type 2"] = df["Type 2"].astype("category")

    os.makedirs("data", exist_ok=True)
    filepath = "data/pokemon.parquet"
    df.to_parquet(filepath, engine="pyarrow", compression="zstd")

    print(
        f"Fetched {initial_count} entries. Saved {len(df)} unique entries to {filepath}."
    )


if __name__ == "__main__":
    fetch_all_pokemon()
