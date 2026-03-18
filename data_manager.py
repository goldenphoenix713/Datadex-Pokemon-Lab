import requests  # type: ignore[import]
import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.parquet as pq
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
POKEAPI_CRY_URL = (
    "https://raw.githubusercontent.com/PokeAPI/cries/main/cries/pokemon/latest/"
)

METERS_TO_FEET = 3.28084
KILOGRAMS_TO_POUNDS = 2.20462


def load_and_clean_data(filepath: str = "data/pokemon.parquet"):
    """Load Pokémon data from a parquet file and clean it using PyArrow.

    :param filepath: Path to the parquet data file. Defaults to "data/pokemon.parquet".
    :return: A PyArrow Table with cleaned Pokémon data.
    """
    logger.info(f"Loading Pokémon data from {filepath} using PyArrow...")

    try:
        table = pq.read_table(filepath)

        # 1. Row filtering
        exclude_regex = "(?i)Totem|Eternamax|Pikachu Rock Star|Pikachu Belle|Pikachu Phd|Pikachu Pop Star|Pikachu Libre|Pikachu Cosplay|Pikachu.*Cap"
        mask = pc.invert(pc.match_substring_regex(table["Name"], exclude_regex))
        table = table.filter(mask)

        # 2. Name formatting logic
        names = table["Name"]

        # Helper to apply regex replacement patterns
        def apply_name_rules(arr):
            # Mega
            arr = pc.replace_substring_regex(arr, "(?i) (Mega) ", " Mega ")
            arr = pc.replace_substring_regex(arr, " Mega ", " Mega ")
            # In the SQL, it was 'Mega ' || regexp_replace("Name", ' (?i)Mega ', ' ')
            # We can do this more simply by just normalizing the strings if the pattern matches

            # Simple approach: Replicate the CASE WHEN logic
            # This is complex in PyArrow, so let's use a series of replacements or a map
            # Actually, standardizing labels (Mega, Gmax, Alolan...)
            new_names = []
            for n in arr.to_pylist():
                low_n = n.lower()
                if " mega " in low_n or n.endswith(" Mega"):
                    n = "Mega " + n.replace(" Mega", "").replace(" mega", "").strip()
                elif " gmax " in low_n or n.endswith(" Gmax"):
                    n = "Gmax " + n.replace(" Gmax", "").replace(" gmax", "").strip()
                elif " alola " in low_n or n.endswith(" Alola"):
                    n = (
                        "Alolan "
                        + n.replace(" Alola", "").replace(" alola", "").strip()
                    )
                elif " galar " in low_n or n.endswith(" Galar"):
                    n = (
                        "Galarian "
                        + n.replace(" Galar", "").replace(" galar", "").strip()
                    )
                elif " hisui " in low_n or n.endswith(" Hisui"):
                    n = (
                        "Hisuian "
                        + n.replace(" Hisui", "").replace(" hisui", "").strip()
                    )
                elif " paldea " in low_n or n.endswith(" Paldea"):
                    n = (
                        "Paldean "
                        + n.replace(" Paldea", "").replace(" paldea", "").strip()
                    )
                new_names.append(n)
            return pa.array(new_names)

        clean_names = apply_name_rules(names)

        # 3. Calculated Columns
        ids = table["#"]

        # Region Case
        def get_region(id_val):
            if id_val <= 151:
                region = "Kanto"
            elif id_val <= 251:
                region = "Johto"
            elif id_val <= 386:
                region = "Hoenn"
            elif id_val <= 493:
                region = "Sinnoh"
            elif id_val <= 649:
                region = "Unova"
            elif id_val <= 721:
                region = "Kalos"
            elif id_val <= 809:
                region = "Alola"
            elif id_val <= 898:
                region = "Galar"
            elif id_val <= 1025:
                region = "Paldea"
            else:
                region = "Unknown"
            return region

        regions = pa.array([get_region(i) for i in ids.to_pylist()])

        # Boolean Flags
        is_gmax = pc.match_substring_regex(table["Name"], "(?i)Gmax")
        is_mega = pc.match_substring_regex(table["Name"], "(?i)Mega")
        is_regional = pc.match_substring_regex(
            table["Name"], "(?i)Alola|Galar|Hisui|Paldea"
        )

        ub_list = [
            "Nihilego",
            "Buzzwole",
            "Pheromosa",
            "Xurkitree",
            "Celesteela",
            "Kartana",
            "Guzzlord",
            "Poipole",
            "Naganadel",
            "Stakataka",
            "Blacephalon",
        ]
        is_ub = pc.is_in(table["Name"], value_set=pa.array(ub_list))

        # Typing string
        type2 = pc.coalesce(table["Type 2"], pa.scalar("None"))

        def get_typing(t1, t2):
            if t2 == "None" or t2 is None:
                return t1
            return f"{t1}/{t2}"

        typings = pa.array(
            [
                get_typing(r[0], r[1])
                for r in zip(table["Type 1"].to_pylist(), type2.to_pylist())
            ]
        )

        # URLs
        sprite_urls = pa.array(
            [f"{POKEAPI_SPRITE_URL}{i}.png" for i in ids.to_pylist()]
        )
        image_urls = pa.array([f"assets/images/{i}.png" for i in ids.to_pylist()])

        # 4. National Dex (Window function MIN(#) PARTITION BY Species_Name)
        # Group by species and find min ID
        dex_map = table.group_by("Species_Name").aggregate([("#", "min")])
        # Join back to main table
        table = table.join(dex_map, keys="Species_Name")
        national_dex = table["#_min"]

        # 5. Build Final Table
        final_columns = {
            "id": ids,
            "number": ids,
            "Name": clean_names,
            "Primary Type": table["Type 1"],
            "Secondary Type": type2,
            "HP": table["HP"],
            "Attack": table["Attack"],
            "Defense": table["Defense"],
            "Special Attack": table["Sp. Atk"],
            "Special Defense": table["Sp. Def"],
            "Speed": table["Speed"],
            "Height": pc.round(
                pc.divide(pc.multiply(table["Height"], METERS_TO_FEET), 10), 1
            ),
            "Weight": pc.round(
                pc.divide(pc.multiply(table["Weight"], KILOGRAMS_TO_POUNDS), 10), 1
            ),
            "Species_Name": table["Species_Name"],
            "Is_Legendary": table["Is_Legendary"],
            "Is_Mythical": table["Is_Mythical"],
            "Is_Final_Evolution": table["Is_Final_Evolution"],
            "Region": regions,
            "Is_GMax": is_gmax,
            "Is_Mega": is_mega,
            "Is_Regional": is_regional,
            "Is_Ultra_Beast": is_ub,
            "Evolution_Chain_URL": table["Evolution_Chain_URL"],
            "Evolution_Chain_Members": table["Evolution_Chain_Members"],
            "Sprite_URL": sprite_urls,
            "Image_URL": image_urls,
            "Typing": typings,
            "National_Dex": national_dex,
        }

        result_table = pa.table(final_columns)
        logger.debug(
            f"Successfully loaded {result_table.num_rows} records into PyArrow Table."
        )
        return result_table

    except Exception as e:
        logger.error(f"Failed to load data with PyArrow: {e}")
        raise


