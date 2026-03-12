"""Module providing functions to create Plotly visualizations for Pokémon data."""

from typing import Any, List

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from loguru import logger

# Canonical Pokemon Type Colors
TYPE_COLORS = {
    "Normal": "#A8A878",
    "Fire": "#F08030",
    "Water": "#6890F0",
    "Grass": "#78C850",
    "Electric": "#F8D030",
    "Ice": "#98D8D8",
    "Fighting": "#C03028",
    "Poison": "#A040A0",
    "Ground": "#E0C068",
    "Flying": "#A890F0",
    "Psychic": "#F85888",
    "Bug": "#A8B020",
    "Rock": "#B8A038",
    "Ghost": "#705898",
    "Dragon": "#7038F8",
    "Dark": "#705848",
    "Steel": "#B8B8D0",
    "Fairy": "#EE99AC",
    "None": "#68A090",
}


def create_type_badge(pokemon_type: str) -> Any:
    """Create a Mantine Badge component for a given Pokémon type.

    :param pokemon_type: The Pokémon type (e.g., 'Fire', 'Water').
    :type pokemon_type: str
    :return: A dash-mantine-components Badge component.
    :rtype: dmc.Badge
    """
    import dash_mantine_components as dmc

    # Get the canonical color for the type, default to a neutral teal
    color = TYPE_COLORS.get(pokemon_type, "#68A090")
    return dmc.Badge(
        pokemon_type,
        color=color,
        variant="filled",
        size="lg",
        radius="sm",
        style={"textTransform": "capitalize", "fontWeight": 700},
    )


def create_radar_chart(df: pd.DataFrame, pokemon_names: List[str]) -> go.Figure:
    """Create a radar chart comparing stats of selected Pokémon.

    :param df: The Pokémon DataFrame.
    :type df: pd.DataFrame
    :param pokemon_names: A list of Pokémon names to compare.
    :type pokemon_names: List[str]
    :return: A Plotly radar chart.
    :rtype: go.Figure
    """
    logger.debug(f"Creating radar chart for {len(pokemon_names)} Pokémon.")
    # Defensive stats to compare
    categories = [
        "HP",
        "Attack",
        "Defense",
        "Speed",
        "Special Defense",
        "Special Attack",
    ]
    fig = go.Figure()

    # Determine scale based on all available data to keep visuals consistent
    max_stat = df[categories].max().max()

    # If nothing selected, return empty chart with fixed range
    if not pokemon_names:
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, max_stat])),
            showlegend=False,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )
        return fig

    # Filter for the chosen Pokémon
    selected_data = df[df["Name"].isin(pokemon_names)]

    # Add a trace for each selected Pokémon
    for _, row in selected_data.iterrows():
        stats = [row[cat] for cat in categories]
        # Radar charts need to wrap back to the start to close the polygon
        stats.append(stats[0])
        closed_categories = categories + [categories[0]]

        fig.add_trace(
            go.Scatterpolar(
                r=stats,
                theta=closed_categories,
                fill="toself",
                name=row["Name"],
                hoverinfo="text",
                text=[f"{cat}: {val}" for cat, val in zip(closed_categories, stats)],
            )
        )

    # Style the polar axes and legend
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, max_stat],
                showticklabels=False,
                gridcolor="lightgrey",
            ),
            angularaxis=dict(
                tickfont=dict(size=12, color="gray"), rotation=90, direction="clockwise"
            ),
        ),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.3,
            xanchor="center",
            x=0.5,
            font=dict(color="white"),
        ),
        margin=dict(l=40, r=40, t=40, b=40),
        transition=dict(duration=500, easing="cubic-in-out"),
        paper_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def create_type_leaderboard(df: pd.DataFrame, stat_column: str) -> go.Figure:
    """Create a bar chart showing averaged stats by Pokémon primary type.

    :param df: The Pokémon DataFrame.
    :type df: pd.DataFrame
    :param stat_column: The name of the stat column to average and compare.
    :type stat_column: str
    :return: A Plotly horizontal bar chart.
    :rtype: go.Figure
    """
    logger.debug(f"Creating type leaderboard for stat: {stat_column}")
    fig = go.Figure()

    # Validation check
    if not stat_column or stat_column not in df.columns:
        fig.update_layout(
            title=dict(text="Select a stat to compare", font=dict(color="white")),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )
        return fig

    # Calculate average stat per primary type, sorted highest to lowest
    type_stats = (
        df.groupby("Primary Type", observed=False)[stat_column]
        .mean()
        .sort_values(ascending=False)
        .reset_index()
    )
    global_avg = df[stat_column].mean()

    fig = go.Figure()

    # Add horizontal bars colored by the type palette
    fig.add_trace(
        go.Bar(
            x=type_stats[stat_column],
            y=type_stats["Primary Type"],
            orientation="h",
            marker_color=[
                TYPE_COLORS.get(t, "#68A090") for t in type_stats["Primary Type"]
            ],
            text=type_stats[stat_column].round(1),
            textposition="auto",
            name="Type Average",
            textfont=dict(color="white"),
        )
    )

    # Add a global benchmark line for comparison
    fig.add_vline(
        x=global_avg,
        line_dash="dot",
        line_color="white",
        annotation_text=f"Global Average: {global_avg:.1f}",
        annotation_position="bottom right",
        annotation_font=dict(color="white", size=12),
    )

    fig.update_layout(
        title=dict(text=f"Top {stat_column} by Type", font=dict(color="white")),
        xaxis=dict(
            title=stat_column,
            gridcolor="rgba(255,255,255,0.1)",
            tickfont=dict(color="white"),
            title_font=dict(color="white"),
        ),
        yaxis=dict(title="", autorange="reversed", tickfont=dict(color="white")),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=40, b=0),
        height=400,
        showlegend=False,
    )

    return fig


def create_scatter_plot(df: pd.DataFrame, x_col: str, y_col: str) -> go.Figure:
    """Create a scatter plot comparing two stats across all Pokémon.

    :param df: The Pokémon DataFrame.
    :type df: pd.DataFrame
    :param x_col: Stat for the X-axis.
    :type x_col: str
    :param y_col: Stat for the Y-axis.
    :type y_col: str
    :return: A Plotly scatter plot.
    :rtype: go.Figure
    """
    # Validation check for axis selection
    if not x_col or not y_col:
        fig = go.Figure()
        fig.update_layout(
            title=dict(text="Select both axes to explore", font=dict(color="white")),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )
        return fig

    # Build scatter with automatic coloring by type
    fig = px.scatter(
        df,
        x=x_col,
        y=y_col,
        color="Primary Type",
        hover_name="Name",
        color_discrete_map=TYPE_COLORS,
        template="plotly_dark",
    )

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=40, b=0),
        legend=dict(
            title=dict(text="Type", font=dict(color="white")),
            orientation="h",
            y=-0.2,
            font=dict(color="white"),
        ),
        xaxis=dict(gridcolor="rgba(255,255,255,0.1)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.1)"),
    )

    # Style data points: solid marker with white outline for visibility
    fig.update_traces(
        marker=dict(size=10, opacity=0.7, line=dict(width=1, color="white"))
    )

    return fig
