import requests  # type: ignore[import]
import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.parquet as pq
from pathlib import Path
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

        # 2. Name formatting logic — pure PyArrow vectorized (no Python loops, no pandas)
        # Strategy: for each variant pattern, detect matching rows, strip the suffix
        # keyword, and prepend the canonical prefix — all in C++ via PyArrow compute.
        names = table["Name"]

        def _normalize_prefix(arr, detect_pat: str, strip_pat: str, prefix: str):
            """Vectorized: rewrite 'Base Suffix' → 'Prefix Base' across an Arrow string column."""
            is_match = pc.match_substring_regex(arr, detect_pat)
            stripped = pc.utf8_trim(
                pc.replace_substring_regex(arr, strip_pat, ""), characters=" "
            )
            prefixed = pc.binary_join_element_wise(pa.scalar(prefix), stripped, "")
            return pc.if_else(is_match, prefixed, arr)

        names = _normalize_prefix(names, r"(?i) mega( |$)", r"(?i) [Mm]ega", "Mega ")
        names = _normalize_prefix(names, r"(?i) gmax( |$)", r"(?i) [Gg]max", "Gmax ")
        names = _normalize_prefix(
            names, r"(?i) alola[n]?( |$)", r"(?i) [Aa]lola[n]?", "Alolan "
        )
        names = _normalize_prefix(
            names, r"(?i) galar(ian)?( |$)", r"(?i) [Gg]alar(ian)?", "Galarian "
        )
        names = _normalize_prefix(
            names, r"(?i) hisui(an)?( |$)", r"(?i) [Hh]isui(an)?", "Hisuian "
        )
        names = _normalize_prefix(
            names, r"(?i) paldea[n]?( |$)", r"(?i) [Pp]aldea[n]?", "Paldean "
        )

        clean_names = names

        # 3. Calculated Columns
        ids = table["#"]

        # Region mapping — vectorized with pc.case_when (no Python loop)
        regions = pc.case_when(
            pc.make_struct(
                pc.less_equal(ids, 151),
                pc.less_equal(ids, 251),
                pc.less_equal(ids, 386),
                pc.less_equal(ids, 493),
                pc.less_equal(ids, 649),
                pc.less_equal(ids, 721),
                pc.less_equal(ids, 809),
                pc.less_equal(ids, 898),
                pc.less_equal(ids, 1025),
            ),
            "Kanto",
            "Johto",
            "Hoenn",
            "Sinnoh",
            "Unova",
            "Kalos",
            "Alola",
            "Galar",
            "Paldea",
            "Unknown",
        )

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

        # Typing string — vectorized with pc.if_else (no Python loop)
        type2 = pc.coalesce(table["Type 2"], pa.scalar("None"))
        has_type2 = pc.not_equal(type2, pa.scalar("None"))
        typings = pc.if_else(
            has_type2,
            pc.binary_join_element_wise(table["Type 1"], type2, "/"),
            table["Type 1"],
        )

        # URLs — vectorized with pc.binary_join_element_wise (no Python loop)
        ids_str = pc.cast(ids, pa.string())
        sprite_urls = pc.binary_join_element_wise(
            pa.scalar(POKEAPI_SPRITE_URL), ids_str, pa.scalar(".png"), ""
        )
        image_urls = pc.binary_join_element_wise(
            pa.scalar("assets/images/"), ids_str, pa.scalar(".png"), ""
        )

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
            # Has_Shiny was added in a later schema version; fall back to False for
            # older Parquet files (until fetch_api_data.py is re-run).
            "Has_Shiny": (
                table["Has_Shiny"]
                if "Has_Shiny" in table.schema.names
                else pa.array([False] * table.num_rows, type=pa.bool_())
            ),
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
    """Download a Pokémon image to the local cache and return the local path.

    .. deprecated::
        Do NOT call this from Dash callbacks. The app now resolves images via
        CDN URLs served directly to the browser (see ``_get_artwork_url`` in
        ``src/callbacks_details.py``). Use ``scripts/prefetch_assets.py`` to
        warm the cache offline before deployment.
    """
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
    """Download a Pokémon mini sprite to the local cache and return the local path.

    .. deprecated::
        Do NOT call this from Dash callbacks. Sprites are served via CDN URLs.
        Use ``scripts/prefetch_assets.py`` to warm the cache offline.
    """
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
    """Download a Pokémon cry audio file to the local cache and return the local path.

    .. deprecated::
        Do NOT call this from Dash callbacks. Cry audio is served via CDN URLs.
        Use ``scripts/prefetch_assets.py`` to warm the cache offline.
    """
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


if __name__ == "__main__":
    pokemon_table = load_and_clean_data()
