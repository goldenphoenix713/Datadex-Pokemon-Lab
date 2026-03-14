"""Module for loading, cleaning, and managing Pokémon data and assets."""

from pathlib import Path

import pandas as pd
import requests
from loguru import logger

# Image URL for official artwork
OFFICIAL_ARTWORK_URL = (
    "https://raw.githubusercontent.com/PokeAPI/sprites/"
    + "master/sprites/pokemon/other/official-artwork/"
)
SHINY_ARTWORK_URL = (
    "https://raw.githubusercontent.com/PokeAPI/sprites/"
    + "master/sprites/pokemon/other/official-artwork/shiny/"
)

METERS_TO_FEET = 3.28084
KILOGRAMS_TO_POUNDS = 2.20462


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

    # Remove Totem and Eternamax variants as requested
    # Also remove custom Pikachu variants (Cosplay, Cap, etc.)
    exclude_patterns = [
        "Totem",
        "Eternamax",
        "Pikachu Rock Star",
        "Pikachu Belle",
        "Pikachu Phd",
        "Pikachu Pop Star",
        "Pikachu Libre",
        "Pikachu Cosplay",
        r"Pikachu.*Cap",
    ]

    df = df[
        ~df["Name"].str.contains("|".join(exclude_patterns), case=False, regex=True)
    ]
    logger.debug(f"Filtered out excluded variants. {len(df)} records remaining.")

    # Flag specific forms
    df["Is_GMax"] = df["Name"].str.contains("Gmax", case=False)

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

    # Map the localized image paths to a new column for Dash components
    # These will be the potential paths; the actual download/check happens in callbacks
    def get_image_path(pokemon_id):
        return f"assets/images/{pokemon_id}.png"

    df["Image_URL"] = df["#"].apply(get_image_path)

    # Enhance with Region mapping based on ID
    def determine_region(p_id):
        if p_id <= 151:
            return "Kanto"
        if p_id <= 251:
            return "Johto"
        if p_id <= 386:
            return "Hoenn"
        if p_id <= 493:
            return "Sinnoh"
        if p_id <= 649:
            return "Unova"
        if p_id <= 721:
            return "Kalos"
        if p_id <= 809:
            return "Alola"
        if p_id <= 898:
            return "Galar"
        return "Paldea"

    df["Region"] = df["#"].apply(determine_region)

    # Detect Forms based on Name
    df["Is_Mega"] = df["Name"].str.contains("Mega", case=False)
    df["Is_Regional"] = df["Name"].str.contains("Alola|Galar|Hisui|Paldea", case=False)

    # Add Sprite URL for dropdown icons
    def get_sprite_url(p_id):
        return f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/{p_id}.png"

    df["Sprite_URL"] = df["#"].apply(get_sprite_url)

    # Add National_Dex for grouping alternate forms with base species
    df["National_Dex"] = df.groupby("Species_Name")["#"].transform("min")

    # Convert height from API units (0.1 meters) to feet
    df["Height"] = (df["Height"] * METERS_TO_FEET / 10).round(1)

    # Convert weight from API units (0.1 kg) to pounds
    df["Weight"] = (df["Weight"] * KILOGRAMS_TO_POUNDS / 10).round(1)

    return df


def ensure_pokemon_image(
    pokemon_id: int, pokemon_name: str = "Unknown", shiny: bool = False
) -> str:
    """Check if a Pokémon image is cached locally, download it if not.

    :param pokemon_id: The official ID of the Pokémon.
    :type pokemon_id: int
    :param pokemon_name: The name of the Pokémon for logging. Defaults to "Unknown".
    :type pokemon_name: str
    :param shiny: Whether to fetch the shiny version. Defaults to False.
    :type shiny: bool
    :return: The local path to the image, or a placeholder if download fails.
    :rtype: str
    """
    assets_dir = Path("assets")
    images_dir = assets_dir / "images"

    # Ensure directories exist
    images_dir.mkdir(parents=True, exist_ok=True)

    suffix = "_shiny" if shiny else ""
    image_name = f"{pokemon_id}{suffix}.png"
    base_url = SHINY_ARTWORK_URL if shiny else OFFICIAL_ARTWORK_URL
    image_url = f"{base_url}{pokemon_id}.png"
    image_path = images_dir / image_name
    placeholder_path = "assets/images/placeholder.png"

    # Only download if we don't already have it cached locally
    if not image_path.exists():
        try:
            variant = "shiny " if shiny else ""
            logger.info(
                f"Downloading {variant}image for {pokemon_name} (ID: {pokemon_id})..."
            )
            response = requests.get(image_url, timeout=10)
            if response.status_code == 200:
                with open(image_path, "wb") as f:
                    f.write(response.content)
                logger.debug(f"Successfully downloaded {image_name}")
                return str(image_path)
            else:
                logger.warning(
                    f"Failed to download {image_name} (Status: {response.status_code})"
                )
        except Exception as e:
            logger.error(f"Error downloading {image_name}: {e}")

        return placeholder_path
    else:
        # Image is already in cache
        logger.debug(f"Image {image_name} already exists for {pokemon_name}")
        return str(image_path)


def has_shiny_artwork(pokemon_id: int) -> bool:
    """Check if a shiny official artwork exists for the given Pokémon ID.

    :param pokemon_id: The official ID of the Pokémon.
    :type pokemon_id: int
    :return: True if shiny artwork exists, False otherwise.
    :rtype: bool
    """
    # First check local cache
    assets_dir = Path("assets")
    images_dir = assets_dir / "images"
    cached_path = images_dir / f"{pokemon_id}_shiny.png"
    if cached_path.exists():
        return True

    # If not cached, perform a quick HEAD request to the sprite repository
    url = f"{SHINY_ARTWORK_URL}{pokemon_id}.png"
    try:
        response = requests.head(url, timeout=5)
        return response.status_code == 200
    except Exception as e:
        logger.error(f"Error checking shiny existence for {pokemon_id}: {e}")
        return False


if __name__ == "__main__":
    df = load_and_clean_data()
