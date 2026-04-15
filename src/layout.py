"""Main layout assembly for the Data-Dex application."""

import dash_mantine_components as dmc
from dash import dcc, html, Output, Input, clientside_callback
from src.filters import create_filter_stack, FILTER_STORE_DEFAULTS
from src.constants import CUSTOM_THEME, STAT_OPTIONS
from src.components import (
    radar_card,
    pokemon_detail_card,
    type_leaderboard_card,
    world_exploration_card,
    trainer_comparison_card,
)
from src.data import pokemon_ids, pokemon_sprites, pokemon_table

layout = dmc.MantineProvider(
    theme=CUSTOM_THEME,
    forceColorScheme="dark",
    children=[
        dcc.Store(id="current-pokemon-data", data={}, storage_type="memory"),
        dcc.Store(id="team-store", data=[], storage_type="session"),
        dcc.Store(id="pokemon-id-map", data=pokemon_ids, storage_type="memory"),
        dcc.Store(id="pokemon-sprite-map", data=pokemon_sprites, storage_type="memory"),
        dcc.Store(
            id="full-pokemon-data",
            data=pokemon_table.to_pylist(),
            storage_type="memory",
        ),
        dcc.Store(id="stats-names-store", data=STAT_OPTIONS, storage_type="memory"),
        dcc.Store(id="filter-store", data=FILTER_STORE_DEFAULTS, storage_type="memory"),
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
                        dmc.Box(
                            pos="relative",
                            h="100%",
                            children=[
                                dmc.Burger(
                                    id="drawer-burger",
                                    opened=False,
                                    hiddenFrom="sm",
                                    size="sm",
                                    pos="absolute",
                                    left="md",
                                    top="50%",
                                    style={
                                        "transform": "translateY(-50%)",
                                        "zIndex": 100,
                                    },
                                ),
                                dmc.Center(
                                    h="100%",
                                    children=[
                                        html.H1(
                                            "Data-Dex: Ultimate Stat Lab",
                                            className="pokemon-title",
                                            style={"margin": 0},
                                        )
                                    ],
                                ),
                            ],
                        )
                    ]
                ),
                dmc.AppShellNavbar(
                    children=[
                        dmc.ScrollArea(
                            h="100%",
                            offsetScrollbars=True,
                            children=[create_filter_stack("navbar")],
                        )
                    ]
                ),
                dmc.AppShellMain(
                    children=[
                        dmc.Container(
                            size="xl",
                            children=[
                                dmc.Grid(
                                    gutter="lg",
                                    children=[
                                        pokemon_detail_card,
                                        dmc.GridCol(
                                            span={"base": 12, "md": 8},
                                            children=[
                                                dmc.Stack(
                                                    gap="lg",
                                                    children=[
                                                        radar_card,
                                                        trainer_comparison_card,
                                                    ],
                                                )
                                            ],
                                        ),
                                        type_leaderboard_card,
                                        world_exploration_card,
                                    ],
                                ),
                            ],
                        ),
                        dmc.Drawer(
                            id="filter-drawer",
                            title="Filters",
                            opened=False,
                            children=[
                                dmc.ScrollArea(
                                    h="calc(100vh - 80px)",
                                    offsetScrollbars=True,
                                    children=[create_filter_stack("drawer")],
                                )
                            ],
                        ),
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
                                    "Pokémon and Pokémon character names are trademarks of Nintendo.\n"
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
        ),
    ],
)

clientside_callback(
    """
    function(burger_opened, drawer_opened) {
        const ctx = window.dash_clientside.callback_context;
        if (!ctx.triggered || ctx.triggered.length === 0) {
            return [window.dash_clientside.no_update, window.dash_clientside.no_update];
        }
        const trigger = ctx.triggered[0].prop_id;
        if (trigger.includes("drawer-burger")) {
            return [burger_opened, burger_opened];
        }
        if (trigger.includes("filter-drawer")) {
            return [drawer_opened, drawer_opened];
        }
        return [window.dash_clientside.no_update, window.dash_clientside.no_update];
    }
    """,
    Output("drawer-burger", "opened"),
    Output("filter-drawer", "opened"),
    Input("drawer-burger", "opened"),
    Input("filter-drawer", "opened"),
)
