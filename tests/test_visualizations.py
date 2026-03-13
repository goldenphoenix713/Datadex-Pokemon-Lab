import plotly.graph_objects as go
from visualizations import (
    create_radar_chart,
    create_type_leaderboard,
    create_scatter_plot,
)


def test_create_radar_chart_returns_figure(sample_pokemon_df):
    fig = create_radar_chart(sample_pokemon_df, ["Bulbasaur", "Charmander"])
    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 2


def test_create_radar_chart_empty_selection(sample_pokemon_df):
    fig = create_radar_chart(sample_pokemon_df, [])
    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 0


def test_create_type_leaderboard_returns_figure(sample_pokemon_df):
    fig = create_type_leaderboard(sample_pokemon_df, "Attack")
    assert isinstance(fig, go.Figure)
    assert len(fig.data) > 0


def test_create_scatter_plot_returns_figure(sample_pokemon_df):
    fig = create_scatter_plot(sample_pokemon_df, "Weight", "Speed")
    assert isinstance(fig, go.Figure)
    assert len(fig.data) > 0


def test_create_type_leaderboard_invalid_stat(sample_pokemon_df):
    fig = create_type_leaderboard(sample_pokemon_df, "InvalidStat")
    assert isinstance(fig, go.Figure)
    assert "compare" in fig.layout.title.text


def test_create_scatter_plot_missing_axes(sample_pokemon_df):
    fig = create_scatter_plot(sample_pokemon_df, "", "Speed")
    assert isinstance(fig, go.Figure)
    assert "explore" in fig.layout.title.text
