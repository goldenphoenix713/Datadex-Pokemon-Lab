"""Offline asset pre-fetching script for Data-Dex.

Run this once to warm the local asset cache before deploying or demoing the app.
The app itself never calls these functions at runtime anymore — it serves CDN
URLs directly to the browser and falls back to local files when they exist.

Usage:
    python scripts/prefetch_assets.py              # pre-fetch all assets
    python scripts/prefetch_assets.py --images     # only official artwork
    python scripts/prefetch_assets.py --sprites    # only mini sprites
    python scripts/prefetch_assets.py --cries      # only cry .ogg files
"""

import argparse
import sys
from pathlib import Path

# Allow running from the project root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from concurrent.futures import ThreadPoolExecutor
from loguru import logger
from data_manager import (
    load_and_clean_data,
    ensure_pokemon_image,
    ensure_pokemon_sprite,
    ensure_pokemon_cry,
)


def prefetch_images(pokemon_table) -> None:
    """Download official artwork (normal + shiny) for all Pokémon."""
    rows = pokemon_table.select(["id", "Name", "Has_Shiny"]).to_pylist()
    logger.info(f"Pre-fetching artwork for {len(rows)} Pokémon...")

    def _fetch(row):
        p_id, name, has_shiny = int(row["id"]), row["Name"], row["Has_Shiny"]
        ensure_pokemon_image(p_id, name, shiny=False)
        if has_shiny:
            ensure_pokemon_image(p_id, name, shiny=True)

    with ThreadPoolExecutor(max_workers=10) as executor:
        list(executor.map(_fetch, rows))
    logger.info("Artwork pre-fetch complete.")


def prefetch_sprites(pokemon_table) -> None:
    """Download mini sprites for all Pokémon."""
    rows = pokemon_table.select(["id", "Name"]).to_pylist()
    logger.info(f"Pre-fetching sprites for {len(rows)} Pokémon...")

    def _fetch(row):
        ensure_pokemon_sprite(int(row["id"]), row["Name"])

    with ThreadPoolExecutor(max_workers=10) as executor:
        list(executor.map(_fetch, rows))
    logger.info("Sprite pre-fetch complete.")


def prefetch_cries(pokemon_table) -> None:
    """Download cry audio for all Pokémon."""
    rows = pokemon_table.select(["id", "Name"]).to_pylist()
    logger.info(f"Pre-fetching cries for {len(rows)} Pokémon...")

    def _fetch(row):
        ensure_pokemon_cry(int(row["id"]), row["Name"])

    with ThreadPoolExecutor(max_workers=10) as executor:
        list(executor.map(_fetch, rows))
    logger.info("Cry pre-fetch complete.")


def main():
    parser = argparse.ArgumentParser(description="Pre-fetch Pokémon assets locally.")
    parser.add_argument("--images", action="store_true", help="Fetch official artwork")
    parser.add_argument("--sprites", action="store_true", help="Fetch mini sprites")
    parser.add_argument("--cries", action="store_true", help="Fetch cry audio")
    args = parser.parse_args()

    # If no flags, fetch everything
    fetch_all = not (args.images or args.sprites or args.cries)

    pokemon_table = load_and_clean_data()

    if fetch_all or args.images:
        prefetch_images(pokemon_table)
    if fetch_all or args.sprites:
        prefetch_sprites(pokemon_table)
    if fetch_all or args.cries:
        prefetch_cries(pokemon_table)


if __name__ == "__main__":
    main()
