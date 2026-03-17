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
    mocker.patch("src.callbacks_details.ctx", mocker.Mock(inputs_list=[]))

    # Signature: (focus_name, is_shiny, t_height, t_weight, show_mega, show_gmax, show_regional)
    result = update_details("Bulbasaur", False, 1.7, 70, True, False, True)
    (
        img_src,
        name_display,
        type_badges,
        progress_bars,
        toggle_style,
        current_shiny,
        comparison,
        evolution,
    ) = result
    assert img_src == "assets/images/1.png"
    assert name_display == "Bulbasaur"
    assert toggle_style == {"display": "block"}
    assert current_shiny is False

    # Test shiny toggle on
    result_shiny = update_details("Bulbasaur", True, 1.7, 70, True, False, True)
    assert result_shiny[5] is True


def test_update_details_callback_no_selection(mocker):
    mocker.patch("src.callbacks_details.ctx", mocker.Mock(inputs_list=[]))
    result = update_details("", False, 1.7, 70, True, False, True)
    (
        img_src,
        name_display,
        type_badges,
        progress_bars,
        toggle_style,
        current_shiny,
        comparison,
        evolution,
    ) = result
    assert img_src == ""
    assert name_display == "Select a Pokémon"
    assert toggle_style == {"display": "none"}


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

    # Test toggling Mega
    options_no_mega = update_selector_options(
        [], False, True, False, True, True, False, True, [], "name", []
    )
    names_no_mega = [opt["value"] for opt in options_no_mega]
    assert all("Mega" not in name for name in names_no_mega)

    # Test toggling Regional
    options_no_regional = update_selector_options(
        [], True, False, False, True, True, False, True, [], "name", []
    )
    names_no_reg = [opt["value"] for opt in options_no_regional]
    # In our renaming logic, Alola -> Alolan. Let's check for "Alolan".
    assert all("Alolan" not in name for name in names_no_reg)

    # Test toggling Legendaries
    options_no_legendary = update_selector_options(
        [], True, True, False, False, True, False, True, [], "name", []
    )
    names_no_legend = [opt["value"] for opt in options_no_legendary]
    assert "Mewtwo" not in names_no_legend or len(names_no_legend) < len(options)

    # Test Final Evolutions only
    options_final = update_selector_options(
        [], True, True, True, True, True, False, True, [], "name", []
    )
    names_final = [opt["value"] for opt in options_final]
    assert "Bulbasaur" not in names_final  # Bulbasaur is not final
    assert "Venusaur" in names_final  # Venusaur is final


def test_update_details_callback_high_stat(mocker):
    mocker.patch(
        "src.callbacks_details.ensure_pokemon_image",
        return_value="assets/images/6.png",
    )
    mocker.patch("src.callbacks_details.has_shiny_artwork", return_value=True)
    mocker.patch("src.callbacks_details.ctx", mocker.Mock(inputs_list=[]))
    # Charizard stats are high enough for green? Attack is 84, Sp Atk is 109.
    result = update_details("Charizard", False, 1.7, 70, True, False, True)
    (
        img_src,
        name_display,
        type_badges,
        progress_bars,
        toggle_style,
        current_shiny,
        comparison,
        evolution,
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
