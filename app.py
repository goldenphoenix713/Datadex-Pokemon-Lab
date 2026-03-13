"""Main entry point for the Data-Dex Dash application.

This module initializes the Dash app, defines the layout using dash-mantine-components,
and handles interactivity via Dash callbacks.
"""

from loguru import logger
import sys
from typing import Any, List, Tuple
from dash import callback, Input, Output
import dash
import dash_mantine_components as dmc
from dash import dcc, html
import pandas as pd

logger.remove()
logger.add("logs/app.log", level="DEBUG")
logger.add(sys.stderr, level="DEBUG")

from data_manager import (  # noqa: E402
    load_and_clean_data,
    ensure_pokemon_image,
    has_shiny_artwork,
)  # noqa: E402
from visualizations import (  # noqa: E402
    create_scatter_plot,
    create_radar_chart,
    create_type_badge,
    create_type_leaderboard,
)


logger.info("Data-Dex Dash application starting...")

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

# Left Column: User Selection and Radar Comparison
radar_card = dmc.GridCol(
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
                dmc.Text("Choose your Pokémon Team", size="sm", fw=500, mb=4),
                dcc.Dropdown(
                    id="pokemon-selector",
                    placeholder="Search names...",
                    options=[{"label": n, "value": n} for n in pokemon_names],
                    value=["Bulbasaur", "Charmander"],
                    multi=True,
                    clearable=True,
                    className="custom-dropdown",
                ),
                dmc.Space(h="xl"),
                dcc.Graph(
                    id="radar-chart",
                    config={"displayModeBar": False},
                ),
            ],
        ),
    ],
)

# Right Column: Detail Card for the selected Pokémon
pokemon_detail_card = dmc.GridCol(
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
                            className="pokemon-artwork",
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
                dmc.Center(
                    children=[
                        dmc.Switch(
                            id="shiny-toggle",
                            label="Shiny Mode",
                            checked=False,
                            mb="md",
                            style={"display": "none"},  # Hidden by default
                        )
                    ]
                ),
                # Container for dynamic progress bars
                html.Div(id="stat-progress-bars"),
            ],
        )
    ],
)

# Bottom Row: Global analysis components
type_leaderboard_card = dmc.GridCol(
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
)

# World exploration card (stats scatter plot)
world_exploration_card = dmc.GridCol(
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
                            data=stat_options + ["Height", "Weight"],
                            value="Weight",
                        ),
                        dmc.Select(
                            id="y-axis-selector",
                            label="Vertical (Y)",
                            data=stat_options + ["Height", "Weight"],
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
)

