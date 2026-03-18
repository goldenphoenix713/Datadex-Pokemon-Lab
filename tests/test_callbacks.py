import plotly.graph_objects as go
from src.callbacks_charts import update_radar, update_leaderboard, update_scatter
from src.callbacks_details import update_details
from src.callbacks_discovery import update_focus_options as update_selector_options


def test_update_radar_callback(mocker):
    # Mock create_radar_chart if needed, or just let it run if df is available
    mocker.patch("src.callbacks_charts.ctx", mocker.Mock(inputs_list=[]))
    fig = update_radar(["Bulbasaur"])
    assert isinstance(fig, go.Figure)


def test_update_leaderboard_callback(mocker):
    mocker.patch("src.callbacks_charts.ctx", mocker.Mock(inputs_list=[]))
    # Signature: (stat, regions, show_mega, show_regional, final_only, show_legendary, show_mythical, show_gmax, show_ultra_beasts, selected_types, stat_values)
    fig = update_leaderboard(
        "Defense", [], True, True, False, True, True, False, True, [], []
    )
    assert isinstance(fig, go.Figure)


def test_update_details_callback(mocker):
    # Mock ensure_pokemon_image and shiny_lookup
    mocker.patch(
        "src.callbacks_details.ensure_pokemon_image",
        return_value="assets/images/1.png",
    )
    mocker.patch("src.callbacks_details.has_shiny_artwork", return_value=True)
    mocker.patch(
        "src.callbacks_details.ensure_pokemon_cry", return_value="assets/sounds/1.ogg"
    )
    mocker.patch("src.callbacks_details.ctx", mocker.Mock(inputs_list=[]))

    # Signature: (focus_name, is_shiny, t_height, t_weight, show_mega, show_gmax, show_regional, team)
    result_shiny = update_details("Bulbasaur", True, 1.7, 70, True, False, True, [])
    # Check current_shiny (6th element, index 5)
    assert result_shiny[5] is True

    result = update_details("Bulbasaur", False, 1.7, 70, True, False, True, [])
    (
        img_src,
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
    assert img_src == "assets/images/1.png"
    assert name_display == "Bulbasaur"
    assert toggle_style == {"display": "block"}
    assert current_shiny is False
    assert add_disabled is False
    assert cry_src == "assets/sounds/1.ogg"


def test_update_details_callback_no_selection(mocker):
    mocker.patch("src.callbacks_details.ctx", mocker.Mock(inputs_list=[]))
    result = update_details("", False, 1.7, 70, True, False, True, [])
    (
        img_src,
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
    assert img_src == ""
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
    mocker.patch(
        "src.callbacks_details.ensure_pokemon_image",
        return_value="assets/images/6.png",
    )
    mocker.patch("src.callbacks_details.has_shiny_artwork", return_value=True)
    mocker.patch(
        "src.callbacks_details.ensure_pokemon_cry", return_value="assets/sounds/6.ogg"
    )
    mocker.patch("src.callbacks_details.ctx", mocker.Mock(inputs_list=[]))
    # Charizard stats are high enough for green? Attack is 84, Sp Atk is 109.
    result = update_details("Charizard", False, 1.7, 70, True, False, True, [])
    (
        img_src,
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
    # Find Special Attack or just check any green
    assert any(
        getattr(bar.children[1], "color", None) == "green" for bar in progress_bars
    )


def test_update_scatter_callback(mocker):
    mocker.patch("src.callbacks_charts.ctx", mocker.Mock(inputs_list=[]))
    # Signature: (x, y, regions, show_mega, show_regional, final_only, show_legendary, show_mythical, show_gmax, show_ultra_beasts, types, stat_values)
    fig = update_scatter(
        "Attack",
        "Defense",
        [],
        True,
        True,
        False,
        True,
        True,
        False,
        True,
        [],
        [],
    )
    assert isinstance(fig, go.Figure)
