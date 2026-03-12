import pytest
import pandas as pd


@pytest.fixture
def sample_pokemon_df():
    data = {
        "#": [1, 4, 7],
        "Name": ["Bulbasaur", "Charmander", "Squirtle"],
        "Primary Type": ["Grass", "Fire", "Water"],
        "Secondary Type": ["Poison", "None", "None"],
        "HP": [45, 39, 44],
        "Attack": [49, 52, 48],
        "Defense": [49, 43, 65],
        "Special Attack": [65, 60, 50],
        "Special Defense": [65, 50, 64],
        "Speed": [45, 65, 43],
        "Height": [7, 6, 5],
        "Weight": [69, 85, 90],
        "Image_URL": [
            "https://example.com/1.png",
            "https://example.com/4.png",
            "https://example.com/7.png",
        ],
    }
    return pd.DataFrame(data)