# Application Layout
app.layout = dmc.MantineProvider(
    theme=custom_theme,
    forceColorScheme="dark",
    children=[
        dmc.AppShell(
            header={"height": 100},
            navbar={
                "width": 300,
                "breakpoint": "sm",
                "collapsed": {"mobile": True},
            },
            footer={"height": 60},
            padding="md",
            children=[
                dmc.AppShellHeader(
                    children=[
                        dmc.Center(
                            style={"height": "100%"},
                            children=[
                                html.H1(
                                    "Data-Dex: Ultimate Stat Lab",
                                    className="pokemon-title",
                                    style={"margin": 0},
                                )
                            ],
                        )
                    ]
                ),
                dmc.AppShellNavbar(
                    p="md",
                    children=[
                        dmc.Title("Filters", order=4, mb="md"),
                        dmc.MultiSelect(
                            id="region-filter",
                            label="Regions",
                            placeholder="Select Regions",
                            data=[
                                "Kanto",
                                "Johto",
                                "Hoenn",
                                "Sinnoh",
                                "Unova",
                                "Kalos",
                                "Alola",
                                "Galar",
                                "Paldea",
                            ],
                            value=[],
                            mb="md",
                        ),
                        dmc.MultiSelect(
                            id="type-filter",
                            label="Types",
                            placeholder="Select Types",
                            data=[
                                "Bug",
                                "Dark",
                                "Dragon",
                                "Electric",
                                "Fairy",
                                "Fighting",
                                "Fire",
                                "Flying",
                                "Ghost",
                                "Grass",
                                "Ground",
                                "Ice",
                                "Normal",
                                "Poison",
                                "Psychic",
                                "Rock",
                                "Steel",
                                "Water",
                            ],
                            value=[],
                            mb="md",
                        ),
                        dmc.Select(
                            id="sort-order",
                            label="Sort By",
                            data=[
                                {"label": "Pokédex Number", "value": "number"},
                                {"label": "Name", "value": "name"},
                            ],
                            value="name",
                            mb="md",
                        ),
                        dmc.Stack(
                            gap="xs",
                            children=[
                                dmc.Switch(
                                    id="mega-toggle",
                                    label="Show Mega evolutions",
                                    checked=True,
                                ),
                                dmc.Switch(
                                    id="regional-toggle",
                                    label="Show Regional forms",
                                    checked=True,
                                ),
                                dmc.Switch(
                                    id="final-evolution-toggle",
                                    label="Final Evolutions Only",
                                    checked=False,
                                ),
                                dmc.Switch(
                                    id="legendary-toggle",
                                    label="Include Legendaries",
                                    checked=True,
                                ),
                                dmc.Switch(
                                    id="mythical-toggle",
                                    label="Include Mythicals",
                                    checked=True,
                                ),
                                dmc.Switch(
                                    id="gmax-toggle",
                                    label="Show G-Max forms",
                                    checked=False,
                                ),
                            ],
                        ),
                        dmc.Divider(my="md"),
                        dmc.Text("Selection Helper", size="xs", c="dimmed", mb="xs"),
                        dmc.Text(
                            "Use these filters to narrow down the list of Pokémon in the team selector.",
                            size="xs",
                            c="dimmed",
                        ),
                    ],
                ),
                dmc.AppShellMain(
                    children=[
                        dmc.Container(
                            size="xl",
                            children=[
                                dmc.Grid(
                                    gutter="lg",
                                    children=[
                                        radar_card,
                                        pokemon_detail_card,
                                        type_leaderboard_card,
                                        world_exploration_card,
                                    ],
                                ),
                            ],
                        )
                    ]
                ),
                dmc.AppShellFooter(
                    p="xs",
                    children=[
                        dmc.Stack(
                            gap=0,
                            align="center",
                            children=[
                                dmc.Text(
                                    "© 2026 Pokémon. © 1995–2026 Nintendo/Creatures Inc./GAME FREAK inc. "
                                    "Pokémon and Pokémon character names are trademarks of Nintendo. "
                                    "This project is not affiliated with or endorsed by The Pokémon Company or Nintendo.",
                                    size="xs",
                                    c="dimmed",
                                    ta="center",
                                ),
                                dmc.Text(
                                    "Data & Images: Attributed to PokéAPI (pokeapi.co).",
                                    size="xs",
                                    c="dimmed",
                                    ta="center",
                                ),
                            ],
                        )
                    ],
                ),
            ],
        )
    ],
)


# Interactivity: Callbacks to update visuals based on user input
def get_filtered_df(
    regions: List[str],
    show_mega: bool,
    show_regional: bool,
    final_only: bool,
    show_legendary: bool,
    show_mythical: bool,
    show_gmax: bool,
    selected_types: List[str],
) -> pd.DataFrame:
    """Centralized filtering logic for all visualizations."""
    filtered_df = df.copy()

    if regions:
        filtered_df = filtered_df[filtered_df["Region"].isin(regions)]

    if not show_mega:
        filtered_df = filtered_df[~filtered_df["Is_Mega"]]

    if not show_regional:
        filtered_df = filtered_df[~filtered_df["Is_Regional"]]

    if final_only:
        filtered_df = filtered_df[filtered_df["Is_Final_Evolution"]]

    if not show_legendary:
        filtered_df = filtered_df[~filtered_df["Is_Legendary"]]

    if not show_mythical:
        filtered_df = filtered_df[~filtered_df["Is_Mythical"]]

    if not show_gmax:
        filtered_df = filtered_df[~filtered_df["Is_GMax"]]

    if selected_types:
        filtered_df = filtered_df[
            (filtered_df["Primary Type"].isin(selected_types))
            | (filtered_df["Secondary Type"].isin(selected_types))
        ]

    return filtered_df


