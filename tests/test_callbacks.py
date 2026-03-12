from app import update_radar, update_leaderboard, update_details
import plotly.graph_objects as go
from dash import html


def test_update_radar_callback(mocker):
    # Mock create_radar_chart if needed, or just let it run if df is available
    fig = update_radar(["Bulbasaur"])
    assert isinstance(fig, go.Figure)


def test_update_leaderboard_callback():
    fig = update_leaderboard("Defense")
    assert isinstance(fig, go.Figure)


def test_update_details_callback():
    img_src, name_display, progress_bars = update_details(["Bulbasaur"])
    assert "official-artwork/1.png" in img_src
    assert name_display == "Bulbasaur"
    assert len(progress_bars) > 0
    assert isinstance(progress_bars[0], html.Div)


def test_update_details_callback_no_selection():
    img_src, name_display, progress_bars = update_details([])
    assert img_src == ""
    assert name_display == "Select a Pokémon"
    assert progress_bars == []
