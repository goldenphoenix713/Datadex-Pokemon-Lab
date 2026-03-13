from unittest.mock import MagicMock

import requests

from fetch_api_data import fetch_single_pokemon


def test_fetch_single_pokemon_success(mocker):
    # Mock response from requests.get for both pokemon and species
    mock_pokemon_data = {
        "id": 1,
        "name": "bulbasaur",
        "species": {"name": "bulbasaur", "url": "https://url/species/1"},
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

    mock_species_data = {
        "is_legendary": False,
        "is_mythical": False,
        "evolution_chain": {"url": "https://url/evo/1"},
    }

    # Use a side effect to handle different URLs
    def get_side_effect(url, **kwargs):
        resp = MagicMock()
        resp.status_code = 200
        if "pokemon" in url:
            resp.json.return_value = mock_pokemon_data
        else:
            resp.json.return_value = mock_species_data
        return resp

    mocker.patch("requests.get", side_effect=get_side_effect)

    result = fetch_single_pokemon("https://pokeapi.co/api/v2/pokemon/1")

    assert result["#"] == 1
    assert result["Name"] == "Bulbasaur"
    assert result["Is_Legendary"] is False


def test_fetch_single_pokemon_failure(mocker):
    mocker.patch(
        "requests.get",
        side_effect=requests.exceptions.RequestException("Connection error"),
    )

    result = fetch_single_pokemon("https://pokeapi.co/api/v2/pokemon/invalid")

    assert result is None
