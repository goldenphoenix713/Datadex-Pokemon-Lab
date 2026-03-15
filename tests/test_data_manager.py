from data_manager import load_and_clean_data


def test_load_and_clean_data(mocker):
    # Mock PyArrow Table
    import pyarrow as pa

    mock_table = pa.table(
        {
            "number": [1],
            "Name": ["Bulbasaur"],
            "Primary Type": ["Grass"],
            "Secondary Type": ["Poison"],
            "HP": [45],
            "Attack": [49],
            "Defense": [49],
            "Special Attack": [65],
            "Special Defense": [65],
            "Speed": [45],
            "Height": [7.0],
            "Weight": [69.0],
            "Species_Name": ["bulbasaur"],
            "Image_URL": ["assets/images/1.png"],
        }
    )

    # Mock duckdb.connect().execute().to_arrow_table()
    mock_conn = mocker.Mock()
    mocker.patch("duckdb.connect", return_value=mock_conn)
    mock_conn.execute.return_value.to_arrow_table.return_value = mock_table

    df = load_and_clean_data("fake_path.parquet")

    # Check renames (now columns in pa.Table)
    assert "Special Attack" in df.column_names
    assert "Special Defense" in df.column_names
    assert "Primary Type" in df.column_names
    assert "Secondary Type" in df.column_names

    # Check Image_URL generation
    assert "Image_URL" in df.column_names
    assert df.to_pylist()[0]["Image_URL"] == "assets/images/1.png"


def test_load_and_clean_data_handles_missing_secondary_type(mocker):
    import pyarrow as pa

    mock_table = pa.table(
        {
            "Name": ["Pikachu"],
            "Secondary Type": ["None"],
        }
    )

    mock_conn = mocker.Mock()
    mocker.patch("duckdb.connect", return_value=mock_conn)
    mock_conn.execute.return_value.to_arrow_table.return_value = mock_table

    df = load_and_clean_data("fake_path.parquet")

    assert df.to_pylist()[0]["Secondary Type"] == "None"


def test_load_and_clean_data_adds_enhanced_fields(mocker):
    import pyarrow as pa

    mock_table = pa.table(
        {
            "Name": ["Bulbasaur", "Chikorita", "Charizard Mega X", "Rattata Alolan"],
            "Region": ["Kanto", "Johto", "Kanto", "Kanto"],
            "Is_Mega": [False, False, True, False],
            "Is_Regional": [False, False, False, True],
            "Sprite_URL": [
                "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/1.png",
                "url",
                "url",
                "url",
            ],
        }
    )

    mock_conn = mocker.Mock()
    mocker.patch("duckdb.connect", return_value=mock_conn)
    mock_conn.execute.return_value.to_arrow_table.return_value = mock_table

    df = load_and_clean_data("fake_path.parquet")

    data = df.to_pylist()
    # Verify Regions
    assert data[0]["Region"] == "Kanto"
    assert data[1]["Region"] == "Johto"

    # Verify Form Detection
    assert data[2]["Is_Mega"]
    assert not data[0]["Is_Mega"]
    assert data[3]["Is_Regional"]
    assert not data[0]["Is_Regional"]

    # Verify Sprite URLs
    assert (
        data[0]["Sprite_URL"]
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
    # Mock duckdb.connect to raise an exception
    mocker.patch("duckdb.connect", side_effect=Exception("DuckDB Error"))
    import pytest

    with pytest.raises(Exception, match="DuckDB Error"):
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
