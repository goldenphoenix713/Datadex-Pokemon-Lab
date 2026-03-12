import dash  # type: ignore[import-untyped]
from dash import html, dcc, Input, Output, callback
import dash_mantine_components as dmc  # type: ignore[import-untyped]
from data_manager import load_and_clean_data
from visualizations import (
    create_radar_chart,
    create_type_leaderboard,
    create_scatter_plot,
)

# Enforce React 18.2.0 for DMC compatibility
dash._dash_renderer._set_react_version("18.2.0")

app = dash.Dash(__name__, title="Data-Dex: Ultimate Stat Lab")

# Load data
df = load_and_clean_data()
pokemon_names = sorted(df["Name"].unique())
stat_options = ["HP", "Attack", "Defense", "Speed", "Special Defense", "Special Attack"]

custom_theme = {
    "fontFamily": "Inter, sans-serif",
    "headings": {"fontFamily": "PokemonSolid, sans-serif"},
    "primaryColor": "blue",
    "colorScheme": "dark",
}

app.layout = dmc.MantineProvider(
    theme=custom_theme,
    children=[
        dmc.Container(
            size="xl",
            p="md",
            children=[
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
                        # Left Column: Selection & Radar
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
                        # Right Column: Details & Images
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
                                        dmc.Space(h="md"),
                                        html.Div(id="stat-progress-bars"),
                                    ],
                                )
                            ],
                        ),
                        # Bottom Row: Leaderboard & Outlier Hunt
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


# Callbacks
@callback(Output("radar-chart", "figure"), Input("pokemon-selector", "value"))
def update_radar(selected_pokemon):
    return create_radar_chart(df, selected_pokemon)


@callback(Output("leaderboard-chart", "figure"), Input("stat-selector", "value"))
def update_leaderboard(stat):
    return create_type_leaderboard(df, stat)


@callback(
    Output("scatter-plot", "figure"),
    Input("x-axis-selector", "value"),
    Input("y-axis-selector", "value"),
)
def update_scatter(x, y):
    return create_scatter_plot(df, x, y)


@callback(
    Output("pokemon-image", "src"),
    Output("pokemon-name-display", "children"),
    Output("stat-progress-bars", "children"),
    Input("pokemon-selector", "value"),
)
def update_details(selected_pokemon):
    if not selected_pokemon:
        return "", "Select a Pokémon", []

    # Show detail for the first selected
    name = selected_pokemon[0]
    p_data = df[df["Name"] == name].iloc[0]

    progress_bars = []
    for stat in stat_options:
        val = p_data[stat]
        percent = (val / 160) * 100
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

    return p_data["Image_URL"], name, progress_bars


if __name__ == "__main__":
    app.run_server(debug=True, port=8050)
