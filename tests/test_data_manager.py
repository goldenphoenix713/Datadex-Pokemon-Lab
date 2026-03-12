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
    assert (
        df.loc[0, "Image_URL"]
        == "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/1.png"
    )


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
        }
    )

    mocker.patch("pandas.read_parquet", return_value=mock_df)

    df = load_and_clean_data("fake_path.parquet")

    assert df.loc[0, "Secondary Type"] == "None"
