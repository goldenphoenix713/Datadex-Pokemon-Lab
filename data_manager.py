import duckdb
import requests  # type: ignore[import-untyped]
from pathlib import Path
from loguru import logger
from diskcache import Cache

# Initialize persistent cache directory
cache_dir = Path(".cache")
cache_dir.mkdir(exist_ok=True)
registry_cache = Cache(str(cache_dir / "registry"))

# Image URL for official artwork
OFFICIAL_ARTWORK_URL = (
    "https://raw.githubusercontent.com/PokeAPI/sprites/"
    + "master/sprites/pokemon/other/official-artwork/"
)
SHINY_ARTWORK_URL = (
    "https://raw.githubusercontent.com/PokeAPI/sprites/"
    + "master/sprites/pokemon/other/official-artwork/shiny/"
)
POKEAPI_SPRITE_URL = (
    "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/"
)

METERS_TO_FEET = 3.28084
KILOGRAMS_TO_POUNDS = 2.20462


def load_and_clean_data(filepath: str = "data/pokemon.parquet"):
    """Load Pokémon data from a parquet file and clean it using DuckDB.

    :param filepath: Path to the parquet data file. Defaults to "data/pokemon.parquet".
    :return: A PyArrow Table with cleaned Pokémon data.
    """
    logger.info(f"Loading Pokémon data from {filepath} using DuckDB...")

    # Regional mapping logic
    region_case = """
        CASE
            WHEN "#" <= 151 THEN 'Kanto'
            WHEN "#" <= 251 THEN 'Johto'
            WHEN "#" <= 386 THEN 'Hoenn'
            WHEN "#" <= 493 THEN 'Sinnoh'
            WHEN "#" <= 649 THEN 'Unova'
            WHEN "#" <= 721 THEN 'Kalos'
            WHEN "#" <= 809 THEN 'Alola'
            WHEN "#" <= 898 THEN 'Galar'
            ELSE 'Paldea'
        END
    """

    # Exclude patterns (Totem, Eternamax, etc.)
    exclude_regex = "(?i)Totem|Eternamax|Pikachu Rock Star|Pikachu Belle|Pikachu Phd|Pikachu Pop Star|Pikachu Libre|Pikachu Cosplay|Pikachu.*Cap"

    # SQL query for comprehensive cleaning and transformation
    query = f"""
    SELECT
        "#" as id,
        "#" as "number",
        CASE
            WHEN "Name" ILIKE '% Mega %' THEN 'Mega ' || regexp_replace("Name", ' (?i)Mega ', ' ')
            WHEN "Name" ILIKE '% Mega' THEN 'Mega ' || regexp_replace("Name", ' (?i)Mega', '')
            WHEN "Name" ILIKE '% Gmax %' THEN 'Gmax ' || regexp_replace("Name", ' (?i)Gmax ', ' ')
            WHEN "Name" ILIKE '% Gmax' THEN 'Gmax ' || regexp_replace("Name", ' (?i)Gmax', '')
            WHEN "Name" ILIKE '% Alola %' THEN 'Alolan ' || regexp_replace("Name", ' (?i)Alola ', ' ')
            WHEN "Name" ILIKE '% Alola' THEN 'Alolan ' || regexp_replace("Name", ' (?i)Alola', '')
            WHEN "Name" ILIKE '% Galar %' THEN 'Galarian ' || regexp_replace("Name", ' (?i)Galar ', ' ')
            WHEN "Name" ILIKE '% Galar' THEN 'Galarian ' || regexp_replace("Name", ' (?i)Galar', '')
            WHEN "Name" ILIKE '% Hisui %' THEN 'Hisuian ' || regexp_replace("Name", ' (?i)Hisui ', ' ')
            WHEN "Name" ILIKE '% Hisui' THEN 'Hisuian ' || regexp_replace("Name", ' (?i)Hisui', '')
            WHEN "Name" ILIKE '% Paldea %' THEN 'Paldean ' || regexp_replace("Name", ' (?i)Paldea ', ' ')
            WHEN "Name" ILIKE '% Paldea' THEN 'Paldean ' || regexp_replace("Name", ' (?i)Paldea', '')
            ELSE "Name"
        END as "Name",
        "Type 1" as "Primary Type",
        COALESCE("Type 2", 'None') as "Secondary Type",
        "HP", "Attack", "Defense",
        "Sp. Atk" as "Special Attack",
        "Sp. Def" as "Special Defense",
        "Speed",
        ROUND("Height" * {METERS_TO_FEET} / 10, 1) as "Height",
        ROUND("Weight" * {KILOGRAMS_TO_POUNDS} / 10, 1) as "Weight",
        "Species_Name",
        "Is_Legendary",
        "Is_Mythical",
        "Is_Final_Evolution",
        {region_case} as "Region",
        "Name" ILIKE '%Gmax%' as "Is_GMax",
        "Name" ILIKE '%Mega%' as "Is_Mega",
        regexp_matches("Name", '(?i)Alola|Galar|Hisui|Paldea') as "Is_Regional",
        "Name" IN ('Nihilego', 'Buzzwole', 'Pheromosa', 'Xurkitree', 'Celesteela', 'Kartana', 'Guzzlord', 'Poipole', 'Naganadel', 'Stakataka', 'Blacephalon') as "Is_Ultra_Beast",
        "Evolution_Chain_URL",
        "Evolution_Chain_Members",
        'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/' || "#" || '.png' as "Sprite_URL",
        'assets/images/' || "#" || '.png' as "Image_URL",
        MIN("#") OVER (PARTITION BY Species_Name) as "National_Dex"
    FROM read_parquet('{filepath}')
    WHERE NOT regexp_matches("Name", '{exclude_regex}')
    """

    try:
        # We use a memory connection to execute the query and return Arrow
        conn = duckdb.connect(":memory:")
        table = conn.execute(query).to_arrow_table()
        logger.debug(
            f"Successfully loaded {table.num_rows} records into PyArrow Table."
        )
        return table
    except Exception as e:
        logger.error(f"Failed to load data with DuckDB: {e}")
        raise


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

        return str(placeholder_path)
    else:
        # Image is already in cache
        logger.debug(f"Image {image_name} already exists for {pokemon_name}")
        return str(image_path)


