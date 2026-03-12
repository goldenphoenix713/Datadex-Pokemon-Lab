"""Main entry point for the Data-Dex Dash application.

This module initializes the Dash app, defines the layout using dash-mantine-components,
and handles interactivity via Dash callbacks.
"""

from typing import Any, List, Tuple

import dash
import dash_mantine_components as dmc
from dash import Input, Output, callback, dcc, html

from data_manager import load_and_clean_data
from visualizations import (
    create_radar_chart,
    create_scatter_plot,
    create_type_badge,
    create_type_leaderboard,
)

# Enforce React 18.2.0 for DMC compatibility
# This is a specific requirement for dash-mantine-components to render correctly.
dash._dash_renderer._set_react_version("18.2.0")  # type: ignore[possibly-missing-attribute]

app = dash.Dash(__name__, title="Data-Dex: Ultimate Stat Lab")

# Load and prepare data on startup
df = load_and_clean_data()
pokemon_names = sorted(df["Name"].unique())
stat_options = ["HP", "Attack", "Defense", "Speed", "Special Defense", "Special Attack"]

# Define a consistent theme using Mantine's design system
custom_theme = {
    "fontFamily": "Inter, sans-serif",
    "headings": {"fontFamily": "PokemonSolid, sans-serif"},
    "primaryColor": "blue",
    "colorScheme": "dark",
}

# Application Layout
app.layout = dmc.MantineProvider(
    theme=custom_theme,
    children=[
        dmc.Container(
            size="xl",
            p="md",
            children=[
                # Header Section
                dmc.Center(
                    children=[
                        html.H1(
                            "Data-Dex: Ultimate Stat Lab", className="pokemon-title"
                        )
                    ]
                ),
                dmc.Grid(
                    gutter="lg",
                    children=[
                        # Left Column: User Selection and Radar Comparison
                        dmc.GridCol(
                            span={"base": 12, "md": 8},
                            children=[
                                dmc.Card(
                                    withBorder=True,
                                    shadow="sm",
                                    p="lg",
                                    radius="md",
                                    mb="md",
                                    children=[
                                        dmc.Title(
                                            "Face-Off Radar",
                                            order=2,
                                            className="pokemon-section-title",
                                        ),
                                        dmc.Text(
                                            "Select 2-3 Pokémon to compare their stats side-by-side.",
                                            c="dimmed",
                                            mb="md",
                                        ),
                                        # Multi-select dropdown for choosing Pokémon
                                        dmc.MultiSelect(
                                            id="pokemon-selector",
                                            label="Choose your Pokémon Team",
                                            placeholder="Search names...",
                                            data=pokemon_names,
                                            value=["Bulbasaur", "Charmander"],
                                            maxValues=3,
                                            searchable=True,
                                            clearable=True,
                                            mb="xl",
                                        ),
                                        dcc.Graph(
                                            id="radar-chart",
                                            config={"displayModeBar": False},
                                        ),
                                    ],
                                ),
                            ],
                        ),
                        # Right Column: Detail Card for the selected Pokémon
                        dmc.GridCol(
                            span={"base": 12, "md": 4},
                            children=[
                                dmc.Card(
                                    withBorder=True,
                                    shadow="sm",
                                    p="lg",
                                    radius="md",
                                    children=[
                                        dmc.Title(
                                            id="pokemon-name-display",
                                            order=2,
                                            className="pokemon-section-title",
                                        ),
                                        dmc.Center(
                                            children=[
                                                html.Img(
                                                    id="pokemon-image",
                                                    src="",
                                                    style={"height": "200px"},
                                                )
                                            ]
                                        ),
                                        # Box for type badges
                                        dmc.Center(
                                            children=[
                                                dmc.Group(
                                                    id="pokemon-types",
                                                    mt="sm",
                                                    gap="xs",
                                                )
                                            ]
                                        ),
                                        dmc.Space(h="md"),
                                        # Container for dynamic progress bars
                                        html.Div(id="stat-progress-bars"),
                                    ],
                                )
                            ],
                        ),
                        # Bottom Row: Global analysis components
                        dmc.GridCol(
                            span={"base": 12, "md": 6},
                            children=[
                                dmc.Card(
                                    withBorder=True,
                                    shadow="sm",
                                    p="lg",
                                    radius="md",
                                    children=[
                                        dmc.Title(
                                            "Type Leaderboard",
                                            order=3,
                                            className="pokemon-section-title",
                                        ),
                                        dmc.Text(
                                            "Which element hits the hardest?",
                                            c="dimmed",
                                            mb="md",
                                        ),
                                        # Dropdown to select the statistic for averaging
                                        dmc.Select(
                                            id="stat-selector",
                                            label="Compare averages for:",
                                            data=stat_options,
                                            value="Attack",
                                            mb="md",
                                        ),
                                        dcc.Graph(
                                            id="leaderboard-chart",
                                            config={"displayModeBar": False},
                                        ),
                                    ],
                                )
                            ],
                        ),
                        dmc.GridCol(
                            span={"base": 12, "md": 6},
                            children=[
                                dmc.Card(
                                    withBorder=True,
                                    shadow="sm",
                                    p="lg",
                                    radius="md",
                                    children=[
                                        dmc.Title(
                                            "Exploring the World",
                                            order=3,
                                            className="pokemon-section-title",
                                        ),
                                        dmc.Text(
                                            "Find the heaviest, fastest, or strangest Pokémon!",
                                            c="dimmed",
                                            mb="md",
                                        ),
                                        # Selectors for X and Y axes of the scatter plot
                                        dmc.Group(
                                            grow=True,
                                            children=[
                                                dmc.Select(
                                                    id="x-axis-selector",
                                                    label="Horizontal (X)",
                                                    data=stat_options
                                                    + ["Height", "Weight"],
                                                    value="Weight",
                                                ),
                                                dmc.Select(
                                                    id="y-axis-selector",
                                                    label="Vertical (Y)",
                                                    data=stat_options
                                                    + ["Height", "Weight"],
                                                    value="Speed",
                                                ),
                                            ],
                                            mb="md",
                                        ),
                                        dcc.Graph(
                                            id="scatter-plot",
                                            config={"displayModeBar": False},
                                        ),
                                    ],
                                )
                            ],
                        ),
                    ],
                ),
            ],
        )
    ],
)


