from pathlib import Path
from typing import Any

import requests
import pandas as pd


def load_and_clean_data(filepath="data/pokemon.parquet") -> pd.DataFrame:
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
    url = (
        "https://raw.githubusercontent.com/PokeAPI/sprites/"
        + "master/sprites/pokemon/other/official-artwork/"
    )
    # TODO: Add logic to find base ID for variety forms
    image_dir = Path("assets/images/")
    df["Image_URL"] = df["#"].apply(
        lambda x: (
            str(image_path)
            if (image_path := image_dir / f"{x}.png").exists()
            else f"{url}/{x}.png"
        )
    )

    return df


def download_image(row: Any):
    image_url = row.Image_URL
    image_name = f"{row._1}.png"
    image_path = images_dir / image_name
    if not image_path.exists():
        response = requests.get(image_url)
        if response.status_code == 200:
            with open(image_path, "wb") as f:
                print(f"Downloading {image_name}")
                f.write(response.content)
    else:
        print(f"Image {image_name} already exists")


if __name__ == "__main__":
    from concurrent.futures import ThreadPoolExecutor

    df = load_and_clean_data()

    assets_dir = Path("assets")
    if not assets_dir.exists():
        assets_dir.mkdir()

    images_dir = assets_dir / "images"
    if not images_dir.exists():
        images_dir.mkdir()

    with ThreadPoolExecutor(max_workers=20) as executor:
        list(executor.map(download_image, df.itertuples()))

    df["Image_URL"] = df["#"].apply(lambda x: f"assets/images/{x}.png")
    df.to_parquet("data/pokemon.parquet", engine="pyarrow", compression="zstd")
