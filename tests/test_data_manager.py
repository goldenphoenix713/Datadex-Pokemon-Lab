import pandas as pd
from data_manager import load_and_clean_data


def test_load_and_clean_data(mocker):
    # Mock data
    mock_df = pd.DataFrame(
        {
            "#": [1],
            "Name": ["Bulbasaur"],
            "Type 1": ["Grass"],
            "Type 2": ["Poison"],
            "HP": [45],
            "Attack": [49],
            "Defense": [49],
            "Sp. Atk": [65],
            "Sp. Def": [65],
            "Speed": [45],
            "Height": [7],
            "Weight": [69],
            "Species_Name": ["bulbasaur"],
        }
    )

    # Mock read_parquet
    mocker.patch("pandas.read_parquet", return_value=mock_df)

    df = load_and_clean_data("fake_path.parquet")

    # Check renames
    assert "Special Attack" in df.columns
    assert "Special Defense" in df.columns
    assert "Primary Type" in df.columns
    assert "Secondary Type" in df.columns

    # Check Image_URL generation
    assert "Image_URL" in df.columns
    assert df.loc[0, "Image_URL"] == "assets/images/1.png"


def test_load_and_clean_data_handles_missing_secondary_type(mocker):
    mock_df = pd.DataFrame(
        {
            "#": [1],
            "Name": ["Pikachu"],
            "Type 1": ["Electric"],
            "Type 2": [None],
            "HP": [35],
            "Attack": [55],
            "Defense": [40],
            "Sp. Atk": [50],
            "Sp. Def": [50],
            "Speed": [90],
            "Height": [4],
            "Weight": [60],
            "Species_Name": ["pikachu"],
        }
    )

    mocker.patch("pandas.read_parquet", return_value=mock_df)

    df = load_and_clean_data("fake_path.parquet")

    assert df.loc[0, "Secondary Type"] == "None"


def test_load_and_clean_data_adds_enhanced_fields(mocker):
    mock_df = pd.DataFrame(
        {
            "#": [1, 152, 6, 19],
            "Name": ["Bulbasaur", "Chikorita", "Charizard Mega X", "Rattata Alolan"],
            "Type 1": ["Grass", "Grass", "Fire", "Normal"],
            "Type 2": ["Poison", None, "Dragon", "Dark"],
            "HP": [45, 45, 78, 30],
            "Attack": [49, 49, 130, 56],
            "Defense": [49, 49, 111, 35],
            "Sp. Atk": [65, 49, 130, 25],
            "Sp. Def": [65, 49, 85, 35],
            "Speed": [45, 45, 100, 72],
            "Height": [7, 9, 17, 3],
            "Weight": [69, 64, 905, 35],
            "Species_Name": ["bulbasaur", "chikorita", "charizard", "ratata"],
        }
    )

    mocker.patch("pandas.read_parquet", return_value=mock_df)

    df = load_and_clean_data("fake_path.parquet")

    # Verify Regions
    assert df.loc[0, "Region"] == "Kanto"
    assert df.loc[1, "Region"] == "Johto"

    # Verify Form Detection
    assert df.loc[2, "Is_Mega"]
    assert not df.loc[0, "Is_Mega"]
    assert df.loc[3, "Is_Regional"]
    assert not df.loc[0, "Is_Regional"]

    # Verify Sprite URLs
    assert (
        df.loc[0, "Sprite_URL"]
        == "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/1.png"
    )


def test_has_shiny_artwork(mocker):
    # Mock requests.head
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mocker.patch("requests.head", return_value=mock_response)

    from data_manager import has_shiny_artwork

    assert has_shiny_artwork(1) is True

    mock_response.status_code = 404
    assert has_shiny_artwork(9999) is False


def test_ensure_pokemon_image_shiny(mocker, tmp_path):
    # Mock assets and images dir
    mocker.patch("data_manager.Path.mkdir")
    mocker.patch("data_manager.Path.exists", return_value=False)

    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.content = b"fake_shiny_image"
    mocker.patch("requests.get", return_value=mock_response)

    # Use a real file for the 'with open' part if needed, or mock open
    mocker.patch("builtins.open", mocker.mock_open())

    from data_manager import ensure_pokemon_image

    path = ensure_pokemon_image(1, "Bulbasaur", shiny=True)
    assert "1_shiny.png" in path


def test_load_and_clean_data_failure(mocker):
    # Mock read_parquet to raise an exception
    mocker.patch("pandas.read_parquet", side_effect=Exception("Parquet Error"))
    import pytest

    with pytest.raises(Exception, match="Parquet Error"):
        load_and_clean_data("any_path.parquet")


def test_ensure_pokemon_image_cache_hit(mocker):
    # Mock Path.exists to return True for the image
    mocker.patch("data_manager.Path.exists", return_value=True)
    from data_manager import ensure_pokemon_image

    path = ensure_pokemon_image(1, "Bulbasaur")
    assert "1.png" in path
    assert "placeholder" not in path


def test_ensure_pokemon_image_download_failure(mocker):
    # Mock Path.exists to False (not in cache)
    # Mock requests.get to return non-200
    mocker.patch("data_manager.Path.exists", return_value=False)
    mocker.patch("data_manager.Path.mkdir")
    mock_resp = mocker.Mock()
    mock_resp.status_code = 404
    mocker.patch("requests.get", return_value=mock_resp)

    from data_manager import ensure_pokemon_image

    path = ensure_pokemon_image(1, "Bulbasaur")
    assert "placeholder.png" in path


def test_has_shiny_artwork_exception(mocker):
    # Mock Path.exists to False
    # Mock requests.head to raise an exception
    mocker.patch("data_manager.Path.exists", return_value=False)
    mocker.patch("requests.head", side_effect=Exception("Network Error"))

    from data_manager import has_shiny_artwork

    assert has_shiny_artwork(1) is False


def test_has_shiny_artwork_cache_hit(mocker):
    # Mock Path.exists to return True (closes data_manager.py line 175)
    mocker.patch("data_manager.Path.exists", return_value=True)
    from data_manager import has_shiny_artwork

    assert has_shiny_artwork(1) is True