# Interactivity: Callbacks to update visuals based on user input
@callback(Output("radar-chart", "figure"), Input("pokemon-selector", "value"))
def update_radar(selected_pokemon: List[str]) -> Any:
    """Update the radar chart based on selected Pokémon.

    :param selected_pokemon: List of names for chosen Pokémon.
    :type selected_pokemon: List[str]
    :return: A Plotly graph figure.
    :rtype: Any
    """
    return create_radar_chart(df, selected_pokemon)


@callback(Output("leaderboard-chart", "figure"), Input("stat-selector", "value"))
def update_leaderboard(stat: str) -> Any:
    """Update the type leaderboard based on a selected stat.

    :param stat: The Pokémon statistic to compare averages for.
    :type stat: str
    :return: A Plotly graph figure.
    :rtype: Any
    """
    return create_type_leaderboard(df, stat)


@callback(
    Output("scatter-plot", "figure"),
    Input("x-axis-selector", "value"),
    Input("y-axis-selector", "value"),
)
def update_scatter(x: str, y: str) -> Any:
    """Update the scatter plot visualization for exploring outliers.

    :param x: The stat to display on the X-axis.
    :type x: str
    :param y: The stat to display on the Y-axis.
    :type y: str
    :return: A Plotly graph figure.
    :rtype: Any
    """
    return create_scatter_plot(df, x, y)


@callback(
    Output("pokemon-image", "src"),
    Output("pokemon-name-display", "children"),
    Output("pokemon-types", "children"),
    Output("stat-progress-bars", "children"),
    Input("pokemon-selector", "value"),
)
def update_details(
    selected_pokemon: List[str],
) -> Tuple[str, str, List[Any], List[Any]]:
    """Update the detail card for the primary selected Pokémon.

    :param selected_pokemon: List of chosen Pokémon names.
    :type selected_pokemon: List[str]
    :return: A tuple containing the image source URL, the Pokémon name, list of
        type badge components, and list of stat progress bar components.
    :rtype: Tuple[str, str, List[Any], List[Any]]
    """
    # Defensive check: if no selection, show placeholder empty state
    if not selected_pokemon:
        return "", "Select a Pokémon", [], []

    # Identify the primary Pokémon (first in the list) for details
    name = selected_pokemon[0]
    p_data = df[df["Name"] == name].iloc[0]

    max_stat = df[stat_options].max().max()

    # Dynamically build progress bars for stats
    progress_bars = []
    for stat in stat_options:
        val = p_data[stat]
        # Normalize to the maximum stat value
        percent = (val / max_stat) * 100
        progress_bars.append(
            html.Div(
                [
                    dmc.Group(
                        justify="apart",
                        children=[
                            dmc.Text(stat, size="sm", fw=500),
                            dmc.Text(str(val), size="sm", c="blue"),
                        ],
                    ),
                    dmc.Progress(value=percent, mb="xs", animated=True),
                ]
            )
        )

    # Generate type badges using the helper from visualizations.py
    types = [p_data["Primary Type"]]
    if p_data["Secondary Type"] != "None":
        types.append(p_data["Secondary Type"])

    type_badges = [create_type_badge(t) for t in types]

    return p_data["Image_URL"], name, type_badges, progress_bars


if __name__ == "__main__":
    # Start the server (debug=True enables hot reloading)
    app.run_server(debug=True, port=8050, use_reloader=False)
