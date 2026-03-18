from typing import Any, List
import plotly.express as px
import plotly.graph_objects as go

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

RADAR_CATEGORIES = [
    "HP",
    "Attack",
    "Defense",
    "Speed",
    "Special Defense",
    "Special Attack",
]


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


def get_radar_dummy_trace() -> go.Scatterpolar:
    """Return a hidden dummy trace to keep the radar chart in polar mode."""
    return go.Scatterpolar(
        r=[0] * len(RADAR_CATEGORIES),
        theta=RADAR_CATEGORIES,
        showlegend=False,
        hoverinfo="skip",
        marker=dict(opacity=0),
    )


def get_radar_base_figure() -> go.Figure:
    """Create a radar chart base with layout and styling but no data."""
    from src.data import MAX_BASE_STAT

    fig = go.Figure()
    # Add a dummy trace with all categories to space axes correctly
    fig.add_trace(
        go.Scatterpolar(
            r=[0] * len(RADAR_CATEGORIES),
            theta=RADAR_CATEGORIES,
            showlegend=False,
            hoverinfo="skip",
            marker=dict(opacity=0),
        )
    )

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, MAX_BASE_STAT],
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
        height=400,
        transition=dict(duration=500, easing="cubic-in-out"),
        paper_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def get_radar_traces(table: Any, pokemon_names: List[str]) -> List[go.Scatterpolar]:
    """Generate radar traces for selected Pokémon."""
    if not pokemon_names:
        return []

    import pyarrow.compute as pc

    selected_data = table.filter(pc.field("Name").isin(pokemon_names))
    traces = []

    for row in selected_data.to_pylist():
        stats = [row[cat] for cat in RADAR_CATEGORIES]
        stats.append(stats[0])
        closed_categories = RADAR_CATEGORIES + [RADAR_CATEGORIES[0]]

        traces.append(
            go.Scatterpolar(
                r=stats,
                theta=closed_categories,
                fill="toself",
                name=row["Name"],
                hoverinfo="text",
                text=[f"{cat}: {val}" for cat, val in zip(closed_categories, stats)],
            )
        )
    return traces


def create_radar_chart(table: Any, pokemon_names: List[str]) -> go.Figure:
    """Create a radar chart by combining base figure and data traces."""
    fig = get_radar_base_figure()
    traces = get_radar_traces(table, pokemon_names)
    if traces:
        # Replace the dummy trace if we have real data
        fig.data = traces
    return fig


def get_leaderboard_base_figure(stat_column: str = "Attack") -> go.Figure:
    """Create a bar chart base with layout and styling but no data."""
    fig = go.Figure()
    fig.update_layout(
        title=dict(text=f"Top {stat_column} by Type", font=dict(color="white")),
        xaxis=dict(
            title=dict(text=stat_column, font=dict(color="white")),
            gridcolor="rgba(255,255,255,0.1)",
            tickfont=dict(color="white"),
            title_font=dict(color="white"),
        ),
        yaxis=dict(
            title=dict(text="", font=dict(color="white")),
            autorange="reversed",
            tickfont=dict(color="white"),
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=40, b=0),
        height=400,
        showlegend=False,
        transition=dict(duration=500, easing="cubic-in-out"),
    )
    return fig


def get_leaderboard_data(pokemon_table: Any, stat_column: str) -> dict:
    """Generate bar trace and global average line for the leaderboard."""
    from src.stats_logic import compute_type_averages, get_global_avg

    type_stats = compute_type_averages(pokemon_table, stat_column)
    global_avg = get_global_avg(pokemon_table, stat_column)

    if not type_stats:
        return {"trace": None, "global_avg": None}

    trace = go.Bar(
        x=[row["avg_stat"] for row in type_stats],
        y=[row["Primary Type"] for row in type_stats],
        orientation="h",
        marker_color=[
            TYPE_COLORS.get(row["Primary Type"], "#68A090") for row in type_stats
        ],
        text=[round(row["avg_stat"], 1) for row in type_stats],
        textposition="auto",
        name="Type Average",
        textfont=dict(color="white"),
    )

    return {"trace": trace, "global_avg": global_avg}


def create_type_leaderboard(pokemon_table: Any, stat_column: str) -> go.Figure:
    """Create a type leaderboard by combining base figure and data elements."""
    fig = get_leaderboard_base_figure(stat_column)
    data = get_leaderboard_data(pokemon_table, stat_column)

    if data["trace"]:
        fig.add_trace(data["trace"])
        fig.add_vline(
            x=data["global_avg"],
            line_dash="dot",
            line_color="white",
            annotation_text=f"Global Average: {data['global_avg']:.1f}",
            annotation_position="bottom right",
            annotation_font=dict(color="white", size=12),
        )
    return fig


def get_scatter_base_figure(x_col: str = "Weight", y_col: str = "Speed") -> go.Figure:
    """Create a scatter plot base with layout and styling but no data."""
    fig = go.Figure()
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
        xaxis=dict(
            title=dict(text=x_col, font=dict(color="white")),
            gridcolor="rgba(255,255,255,0.1)",
            autorange=True,
        ),
        yaxis=dict(
            title=dict(text=y_col, font=dict(color="white")),
            gridcolor="rgba(255,255,255,0.1)",
            autorange=True,
        ),
        template="plotly_dark",
        transition=dict(duration=500, easing="cubic-in-out"),
    )
    return fig


def create_scatter_plot(pokemon_table: Any, x_col: str, y_col: str) -> go.Figure:
    """Create a scatter plot by combining base figure and px.scatter data."""
    if not x_col or not y_col:
        fig = get_scatter_base_figure()
        fig.update_layout(
            title=dict(text="Select both axes to explore", font=dict(color="white"))
        )
        return fig

    # Plotly 6.0+ handles Arrow tables directly
    # px.scatter handles the complex color mapping and hover data logic
    px_fig = px.scatter(
        pokemon_table,
        x=x_col,
        y=y_col,
        color="Primary Type",
        hover_name="Name",
        hover_data={
            "Typing": True,
            "Primary Type": False,
            "Secondary Type": False,
        },
        color_discrete_map=TYPE_COLORS,
        template="plotly_dark",
    )

    fig = get_scatter_base_figure(x_col, y_col)
    fig.data = px_fig.data
    # Re-apply point styling
    fig.update_traces(
        marker=dict(size=10, opacity=0.7, line=dict(width=1, color="white"))
    )

    return fig
