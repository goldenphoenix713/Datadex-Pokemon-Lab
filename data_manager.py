import pandas as pd  # type: ignore[import-untyped]


def load_and_clean_data(filepath="data/pokemon.parquet"):
    df = pd.read_parquet(filepath, engine="pyarrow")

    # Rename stats to full names for better display
    rename_map = {
        "Sp. Atk": "Special Attack",
        "Sp. Def": "Special Defense",
        "Type 1": "Primary Type",
        "Type 2": "Secondary Type",
    }
    df = df.rename(columns=rename_map)
    if "Secondary Type" in df.columns and hasattr(df["Secondary Type"], "cat"):
        df["Secondary Type"] = (
            df["Secondary Type"].cat.add_categories("None").fillna("None")
        )
    else:
        df["Secondary Type"] = df["Secondary Type"].fillna("None")

    # Image URL generation for official artwork
    # Note: PokéAPI uses the base species ID for artwork.
    # For variety forms (IDs > 10000), we might need logic to find the base ID,
    # but for now we'll use the ID from the parquet which works for most.
    df["Image_URL"] = df["#"].apply(
        lambda x: (
            f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/{x}.png"
        )
    )

    return df