@callback(
    Output("pokemon-selector", "options"),
    Input("region-filter", "value"),
    Input("mega-toggle", "checked"),
    Input("regional-toggle", "checked"),
    Input("final-evolution-toggle", "checked"),
    Input("legendary-toggle", "checked"),
    Input("mythical-toggle", "checked"),
    Input("gmax-toggle", "checked"),
    Input("type-filter", "value"),
    Input("sort-order", "value"),
)
def update_selector_options(
    regions: List[str],
    show_mega: bool,
    show_regional: bool,
    final_only: bool,
    show_legendary: bool,
    show_mythical: bool,
    show_gmax: bool,
    selected_types: List[str],
    sort_by: str,
) -> List[dict]:
    """Filter the list of available Pokémon names for the selector."""
    filtered_df = get_filtered_df(
        regions,
        show_mega,
        show_regional,
        final_only,
        show_legendary,
        show_mythical,
        show_gmax,
        selected_types,
    )

    # Return options with labels and sprite icons
    options = []
    for _, row in filtered_df.iterrows():
        options.append(
            {
                "label": html.Div(
                    [
                        html.Img(
                            src=row["Sprite_URL"],
                            style={
                                "height": "24px",
                                "marginRight": "10px",
                                "pointerEvents": "none",
                            },
                            className="pokemon-sprite",
                        ),
                        html.Span(row["Name"]),
                    ],
                    style={"display": "flex", "alignItems": "center"},
                ),
                "value": row["Name"],
                "number": row["#"],  # Keep internal ID for sorting
                "nat_dex": row["National_Dex"],  # For grouping
            }
        )

    if sort_by == "number":
        sorted_options = sorted(options, key=lambda x: (x["nat_dex"], x["number"]))
    else:
        sorted_options = sorted(options, key=lambda x: str(x["value"]))

    # Return clean options list
    return [{"label": opt["label"], "value": opt["value"]} for opt in sorted_options]


@callback(Output("radar-chart", "figure"), Input("pokemon-selector", "value"))
def update_radar(selected_pokemon: List[str]) -> Any:
    """Update the radar chart based on selected Pokémon."""
    logger.debug(f"Updating radar chart for: {selected_pokemon}")
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
    Input("type-filter", "value"),
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
    selected_types: List[str],
) -> Any:
    """Update the type leaderboard based on a selected stat and filters."""
    logger.debug(f"Updating leaderboard for stat: {stat}")
    filtered_df = get_filtered_df(
        regions,
        show_mega,
        show_regional,
        final_only,
        show_legendary,
        show_mythical,
        show_gmax,
        selected_types,
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
    Input("type-filter", "value"),
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
    selected_types: List[str],
) -> Any:
    """Update the scatter plot visualization for exploring outliers with filters."""
    logger.debug(f"Updating scatter plot: x={x}, y={y}")
    filtered_df = get_filtered_df(
        regions,
        show_mega,
        show_regional,
        final_only,
        show_legendary,
        show_mythical,
        show_gmax,
        selected_types,
    )
    return create_scatter_plot(filtered_df, x, y)


@callback(
    Output("pokemon-image", "src"),
    Output("pokemon-name-display", "children"),
    Output("pokemon-types", "children"),
    Output("stat-progress-bars", "children"),
    Output("shiny-toggle", "style"),
    Output("shiny-toggle", "checked"),
    Input("pokemon-selector", "value"),
    Input("shiny-toggle", "checked"),
)
def update_details(
    selected_pokemon: List[str], is_shiny: bool
) -> Tuple[str, str, List[Any], List[Any], dict, bool]:
    """Update the detail card for the primary selected Pokémon."""
    if not selected_pokemon:
        logger.debug("No Pokémon selected, showing placeholder detail view.")
        return "", "Select a Pokémon", [], [], {"display": "none"}, False

    name = selected_pokemon[0]
    logger.debug(f"Updating detailed view for focus: {name}")
    p_data = df[df["Name"] == name].iloc[0]
    p_id = int(p_data["#"])

    # Check for shiny availability to show/hide toggle
    shiny_exists = has_shiny_artwork(p_id)
    toggle_style = {"display": "block"} if shiny_exists else {"display": "none"}
    # Reset shiny toggle if it doesn't exist for this mon
    current_shiny = is_shiny if shiny_exists else False

    max_stat = df[stat_options].max().max()

    progress_bars = []
    for stat in stat_options:
        val = p_data[stat]
        percent = (val / max_stat) * 100

        # Determine color based on value
        if val < 60:
            color = "red"
        elif val < 90:
            color = "yellow"
        else:
            color = "green"

        progress_bars.append(
            html.Div(
                [
                    dmc.Group(
                        justify="apart",
                        children=[
                            dmc.Text(stat, size="sm", fw=500),
                            dmc.Text(str(val), size="sm", fw=700, c=color),
                        ],
                    ),
                    dmc.Progress(
                        value=percent,
                        color=color,
                        mb="xs",
                        animated=True,
                    ),
                ]
            )
        )

    types = [p_data["Primary Type"]]
    if p_data["Secondary Type"] != "None":
        types.append(p_data["Secondary Type"])

    type_badges = [create_type_badge(t) for t in types]
    image_src = ensure_pokemon_image(p_id, name, shiny=current_shiny)

    return (
        image_src,
        name,
        type_badges,
        progress_bars,
        toggle_style,
        current_shiny,
    )


if __name__ == "__main__":
    # Start the server (debug=True enables hot reloading)
    app.run_server(debug=True, port=8050, use_reloader=False)
