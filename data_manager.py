"""Module for loading, cleaning, and managing Pokémon data and assets."""

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pandas as pd
import requests
from loguru import logger

# Image URL for official artwork
OFFICIAL_ARTWORK_URL = (
    "https://raw.githubusercontent.com/PokeAPI/sprites/"
    + "master/sprites/pokemon/other/official-artwork/"
)


def load_and_clean_data(filepath: str = "data/pokemon.parquet") -> pd.DataFrame:
    """Load Pokémon data from a parquet file and clean it.

    :param filepath: Path to the parquet data file. Defaults to "data/pokemon.parquet".
    :type filepath: str
    :return: A cleaned pandas DataFrame with localized image paths.
    :rtype: pd.DataFrame
    """
    logger.info(f"Loading Pokémon data from {filepath}...")
    # Load the raw data from Parquet
    try:
        df = pd.read_parquet(filepath, engine="pyarrow")
        logger.debug(f"Successfully loaded {len(df)} initial records.")
    except Exception as e:
        logger.error(f"Failed to load data from {filepath}: {e}")
        raise

    # Ensure the assets and images directories exist for local storage
    assets_dir = Path("assets")
    if not assets_dir.exists():
        assets_dir.mkdir()

    images_dir = assets_dir / "images"
    if not images_dir.exists():
        images_dir.mkdir()

    # Rename stats to more readable full names for the UI
    logger.debug("Renaming columns for UI readability...")
    rename_map = {
        "Sp. Atk": "Special Attack",
        "Sp. Def": "Special Defense",
        "Type 1": "Primary Type",
        "Type 2": "Secondary Type",
    }
    df = df.rename(columns=rename_map)

    # Handle missing secondary types by creating a 'None' category
    if "Secondary Type" in df.columns and hasattr(df["Secondary Type"], "cat"):
        df["Secondary Type"] = (
            df["Secondary Type"].cat.add_categories("None").fillna("None")
        )
    else:
        df["Secondary Type"] = df["Secondary Type"].fillna("None")

    # Sync local images: check cache and download missing pieces in parallel
    logger.info("Starting parallel image sync...")
    with ThreadPoolExecutor(max_workers=20) as executor:
        list(
            executor.map(lambda row: download_image(row[1], images_dir), df.iterrows())
        )
    logger.info("Image sync complete.")

    # Map the localized image paths to a new column for Dash components
    image_dir = Path("assets/images/")
    placeholder_path = "assets/images/placeholder.png"

    def get_image_url(pokemon_id):
        local_path = image_dir / f"{pokemon_id}.png"
        if local_path.exists():
            return str(local_path)

        # Check if the image exists at the official URL (status check was done in download_image)
        # However, download_image already tries to download it. We can use the existence of the
        # local file as the source of truth if we want to be safe.
        return placeholder_path

    df["Image_URL"] = df["#"].apply(get_image_url)

    return df


def download_image(row: pd.Series, images_dir: Path) -> None:
    """Download official artwork for a Pokémon if missing.

    :param row: A pandas Series representing a Pokémon record.
    :type row: pd.Series
    :param images_dir: Directory where images should be saved.
    :type images_dir: Path
    :return: None
    :rtype: None
    """
    image_name = f"{row['#']}.png"
    image_url = f"{OFFICIAL_ARTWORK_URL}{image_name}"
    image_path = images_dir / image_name

    # Only download if we don't already have it cached locally
    if not image_path.exists():
        response = requests.get(image_url)
        if response.status_code == 200:
            with open(image_path, "wb") as f:
                logger.debug(f"Downloading {image_name} for {row['Name']}")
                f.write(response.content)
        else:
            # If download fails, return False so the row can be filtered out
            logger.debug(f"Failed to download {image_name} for {row['Name']}")
    else:
        # Image is already in cache
        logger.debug(f"Image {image_name} already exists for {row['Name']}")


if __name__ == "__main__":
    df = load_and_clean_data()
