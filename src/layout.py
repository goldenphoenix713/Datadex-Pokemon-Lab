"""Main layout assembly for the Data-Dex application."""

import dash_mantine_components as dmc
from dash import html
from src.constants import CUSTOM_THEME, REGIONS, TYPES, STAT_OPTIONS
from src.components import (
    radar_card,
    pokemon_detail_card,
    type_leaderboard_card,
    world_exploration_card,
)

layout = dmc.MantineProvider(
    theme=CUSTOM_THEME,
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
                    style={"overflowY": "auto"},
                    children=[
                        dmc.Title("Filters", order=4, mb="md"),
                        dmc.MultiSelect(
                            id="region-filter",
                            label="Regions",
                            placeholder="Select Regions",
                            data=REGIONS,
                            value=[],
                            mb="md",
                        ),
                        dmc.MultiSelect(
                            id="type-filter",
                            label="Types",
                            placeholder="Select Types",
                            data=TYPES,
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
                        dmc.Divider(my="md"),
                        dmc.Title("Stat Ranges", order=4, mb="md"),
                        html.Div(
                            children=[
                                html.Div(
                                    [
                                        dmc.Text(f"{stat} Range", size="sm", mb=5),
                                        dmc.RangeSlider(
                                            id={"type": "stat", "name": stat},
                                            value=[0, 255],
                                            min=0,
                                            max=255,
                                            step=1,
                                            marks=[
                                                {"value": 0, "label": "0"},
                                                {"value": 128, "label": "128"},
                                                {"value": 255, "label": "255"},
                                            ],
                                            mb="xl",
                                        ),
                                    ]
                                )
                                for stat in STAT_OPTIONS
                            ]
                        ),
                        dmc.Divider(my="md"),
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
                                    checked=True,
                                ),
                            ],
                        ),
                        dmc.Divider(my="md"),
                        dmc.Title("Trainer Comparison", order=4, mb="md"),
                        dmc.Group(
                            grow=True,
                            children=[
                                dmc.NumberInput(
                                    id="trainer-height",
                                    label="Your Height (ft)",
                                    value=4.5,
                                    min=2,
                                    max=7,
                                    step=0.01,
                                ),
                                dmc.NumberInput(
                                    id="trainer-weight",
                                    label="Your Weight (lbs)",
                                    value=150,
                                    min=10,
                                    max=200,
                                    step=1,
                                ),
                            ],
                            mb="md",
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
