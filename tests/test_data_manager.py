from data_manager import load_and_clean_data


def test_load_and_clean_data(mocker):
    # Mock PyArrow Table
    import pyarrow as pa

    mock_table = pa.table(
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
            "Height": [7.0],
            "Weight": [69.0],
            "Species_Name": ["bulbasaur"],
            "Is_Legendary": [False],
            "Is_Mythical": [False],
            "Is_Final_Evolution": [False],
            "Evolution_Chain_URL": ["url"],
            "Evolution_Chain_Members": ["bulbasaur,ivysaur,venusaur"],
        }
    )

    # Mock pyarrow.parquet.read_table
    mocker.patch("pyarrow.parquet.read_table", return_value=mock_table)

    pokemon_table = load_and_clean_data("fake_path.parquet")

    # Check columns
    assert "Special Attack" in pokemon_table.column_names
    assert "Primary Type" in pokemon_table.column_names
    assert "Image_URL" in pokemon_table.column_names
    assert pokemon_table.to_pylist()[0]["Image_URL"] == "assets/images/1.png"


def test_load_and_clean_data_handles_missing_secondary_type(mocker):
    import pyarrow as pa

    mock_table = pa.table(
        {
            "#": [25],
            "Name": ["Pikachu"],
            "Type 1": ["Electric"],
            "Type 2": pa.array([None], type=pa.string()),
            "HP": [35],
            "Attack": [55],
            "Defense": [40],
            "Sp. Atk": [50],
            "Sp. Def": [50],
            "Speed": [90],
            "Height": [4.0],
            "Weight": [60.0],
            "Species_Name": ["pikachu"],
            "Is_Legendary": [False],
            "Is_Mythical": [False],
            "Is_Final_Evolution": [False],
            "Evolution_Chain_URL": ["url"],
            "Evolution_Chain_Members": ["pichu,pikachu,raichu"],
        }
    )

    mocker.patch("pyarrow.parquet.read_table", return_value=mock_table)

    pokemon_table = load_and_clean_data("fake_path.parquet")

    assert pokemon_table.to_pylist()[0]["Secondary Type"] == "None"


def test_load_and_clean_data_adds_enhanced_fields(mocker):
    import pyarrow as pa

    mock_table = pa.table(
        {
            "#": [1, 152, 6, 19],
            "Name": ["Bulbasaur", "Chikorita", "Charizard Mega X", "Rattata Alolan"],
            "Type 1": ["Grass", "Grass", "Fire", "Normal"],
            "Type 2": ["Poison", "None", "Dragon", "Dark"],
            "HP": [45, 45, 78, 30],
            "Attack": [49, 49, 130, 56],
            "Defense": [49, 65, 111, 35],
            "Sp. Atk": [65, 49, 130, 25],
            "Sp. Def": [65, 65, 85, 35],
            "Speed": [45, 45, 100, 72],
            "Height": [7.0, 9.0, 17.0, 3.0],
            "Weight": [69.0, 64.0, 110.5, 38.0],
            "Species_Name": ["bulbasaur", "chikorita", "charizard", "rattata"],
            "Is_Legendary": [False, False, False, False],
            "Is_Mythical": [False, False, False, False],
            "Is_Final_Evolution": [False, False, False, False],
            "Evolution_Chain_URL": ["url", "url", "url", "url"],
            "Evolution_Chain_Members": ["b,i,v", "c,b,m", "c,c,c", "r,r"],
        }
    )

    mocker.patch("pyarrow.parquet.read_table", return_value=mock_table)

    pokemon_table = load_and_clean_data("fake_path.parquet")

    data = pokemon_table.to_pylist()
    assert data[0]["Region"] == "Kanto"
    assert data[1]["Region"] == "Johto"
    assert data[2]["Is_Mega"]
    assert data[3]["Is_Regional"]


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
    # Mock read_table to raise an exception
    mocker.patch("pyarrow.parquet.read_table", side_effect=Exception("Read Error"))
    import pytest

    with pytest.raises(Exception, match="Read Error"):
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
    # Mock registry_cache.get to return None so it proceeds to the network call
    mocker.patch("data_manager.registry_cache.get", return_value=None)
    mocker.patch("requests.head", side_effect=Exception("Network Error"))

    from data_manager import has_shiny_artwork

    assert has_shiny_artwork(1) is False


def test_has_shiny_artwork_cache_hit(mocker):
    # Mock Path.exists to return True (closes data_manager.py line 175)
    mocker.patch("data_manager.Path.exists", return_value=True)
    from data_manager import has_shiny_artwork

    assert has_shiny_artwork(1) is True


def test_ensure_pokemon_sprite_cache_hit(mocker):
    # Mock Path.exists to return True for the sprite
    mocker.patch("data_manager.Path.exists", return_value=True)
    from data_manager import ensure_pokemon_sprite

    path = ensure_pokemon_sprite(1, "Bulbasaur")
    assert "1.png" in path
    assert "sprites" in path
    assert "pokeball_placeholder" not in path


def test_ensure_pokemon_sprite_download_success(mocker):
    # Mock Path.exists to False (not in cache)
    mocker.patch("data_manager.Path.exists", return_value=False)
    mocker.patch("data_manager.Path.mkdir")

    mock_resp = mocker.Mock()
    mock_resp.status_code = 200
    mock_resp.content = b"fake_sprite_content"
    mocker.patch("requests.get", return_value=mock_resp)

    mocker.patch("builtins.open", mocker.mock_open())

    from data_manager import ensure_pokemon_sprite

    path = ensure_pokemon_sprite(1, "Bulbasaur")
    assert "1.png" in path
    assert "sprites" in path


def test_ensure_pokemon_sprite_download_failure(mocker):
    # Mock Path.exists to False
    mocker.patch("data_manager.Path.exists", return_value=False)
    mocker.patch("data_manager.Path.mkdir")

    mock_resp = mocker.Mock()
    mock_resp.status_code = 404
    mocker.patch("requests.get", return_value=mock_resp)

    from data_manager import ensure_pokemon_sprite

    path = ensure_pokemon_sprite(1, "Bulbasaur")
    assert "pokeball_placeholder.png" in path


def test_ensure_pokemon_cry_download_success(mocker):
    # Mock Path.exists to False (not in cache)
    mocker.patch("data_manager.Path.exists", return_value=False)
    mocker.patch("data_manager.Path.mkdir")

    mock_resp = mocker.Mock()
    mock_resp.status_code = 200
    mock_resp.content = b"fake_cry_content"
    mocker.patch("requests.get", return_value=mock_resp)

    mocker.patch("builtins.open", mocker.mock_open())

    from data_manager import ensure_pokemon_cry

    path = ensure_pokemon_cry(1, "Bulbasaur")
    assert "1.ogg" in path
    assert "sounds" in path


def test_ensure_pokemon_cry_cache_hit(mocker):
    # Mock Path.exists to return True for the cry
    mocker.patch("data_manager.Path.exists", return_value=True)
    from data_manager import ensure_pokemon_cry

    path = ensure_pokemon_cry(1, "Bulbasaur")
    assert "1.ogg" in path
    assert "sounds" in path