def ensure_pokemon_image(
    pokemon_id: int, pokemon_name: str = "Unknown", shiny: bool = False
) -> str:
    """Check if a Pokémon image is cached locally, download it if not."""
    assets_dir = Path("assets")
    images_dir = assets_dir / "images"
    images_dir.mkdir(parents=True, exist_ok=True)

    suffix = "_shiny" if shiny else ""
    image_name = f"{pokemon_id}{suffix}.png"
    base_url = SHINY_ARTWORK_URL if shiny else OFFICIAL_ARTWORK_URL
    image_url = f"{base_url}{pokemon_id}.png"
    image_path = images_dir / image_name
    placeholder_path = "assets/images/placeholder.png"

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
        logger.debug(f"Image {image_name} already exists for {pokemon_name}")
        return str(image_path)


def ensure_pokemon_sprite(pokemon_id: int, pokemon_name: str = "Unknown") -> str:
    """Check if a Pokémon sprite is cached locally, download it if not."""
    assets_dir = Path("assets")
    sprites_dir = assets_dir / "sprites"
    sprites_dir.mkdir(parents=True, exist_ok=True)

    sprite_name = f"{pokemon_id}.png"
    sprite_url = f"{POKEAPI_SPRITE_URL}{pokemon_id}.png"
    sprite_path = sprites_dir / sprite_name
    placeholder_path = sprites_dir / "pokeball_placeholder.png"

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
        logger.debug(f"Sprite {sprite_name} already exists for {pokemon_name}")
        return str(sprite_path)


def ensure_pokemon_cry(pokemon_id: int, pokemon_name: str = "Unknown") -> str:
    """Check if a Pokémon cry is cached locally, download it if not."""
    assets_dir = Path("assets")
    sounds_dir = assets_dir / "sounds"
    sounds_dir.mkdir(parents=True, exist_ok=True)

    cry_name = f"{pokemon_id}.ogg"
    cry_url = f"{POKEAPI_CRY_URL}{pokemon_id}.ogg"
    cry_path = sounds_dir / cry_name

    if not cry_path.exists():
        try:
            logger.info(f"Downloading cry for {pokemon_name} (ID: {pokemon_id})...")
            response = requests.get(cry_url, timeout=10)
            if response.status_code == 200:
                with open(cry_path, "wb") as f:
                    f.write(response.content)
                logger.debug(f"Successfully downloaded cry: {cry_name}")
                return str(cry_path)
            else:
                logger.warning(
                    f"Failed to download cry {cry_name} (Status: {response.status_code})"
                )
        except Exception as e:
            logger.error(f"Error downloading cry {cry_name}: {e}")
        return ""
    else:
        logger.debug(f"Cry {cry_name} already exists for {pokemon_name}")
        return str(cry_path)


def has_shiny_artwork(pokemon_id: int) -> bool:
    """Check if a shiny official artwork exists for the given Pokémon ID."""
    assets_dir = Path("assets")
    images_dir = assets_dir / "images"
    cached_path = images_dir / f"{pokemon_id}_shiny.png"
    if cached_path.exists():
        return True

    cache_key = f"shiny_exists_{pokemon_id}"
    cached_result = registry_cache.get(cache_key)
    if cached_result is not None:
        return bool(cached_result)

    url = f"{SHINY_ARTWORK_URL}{pokemon_id}.png"
    try:
        response = requests.head(url, timeout=5)
        exists = response.status_code == 200
        registry_cache.set(cache_key, exists)
        return exists
    except Exception as e:
        logger.error(f"Error checking shiny existence for {pokemon_id}: {e}")
        return False


if __name__ == "__main__":
    pokemon_table = load_and_clean_data()
