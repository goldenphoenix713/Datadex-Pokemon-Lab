import sys
from pathlib import Path

import pytest
import os
from webdriver_manager.chrome import ChromeDriverManager
import pyarrow as pa

# Add project root to sys.path for test discovery
root_dir = str(Path(__file__).parent.parent)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)


@pytest.fixture
def sample_pokemon_table():
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
    return pa.table(data)


def pytest_configure(config):
    """Ensure chromedriver is in PATH for dash.testing."""
    driver_path = ChromeDriverManager().install()
    # On some systems ChromeDriverManager returns path to exe, on others to dir
    driver_dir = os.path.dirname(driver_path)
    os.environ["PATH"] = driver_dir + os.path.pathsep + os.environ["PATH"]
