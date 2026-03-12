import plotly.graph_objects as go
import pandas as pd
import plotly.express as px

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


def create_type_badge(pokemon_type: str):
    import dash_mantine_components as dmc

    color = TYPE_COLORS.get(pokemon_type, "#68A090")
    return dmc.Badge(
        pokemon_type,
        color=color,
        variant="filled",
        size="lg",
        radius="sm",
        style={"textTransform": "capitalize", "fontWeight": 700},
    )


def create_radar_chart(df: pd.DataFrame, pokemon_names: list) -> go.Figure:
    categories = [
        "HP",
        "Attack",
        "Defense",
        "Speed",
        "Special Defense",
        "Special Attack",
    ]
    fig = go.Figure()

    max_stat = df[categories].max().max()

    if not pokemon_names:
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, max_stat])),
            showlegend=False,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )
        return fig

    selected_data = df[df["Name"].isin(pokemon_names)]

    for _, row in selected_data.iterrows():
        stats = [row[cat] for cat in categories]
        stats.append(stats[0])  # Close the polygon
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
    fig = go.Figure()

    if not stat_column or stat_column not in df.columns:
        fig.update_layout(
            title=dict(text="Select a stat to compare", font=dict(color="white")),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )
        return fig

    # Calculate group means
    type_stats = (
        df.groupby("Primary Type", observed=False)[stat_column]
        .mean()
        .sort_values(ascending=False)
        .reset_index()
    )
    global_avg = df[stat_column].mean()

    fig = go.Figure()

    # Add bars
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

    # Add vertical line for global average
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
    if not x_col or not y_col:
        fig = go.Figure()
        fig.update_layout(
            title=dict(text="Select both axes to explore", font=dict(color="white")),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )
        return fig

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

    fig.update_traces(
        marker=dict(size=10, opacity=0.7, line=dict(width=1, color="white"))
    )

    return fig
