"""Module for loading, cleaning, and managing Pokémon data and assets."""

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pandas as pd
import requests

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
    # Load the raw data from Parquet
    df = pd.read_parquet(filepath, engine="pyarrow")

    # Ensure the assets and images directories exist for local storage
    assets_dir = Path("assets")
    if not assets_dir.exists():
        assets_dir.mkdir()

    images_dir = assets_dir / "images"
    if not images_dir.exists():
        images_dir.mkdir()

    # Rename stats to more readable full names for the UI
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
    with ThreadPoolExecutor(max_workers=20) as executor:
        image_available = list(
            executor.map(lambda row: download_image(row[1], images_dir), df.iterrows())
        )

    # Filter out any rows where the image is completely missing/undownloadable
    df = df[image_available]

    # Map the localized image paths to a new column for Dash components
    image_dir = Path("assets/images/")
    df["Image_URL"] = df["#"].apply(
        lambda x: (
            str(image_path)
            if (image_path := image_dir / f"{x}.png").exists()
            else f"{OFFICIAL_ARTWORK_URL}/{x}.png"
        )
    )

    return df


def download_image(row: pd.Series, images_dir: Path) -> bool:
    """Download official artwork for a Pokémon if missing.

    :param row: A pandas Series representing a Pokémon record.
    :type row: pd.Series
    :param images_dir: Directory where images should be saved.
    :type images_dir: Path
    :return: True if the image is available locally (already present or successfully
        downloaded), False otherwise.
    :rtype: bool
    """
    image_name = f"{row['#']}.png"
    image_url = f"{OFFICIAL_ARTWORK_URL}{image_name}"
    image_path = images_dir / image_name

    # Only download if we don't already have it cached locally
    if not image_path.exists():
        response = requests.get(image_url)
        if response.status_code == 200:
            with open(image_path, "wb") as f:
                print(f"Downloading {image_name} for {row['Name']}")
                f.write(response.content)
            return True
        else:
            # If download fails, return False so the row can be filtered out
            print(f"Failed to download {image_name} for {row['Name']}")
            return False
    else:
        # Image is already in cache
        print(f"Image {image_name} already exists for {row['Name']}")
        return True


if __name__ == "__main__":
    df = load_and_clean_data()