def ensure_pokemon_sprite(pokemon_id: int, pokemon_name: str = "Unknown") -> str:
    """Check if a Pokémon sprite is cached locally, download it if not.

    :param pokemon_id: The official ID of the Pokémon.
    :type pokemon_id: int
    :param pokemon_name: The name of the Pokémon for logging. Defaults to "Unknown".
    :type pokemon_name: str
    :return: The local path to the sprite, or a pokeball placeholder if download fails.
    :rtype: str
    """
    assets_dir = Path("assets")
    sprites_dir = assets_dir / "sprites"

    # Ensure directories exist
    sprites_dir.mkdir(parents=True, exist_ok=True)

    sprite_name = f"{pokemon_id}.png"
    sprite_url = f"{POKEAPI_SPRITE_URL}{pokemon_id}.png"
    sprite_path = sprites_dir / sprite_name
    placeholder_path = sprites_dir / "pokeball_placeholder.png"

    # Only download if we don't already have it cached locally
    if not sprite_path.exists():
        try:
            logger.info(f"Downloading sprite for {pokemon_name} (ID: {pokemon_id})...")
            response = requests.get(sprite_url, timeout=10)
            if response.status_code == 200:
                with open(sprite_path, "wb") as f:
                    f.write(response.content)
                logger.debug(f"Successfully downloaded sprite: {sprite_name}")
                return str(sprite_path)
            else:
                logger.warning(
                    f"Failed to download sprite {sprite_name} (Status: {response.status_code})"
                )
        except Exception as e:
            logger.error(f"Error downloading sprite {sprite_name}: {e}")

        return str(placeholder_path)
    else:
        # Sprite is already in cache
        logger.debug(f"Sprite {sprite_name} already exists for {pokemon_name}")
        return str(sprite_path)


def has_shiny_artwork(pokemon_id: int) -> bool:
    """Check if a shiny official artwork exists for the given Pokémon ID.

    :param pokemon_id: The official ID of the Pokémon.
    :type pokemon_id: int
    :return: True if shiny artwork exists, False otherwise.
    :rtype: bool
    """
    # 1. Check local cache (filesystem)
    assets_dir = Path("assets")
    images_dir = assets_dir / "images"
    cached_path = images_dir / f"{pokemon_id}_shiny.png"
    if cached_path.exists():
        return True

    # 2. Check persistent registry (cross-process cache)
    cache_key = f"shiny_exists_{pokemon_id}"
    cached_result = registry_cache.get(cache_key)
    if cached_result is not None:
        return bool(cached_result)

    # 3. Perform a quick HEAD request if not in registry
    url = f"{SHINY_ARTWORK_URL}{pokemon_id}.png"
    exists = False
    try:
        response = requests.head(url, timeout=5)
        exists = response.status_code == 200
        # Store in persistent cache
        registry_cache.set(cache_key, exists)
        return exists
    except Exception as e:
        logger.error(f"Error checking shiny existence for {pokemon_id}: {e}")
        return False


if __name__ == "__main__":
    df = load_and_clean_data()
