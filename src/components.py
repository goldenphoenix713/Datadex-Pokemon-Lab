"""UI components and cards for the Data-Dex application."""

import dash_mantine_components as dmc
from dash import dcc, html
from src.data import pokemon_sprites
from src.constants import STAT_OPTIONS

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
                dmc.Group(
                    justify="space-between",
                    children=[
                        dmc.Title(
                            "Face-Off Radar",
                            order=2,
                            className="pokemon-section-title",
                        ),
                        dmc.Button(
                            "Clear Team",
                            id="clear-team-btn",
                            variant="subtle",
                            color="gray",
                            leftSection=html.I(className="fas fa-trash"),
                        ),
                    ],
                    mb="md",
                ),
                dmc.Text(
                    "Compare your team's stats side-by-side.",
                    c="dimmed",
                    mb="md",
                ),
                # Dynamic Team List Container
                dmc.ScrollArea(
                    h=120,
                    offsetScrollbars=True,
                    children=[
                        dmc.Group(
                            id="team-list",
                            gap="xs",
                            children=[
                                dmc.Text(
                                    "No Pokémon in your team yet. Add some from the Detail view!",
                                    c="dimmed",
                                    size="sm",
                                    fs="italic",
                                )
                            ],
                        )
                    ],
                    mb="xl",
                ),
                dcc.Graph(
                    id="radar-chart",
                    config={"displayModeBar": False},
                    style={"height": "500px"},
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
                dmc.Select(
                    id="focus-selector",
                    label="Viewing Details For:",
                    placeholder="Select Pokémon",
                    value="Bulbasaur",
                    mb="sm",
                    style={"display": "block"},
                    renderOption={
                        "function": "renderPokemonOption",
                        "options": {"sprites": pokemon_sprites},
                    },
                    searchable=True,
                ),
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
                dmc.Space(h="md"),
                dmc.Button(
                    "Add to Team",
                    id="add-pokemon-btn",
                    fullWidth=True,
                    size="lg",
                    radius="md",
                    leftSection=html.I(className="fas fa-plus"),
                    mb="md",
                    disabled=True,  # Default to disabled if no selection
                ),
                dmc.Divider(my="md"),
                dmc.Text("Evolution Lineage", size="sm", fw=700, mb="sm"),
                html.Div(id="evolution-chain-display"),
                dmc.Divider(my="md"),
                html.Div(id="trainer-comparison-display"),
            ],
        ),
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
                    data=STAT_OPTIONS,
                    value="Attack",
                    mb="md",
                ),
                dcc.Graph(
                    id="leaderboard-chart",
                    config={"displayModeBar": False},
                ),
            ],
        ),
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
                            data=STAT_OPTIONS + ["Height", "Weight"],
                            value="Weight",
                        ),
                        dmc.Select(
                            id="y-axis-selector",
                            label="Vertical (Y)",
                            data=STAT_OPTIONS + ["Height", "Weight"],
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
        ),
    ],
)
