from typing import Any, List
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


def create_radar_chart(table: Any, pokemon_names: List[str]) -> go.Figure:
    """Create a radar chart comparing stats of selected Pokémon using DuckDB for speed.

    :param table: The Pokémon PyArrow Table.
    :param pokemon_names: A list of Pokémon names to compare.
    :return: A Plotly radar chart.
    """
    logger.debug(f"Creating radar chart for {len(pokemon_names)} Pokémon.")
    categories = [
        "HP",
        "Attack",
        "Defense",
        "Speed",
        "Special Defense",
        "Special Attack",
    ]

    from src.data import conn, MAX_BASE_STAT

    max_stat = MAX_BASE_STAT

    logger.debug(f"Categories for radar: {categories}")
    # Efficiently find global max stat across all categories
    stat_columns = ", ".join([f'"{c}"' for c in categories])
    res = (
        conn.execute(f"SELECT MAX(GREATEST({stat_columns})) FROM pokemon")
        .to_arrow_table()
        .to_pylist()
    )

    # Safe extraction of the single scalar result
    if res and res[0]:
        # Get the first (and only) value from the first row dict
        max_stat = list(res[0].values())[0]
    else:
        max_stat = 255

    # Ensure max_stat is a number and not None
    if max_stat is None or not isinstance(max_stat, (int, float)):
        max_stat = 255

    logger.debug(f"Computed max_stat: {max_stat}")

    fig = go.Figure()

    if not pokemon_names:
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, max_stat])),
            showlegend=False,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )
        return fig

    # Filter for the chosen Pokémon using SQL
    names_list = ", ".join([f"'{n}'" for n in pokemon_names])
    selected_data = conn.execute(
        f'SELECT * FROM pokemon WHERE "Name" IN ({names_list})'
    ).to_arrow_table()

    logger.debug(
        f"Radar query found {selected_data.num_rows} match(es) for names: {pokemon_names}"
    )
    if selected_data.num_rows > 0:
        logger.debug(f"Found names in data: {selected_data['Name'].to_pylist()}")

    # Add a trace for each selected Pokémon
    for row in selected_data.to_pylist():
        stats = [row[cat] for cat in categories]
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


def create_type_leaderboard(df: Any, stat_column: str) -> go.Figure:
    """Create a bar chart showing averaged stats by Pokémon primary type using DuckDB."""
    logger.debug(f"Creating type leaderboard for stat: {stat_column}")
    fig = go.Figure()

    if not stat_column:
        return fig

    # Verify stat column exists
    if df is None:
        logger.warning("No data provided to leaderboard.")
        return fig

    # Support both PyArrow/DuckDB and Pandas
    # ARROW/DUCKDB FIRST to avoid property collision where Table has .columns property (RecordBatch)
    if hasattr(df, "column_names"):
        cols = df.column_names
    elif hasattr(df, "columns"):
        cols = df.columns
    else:
        cols = []

    if stat_column not in cols:
        logger.warning(f"Stat column '{stat_column}' not found in data.")
        fig.update_layout(
            title=dict(
                text=f"Stat '{stat_column}' not found to compare",
                font=dict(color="white"),
            ),
        )
        return fig

    from src.data import conn

    # Use SQL for grouping and averaging
    query = f"""
    SELECT 
        "Primary Type", 
        AVG("{stat_column}") as avg_stat
    FROM pokemon
    GROUP BY "Primary Type"
    ORDER BY avg_stat DESC
    """
    type_stats = conn.execute(query).to_arrow_table().to_pylist()
    res = (
        conn.execute(f'SELECT AVG("{stat_column}") FROM pokemon')
        .to_arrow_table()
        .to_pylist()
    )
    global_avg = res[0][list(res[0].keys())[0]] if res and res[0] else 0

    if not type_stats:
        return fig

    # Add horizontal bars colored by the type palette
    fig.add_trace(
        go.Bar(
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


def create_scatter_plot(df: Any, x_col: str, y_col: str) -> go.Figure:
    """Create a scatter plot comparing two stats using Plotly's Arrow support."""
    if not x_col or not y_col:
        fig = go.Figure()
        fig.update_layout(
            title=dict(text="Select both axes to explore", font=dict(color="white")),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )
        return fig

    # Plotly 6.0+ handles Arrow tables directly
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
