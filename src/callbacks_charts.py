from typing import Any, List
from dash import callback, Input, Output, ALL, ctx
from loguru import logger
from src.utils import get_filtered_table as get_filtered_df
from visualizations import (
    create_scatter_plot,
    create_radar_chart,
    create_type_leaderboard,
)


@callback(Output("radar-chart", "figure"), Input("team-store", "data"))
def update_radar(selected_pokemon: List[str]) -> Any:
    """Update the radar chart based on the team store."""
    logger.debug(f"Updating radar chart for team: {selected_pokemon}")
    from src.data import df

    return create_radar_chart(df, selected_pokemon)


@callback(
    Output("leaderboard-chart", "figure"),
    Input("stat-selector", "value"),
    Input("region-filter", "value"),
    Input("mega-toggle", "checked"),
    Input("regional-toggle", "checked"),
    Input("final-evolution-toggle", "checked"),
    Input("legendary-toggle", "checked"),
    Input("mythical-toggle", "checked"),
    Input("gmax-toggle", "checked"),
    Input("ultra-beast-toggle", "checked"),
    Input("type-filter", "value"),
    Input({"type": "stat", "name": ALL}, "value"),
)
def update_leaderboard(
    stat: str,
    regions: List[str],
    show_mega: bool,
    show_regional: bool,
    final_only: bool,
    show_legendary: bool,
    show_mythical: bool,
    show_gmax: bool,
    show_ultra_beasts: bool,
    selected_types: List[str],
    stat_values: List[List[int]],
) -> Any:
    """Update the type leaderboard based on a selected stat and filters."""
    stat_ranges = {
        item["id"]["name"]: item["value"]
        for item in ctx.inputs_list
        if isinstance(item, list)
        for item in item
        if isinstance(item["id"], dict) and item["id"].get("type") == "stat"
    }
    filtered_df = get_filtered_df(
        regions,
        show_mega,
        show_regional,
        final_only,
        show_legendary,
        show_mythical,
        show_gmax,
        show_ultra_beasts,
        selected_types,
        stat_ranges,
    )
    return create_type_leaderboard(filtered_df, stat)


@callback(
    Output("scatter-plot", "figure"),
    Input("x-axis-selector", "value"),
    Input("y-axis-selector", "value"),
    Input("region-filter", "value"),
    Input("mega-toggle", "checked"),
    Input("regional-toggle", "checked"),
    Input("final-evolution-toggle", "checked"),
    Input("legendary-toggle", "checked"),
    Input("mythical-toggle", "checked"),
    Input("gmax-toggle", "checked"),
    Input("ultra-beast-toggle", "checked"),
    Input("type-filter", "value"),
    Input({"type": "stat", "name": ALL}, "value"),
)
def update_scatter(
    x: str,
    y: str,
    regions: List[str],
    show_mega: bool,
    show_regional: bool,
    final_only: bool,
    show_legendary: bool,
    show_mythical: bool,
    show_gmax: bool,
    show_ultra_beasts: bool,
    selected_types: List[str],
    stat_values: List[List[int]],
) -> Any:
    """Update the scatter plot visualization for exploring outliers with filters."""
    stat_ranges = {
        item["id"]["name"]: item["value"]
        for item in ctx.inputs_list
        if isinstance(item, list)
        for item in item
        if isinstance(item["id"], dict) and item["id"].get("type") == "stat"
    }
    filtered_df = get_filtered_df(
        regions,
        show_mega,
        show_regional,
        final_only,
        show_legendary,
        show_mythical,
        show_gmax,
        show_ultra_beasts,
        selected_types,
        stat_ranges,
    )
    return create_scatter_plot(filtered_df, x, y)
