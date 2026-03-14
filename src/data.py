"""Data management and preparation for the Data-Dex application."""

from data_manager import load_and_clean_data

# Load and prepare data on startup
df = load_and_clean_data()
pokemon_names = sorted(df["Name"].unique())

# Preparation for themed dropdowns with sprites
pokemon_sprites = df.set_index("Name")["Sprite_URL"].to_dict()
