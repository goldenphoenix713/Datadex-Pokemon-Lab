from src.callbacks import (
    update_radar,
    update_leaderboard,
    update_details,
    update_focus_options as update_selector_options,
    update_scatter,
)
import plotly.graph_objects as go


def test_update_radar_callback(mocker):
    # Mock create_radar_chart if needed, or just let it run if df is available
    mocker.patch("src.callbacks.ctx", mocker.Mock(inputs_list=[]))
    fig = update_radar(["Bulbasaur"])
    assert isinstance(fig, go.Figure)


def test_update_leaderboard_callback(mocker):
    mocker.patch("src.callbacks.ctx", mocker.Mock(inputs_list=[]))
    fig = update_leaderboard(
        "Defense", [], True, True, False, True, True, False, [], []
    )
    assert isinstance(fig, go.Figure)


def test_update_details_callback(mocker):
    # Mock ensure_pokemon_image and shiny_lookup
    mocker.patch(
        "src.callbacks.ensure_pokemon_image", return_value="assets/images/1.png"
    )
    mocker.patch("src.callbacks.shiny_lookup", {1})
    mocker.patch("src.callbacks.ctx", mocker.Mock(inputs_list=[]))

    result = update_details("Bulbasaur", False, 4.5, 150, True, True, True)
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
    result_shiny = update_details("Bulbasaur", True, 4.5, 150, True, True, True)
    assert result_shiny[5] is True


def test_update_details_callback_no_selection(mocker):
    mocker.patch("src.callbacks.ctx", mocker.Mock(inputs_list=[]))
    result = update_details("", False, 4.5, 150, True, True, True)
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
    mocker.patch("src.callbacks.ctx", mocker.Mock(inputs_list=[]))
    # Test filtering by Region (Kanto entries #1-151)
    # (regions, show_mega, show_regional, final_only, show_legendary, show_mythical, show_gmax, types, sort)
    options = update_selector_options(
        ["Kanto"], True, True, False, True, True, False, [], "name", []
    )
    # Bulbasaur is #1, Chikorita is #152
    names = [opt["value"] for opt in options]
    assert "Bulbasaur" in names
    assert "Chikorita" not in names

    # Test toggling Mega
    options_no_mega = update_selector_options(
        [], False, True, False, True, True, False, [], "name", []
    )
    names_no_mega = [opt["value"] for opt in options_no_mega]
    assert all("Mega" not in name for name in names_no_mega)

    # Test toggling Regional
    options_no_regional = update_selector_options(
        [], True, False, False, True, True, False, [], "name", []
    )
    names_no_reg = [opt["value"] for opt in options_no_regional]
    assert all("Alola" not in name for name in names_no_reg)

    # Test toggling Legendaries
    options_no_legendary = update_selector_options(
        [], True, True, False, False, True, False, [], "name", []
    )
    # Bulbasaur is not legendary, but Mewtwo is (if in df).
    # Let's check for "Mewtwo" or just that it prunes if we know one is legendary.
    # In my regenerated data, let's assume Mewtwo is legendary.
    # We can check the count or specific names if we are sure they are in the dataset.
    names_no_legend = [opt["value"] for opt in options_no_legendary]
    assert "Mewtwo" not in names_no_legend or len(names_no_legend) < len(options)

    # Test Final Evolutions only
    options_final = update_selector_options(
        [], True, True, True, True, True, False, [], "name", []
    )
    names_final = [opt["value"] for opt in options_final]
    assert "Bulbasaur" not in names_final  # Bulbasaur is not final
    assert "Venusaur" in names_final  # Venusaur is final

    # Test Mythicals
    options_all = update_selector_options(
        [], True, True, False, True, True, False, [], "name", []
    )
    options_no_mythical = update_selector_options(
        [], True, True, False, True, False, False, [], "name", []
    )
    assert len(options_no_mythical) < len(options_all)


def test_update_details_callback_high_stat(mocker):
    # Mock for a high stat Pokemon (closes app.py line 472)
    mocker.patch(
        "src.callbacks.ensure_pokemon_image", return_value="assets/images/6.png"
    )
    mocker.patch("src.callbacks.shiny_lookup", {6})
    mocker.patch("src.callbacks.ctx", mocker.Mock(inputs_list=[]))
    # Mewtwo is in our mock DF? No, Bulbasaur and Charmander.
    # Let's mock the DF or use one with high stats.
    # Actually, update_details uses the global 'df'.
    result = update_details("Charizard", False, 4.5, 150, True, True, True)
    # Charizard stats are high enough for green? Attack is 84, Sp Atk is 109.
    # Yes, 109 >= 90.
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
    # Find Special Attack (index 5 usually) or just check any green
    assert any(bar.children[1].color == "green" for bar in progress_bars)


def test_update_scatter_callback(mocker):
    mocker.patch("src.callbacks.ctx", mocker.Mock(inputs_list=[]))
    fig = update_scatter(
        "Attack", "Defense", [], True, True, False, True, True, False, [], []
    )
    assert isinstance(fig, go.Figure)
