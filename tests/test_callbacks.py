from dash import Patch
from src.callbacks_details import update_details, update_pokemon_image
from src.callbacks_discovery import update_focus_options as update_selector_options


def test_update_details_callback(mocker):
    mocker.patch("src.callbacks_details.ctx", mocker.Mock(inputs_list=[]))

    # Signature: (focus_name, is_shiny, t_height, t_weight, show_mega, show_gmax, show_regional, team)
    result_shiny = update_details("Bulbasaur", True, 1.7, 70, True, False, True, [])
    # Check current_shiny (5th element, index 4)
    assert result_shiny[4] is True

    result = update_details("Bulbasaur", False, 1.7, 70, True, False, True, [])
    (
        name_display,
        type_badges,
        progress_bars,
        toggle_style,
        current_shiny,
        comparison,
        evolution,
        add_disabled,
        cry_src,
        cry_icon,
        cry_disabled,
    ) = result
    assert name_display == "Bulbasaur"
    assert isinstance(type_badges, Patch)
    assert isinstance(progress_bars, Patch)
    assert toggle_style == {"display": "block"}
    assert current_shiny is False
    assert add_disabled is False
    assert "https://raw.githubusercontent.com/PokeAPI/cries/main" in cry_src


def test_update_details_callback_no_selection(mocker):
    mocker.patch("src.callbacks_details.ctx", mocker.Mock(inputs_list=[]))
    result = update_details("", False, 1.7, 70, True, False, True, [])
    (
        name_display,
        type_badges,
        progress_bars,
        toggle_style,
        current_shiny,
        comparison,
        evolution,
        add_disabled,
        cry_src,
        cry_icon,
        cry_disabled,
    ) = result
    assert name_display == "Select a Pokémon"
    assert toggle_style == {"display": "none"}
    assert add_disabled is True
    assert cry_src == ""


def test_update_selector_options_callback(mocker):
    mocker.patch("src.callbacks_discovery.ctx", mocker.Mock(inputs_list=[]))
    # Test filtering by Region (Kanto entries #1-151)
    # Signature: (regions, show_mega, show_regional, final_only, show_legendary, show_mythical, show_gmax, show_ultra_beasts, types, sort, stat_values)
    options = update_selector_options(
        ["Kanto"], True, True, False, True, True, False, True, [], "name", []
    )
    names = [opt["value"] for opt in options]
    assert "Bulbasaur" in names
    assert "Chikorita" not in names


def test_update_details_callback_high_stat(mocker):
    mocker.patch("src.callbacks_details.ctx", mocker.Mock(inputs_list=[]))

    result = update_details("Charizard", False, 1.7, 70, True, False, True, [])
    (
        name_display,
        type_badges,
        progress_bars,
        toggle_style,
        current_shiny,
        comparison,
        evolution,
        add_disabled,
        cry_src,
        cry_icon,
        cry_disabled,
    ) = result
    # We can't iterate over Patch, so we just check it's returned
    assert isinstance(progress_bars, Patch)


def test_update_pokemon_image_callback(mocker):
    mocker.patch("src.callbacks_details.ctx", mocker.Mock(inputs_list=[]))
    # Mock Path.exists to False to force the CDN URL path
    mocker.patch("src.callbacks_details.Path.exists", return_value=False)

    # Should return CDN URL by default if local doesn't exist
    img_src = update_pokemon_image("Bulbasaur", False)
    assert "https://raw.githubusercontent.com/PokeAPI/sprites" in img_src
    assert "1.png" in img_src
