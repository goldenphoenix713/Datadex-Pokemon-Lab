from unittest.mock import MagicMock

import requests

from fetch_api_data import fetch_single_pokemon


def test_fetch_single_pokemon_success(mocker):
    # Mock response from requests.get
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "id": 1,
        "name": "bulbasaur",
        "types": [{"type": {"name": "grass"}}, {"type": {"name": "poison"}}],
        "stats": [
            {"base_stat": 45, "stat": {"name": "hp"}},
            {"base_stat": 49, "stat": {"name": "attack"}},
            {"base_stat": 49, "stat": {"name": "defense"}},
            {"base_stat": 65, "stat": {"name": "special-attack"}},
            {"base_stat": 65, "stat": {"name": "special-defense"}},
            {"base_stat": 45, "stat": {"name": "speed"}},
        ],
        "height": 7,
        "weight": 69,
    }

    mocker.patch("requests.get", return_value=mock_response)

    result = fetch_single_pokemon("https://pokeapi.co/api/v2/pokemon/1")

    assert result["#"] == 1
    assert result["Name"] == "Bulbasaur"
    assert result["Type 1"] == "Grass"
    assert result["Type 2"] == "Poison"
    assert result["HP"] == 45
    assert result["Sp. Atk"] == 65


def test_fetch_single_pokemon_failure(mocker):
    mocker.patch(
        "requests.get",
        side_effect=requests.exceptions.RequestException("Connection error"),
    )

    result = fetch_single_pokemon("https://pokeapi.co/api/v2/pokemon/invalid")

    assert result is None
