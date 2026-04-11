import dash
from typing import Any, List
from pathlib import Path
from dash import callback, Input, Output, ctx, html, Patch
import dash_mantine_components as dmc
from dash_iconify import DashIconify
from loguru import logger
import time
import diskcache

from src.data import (
    evolution_map,
    STAT_OPTIONS,
    MAX_BASE_STAT,
    name_to_pokemon,
)
from data_manager import (
    OFFICIAL_ARTWORK_URL,
    SHINY_ARTWORK_URL,
    POKEAPI_CRY_URL,
    ensure_pokemon_cry,
)
from visualizations import create_type_badge

# Persistent cache for tracking Pokémon variants that lack audio files on the CDN
# This prevents repeated slow network attempts for confirmed missing cries.
cry_cache = diskcache.Cache(".cache/failed_cries")

# In-memory caches for the current session for UI-specific objects
_evolution_ui_cache: dict[str, Any] = {}


def _get_artwork_url(p_id: int, shiny: bool) -> str:
    """Return the local cached path if it exists, otherwise fall back to the CDN URL.

    This keeps the Dash server completely out of the download path — the browser
    fetches and caches the image from GitHub's CDN when no local copy exists.
    """

    suffix = "_shiny" if shiny else ""
    local_path = Path(f"assets/images/{p_id}{suffix}.png")
    if local_path.exists():
        return str(local_path)

    base_url = SHINY_ARTWORK_URL if shiny else OFFICIAL_ARTWORK_URL
    return f"{base_url}{p_id}.png"


@callback(
    Output("pokemon-name-display", "children"),
    Output("pokemon-types", "children"),
    Output("stat-progress-bars", "children"),
    Output("shiny-toggle", "style"),
    Output("shiny-toggle", "checked"),
    Output("trainer-comparison-display", "children"),
    Output("evolution-chain-display", "children"),
    Output("add-pokemon-btn", "disabled"),
    Output("pokemon-cry-audio", "src"),
    Output("play-cry-btn", "children"),
    Output("play-cry-btn", "disabled"),
    Input("focus-selector", "value"),
    Input("shiny-toggle", "checked"),
    Input("filter-store", "data"),
    Input("team-store", "data"),
)
def update_details(
    focus_name: str,
    is_shiny: bool,
    filter_store: dict,
    team: List[str],
) -> Any:
    """Update the detail card for the focused Pokémon using DuckDB/Arrow."""
    start_time = time.time()

    filters = (filter_store or {}).get("filters", {})
    toggles = (filter_store or {}).get("toggles", {})
    t_height = filters.get("trainer-height", 4.5)
    t_weight = filters.get("trainer-weight", 150)
    show_mega = toggles.get("mega-toggle", True)
    show_gmax = toggles.get("gmax-toggle", False)
    show_regional = toggles.get("regional-toggle", True)

    if not focus_name:
        logger.debug("No Pokémon selected, showing placeholder detail view.")
        return (
            "Select a Pokémon",
            [],
            [],
            {"display": "none"},
            False,
            "",
            "",
            True,
            "",
            DashIconify(icon="tabler:volume-off"),
            True,
        )

    triggered_id = ctx.triggered_id
    logger.debug(f"Updating detailed view. Triggered by: {triggered_id}")

    last_updated = (filter_store or {}).get("last_updated_id", "")
    if triggered_id == "filter-store" and last_updated in [
        "trainer-height",
        "trainer-weight",
    ]:
        try:
            t_height_f = float(t_height)
            t_weight_f = float(t_weight)
        except (ValueError, TypeError):
            return (dash.no_update,) * 11

        p_data = name_to_pokemon.get(focus_name)
        p_height = p_data["Height"] if p_data else 0
        p_weight = p_data["Weight"] if p_data else 0

        height_ratio = p_height / t_height_f if t_height_f > 0 else 1
        weight_ratio = p_weight / t_weight_f if t_weight_f > 0 else 1

        comparison_view = dmc.Stack(
            gap=4,
            children=[
                dmc.Text("Trainer Comparison", size="xs", fw=700, c="dimmed"),
                dmc.Group(
                    grow=True,
                    children=[
                        dmc.Stack(
                            gap=0,
                            children=[
                                dmc.Text(
                                    f"{f'{focus_name} is' if height_ratio > 1 else 'You are'} taller!",
                                    size="sm",
                                ),
                                dmc.Text(
                                    f"Ratio: {height_ratio:.1f}x", size="xs", c="dimmed"
                                ),
                            ],
                        ),
                        dmc.Stack(
                            gap=0,
                            children=[
                                dmc.Text(
                                    f"{f'{focus_name} is' if weight_ratio > 1 else 'You are'} heavier!",
                                    size="sm",
                                ),
                                dmc.Text(
                                    f"Ratio: {weight_ratio:.1f}x", size="xs", c="dimmed"
                                ),
                            ],
                        ),
                    ],
                ),
            ],
        )
        return (dash.no_update,) * 5 + (
            comparison_view,
            dash.no_update,
            dash.no_update,
            dash.no_update,
            dash.no_update,
            dash.no_update,
        )

    name = focus_name
    p_data = name_to_pokemon.get(name)
    if not p_data:
        return (
            "Select a Pokémon",
            [],
            [],
            {"display": "none"},
            False,
            "",
            "",
            True,
            "",
            DashIconify(icon="tabler:volume-off"),
            True,
        )

    # Use a cache key that includes filter toggles
    evo_cache_key = f"{p_data['Name']}_{show_mega}_{show_gmax}_{show_regional}"
    evolution_display = _evolution_ui_cache.get(evo_cache_key)

    if (
        not evolution_display
        and "Evolution_Chain_Members" in p_data
        and p_data["Evolution_Chain_Members"]
    ):
        members_list = p_data["Evolution_Chain_Members"].split(",")
        chain_items = []
        for member_species in members_list:
            member_forms = evolution_map.get(member_species, [])
            if not member_forms:
                continue
            base_form = min(member_forms, key=lambda x: x["id"])
            is_active = base_form["Species_Name"] == p_data["Species_Name"]
            border_style = "2px solid #5D9CEC" if is_active else "1px solid transparent"
            stage_children = [
                dmc.Tooltip(
                    label=base_form["Name"],
                    children=[
                        html.Div(
                            id={"type": "evo-link", "name": base_form["Name"]},
                            className="evolution-node",
                            n_clicks=0,
                            style={
                                "cursor": "pointer",
                                "border": border_style,
                                "borderRadius": "50%",
                                "padding": "4px",
                                "backgroundColor": "rgba(255, 255, 255, 0.05)",
                                "display": "flex",
                                "alignItems": "center",
                                "justifyContent": "center",
                            },
                            children=[
                                dmc.Image(
                                    src=base_form["Sprite_URL"],
                                    fallbackSrc="/assets/sprites/pokeball_placeholder.png",
                                    h=64,
                                    w="auto",
                                )
                            ],
                        )
                    ],
                )
            ]
            variants = [v for v in member_forms if v["id"] != base_form["id"]]
            if variants:
                variant_icons = []
                for v in variants:
                    if v.get("Is_Mega") and not show_mega:
                        continue
                    if v.get("Is_GMax") and not show_gmax:
                        continue
                    if v.get("Is_Regional") and not show_regional:
                        continue
                    variant_icons.append(
                        dmc.Tooltip(
                            label=v["Name"],
                            children=[
                                html.Div(
                                    id={"type": "evo-link", "name": v["Name"]},
                                    className="evolution-node",
                                    n_clicks=0,
                                    style={"cursor": "pointer"},
                                    children=[
                                        dmc.Image(
                                            src=v["Sprite_URL"],
                                            fallbackSrc="/assets/sprites/pokeball_placeholder.png",
                                            h=32,
                                            w="auto",
                                            style={"opacity": 0.8},
                                        )
                                    ],
                                )
                            ],
                        )
                    )
                if variant_icons:
                    stage_children.append(
                        dmc.Group(gap=2, children=variant_icons, justify="center")
                    )
            chain_items.append(
                dmc.Stack(gap=4, align="center", children=stage_children)
            )
        evolution_display = dmc.Group(gap="sm", justify="center", children=chain_items)
        _evolution_ui_cache[evo_cache_key] = evolution_display

    p_id, p_height, p_weight = int(p_data["id"]), p_data["Height"], p_data["Weight"]
    t_height_val = float(t_height)
    t_weight_val = float(t_weight)
    height_ratio = p_height / t_height_val if t_height_val > 0 else 1
    weight_ratio = p_weight / t_weight_val if t_weight_val > 0 else 1

    comparison_view = dmc.Stack(
        gap=4,
        children=[
            dmc.Text("Trainer Comparison", size="xs", fw=700, c="dimmed"),
            dmc.Group(
                grow=True,
                children=[
                    dmc.Stack(
                        gap=0,
                        children=[
                            dmc.Text(
                                f"{f'{name} is' if height_ratio > 1 else 'You are'} taller!",
                                size="sm",
                            ),
                            dmc.Text(
                                f"Ratio: {height_ratio:.1f}x", size="xs", c="dimmed"
                            ),
                        ],
                    ),
                    dmc.Stack(
                        gap=0,
                        children=[
                            dmc.Text(
                                f"{f'{name} is' if weight_ratio > 1 else 'You are'} heavier!",
                                size="sm",
                            ),
                            dmc.Text(
                                f"Ratio: {weight_ratio:.1f}x", size="xs", c="dimmed"
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )

    shiny_exists = bool(p_data.get("Has_Shiny", False))
    toggle_style = {"display": "block"} if shiny_exists else {"display": "none"}
    current_shiny = is_shiny if shiny_exists else False

    progress_bars = []
    for stat in STAT_OPTIONS:
        val = p_data[stat]
        percent = (val / MAX_BASE_STAT) * 100
        color = "red" if val < 60 else "yellow" if val < 90 else "green"
        progress_bars.append(
            html.Div(
                [
                    dmc.Group(
                        justify="space-between",
                        children=[
                            dmc.Text(stat, size="sm", fw=500),
                            dmc.Text(str(val), size="sm", fw=700, c=color),
                        ],
                    ),
                    dmc.Progress(value=percent, color=color, mb="xs"),
                ]
            )
        )

    types = [p_data["Primary Type"]]
    if p_data["Secondary Type"] != "None":
        types.append(p_data["Secondary Type"])

    add_disabled = name in team or len(team) >= 6

    # Audio Logic: On-demand download with persistent failure caching
    p_id_int = int(p_id)

    # 1. Check persistent failure cache first
    if p_id_int in cry_cache:
        has_cry = False
        cry_src = ""
    else:
        # 2. Check local file or attempt download
        local_path_str = ensure_pokemon_cry(p_id_int, name)
        if local_path_str:
            has_cry = True
            # Use the CDN URL for the browser (better for production/caching)
            cry_src = f"{POKEAPI_CRY_URL}{p_id_int}.ogg"
        else:
            # 3. Mark as persistent failure if download failed (404/Timeout)
            cry_cache.set(p_id_int, True)
            has_cry = False
            cry_src = ""

    cry_icon = (
        DashIconify(icon="tabler:volume")
        if has_cry
        else DashIconify(icon="tabler:volume-off")
    )

    end_time = time.time()
    logger.debug(f"Update details duration: {end_time - start_time}")

    # Patch for types list
    patch_types = Patch()
    patch_types.clear()
    for t in types:
        patch_types.append(create_type_badge(t))

    # Patch for progress bars
    patch_stats = Patch()
    patch_stats.clear()
    for bar in progress_bars:
        patch_stats.append(bar)

    return (
        name,
        patch_types,
        patch_stats,
        toggle_style,
        current_shiny,
        comparison_view,
        evolution_display,
        add_disabled,
        cry_src,
        cry_icon,
        not has_cry,
    )


@callback(
    Output("pokemon-image", "src"),
    Input("focus-selector", "value"),
    Input("shiny-toggle", "checked"),
)
def update_pokemon_image(focus_name: str, is_shiny: bool) -> str | dash.NoUpdate:
    """Async callback to load the high-res Pokémon artwork."""
    if not focus_name:
        return ""

    triggered_id = ctx.triggered_id
    logger.debug(f"Updating Pokémon image. Triggered by: {triggered_id}")

    p_data = name_to_pokemon.get(focus_name)
    if not p_data:
        return ""

    p_id = int(p_data["id"])

    # If it's a shiny toggle, check if shiny artwork exists first
    if triggered_id == "shiny-toggle":
        if not bool(p_data.get("Has_Shiny", False)):
            return dash.no_update

    return _get_artwork_url(p_id, shiny=is_shiny)


dash.clientside_callback(
    """
    function(loading) {
        return !!(loading && loading.is_loading);
    }
    """,
    Output("image-loading-overlay", "visible"),
    Input("pokemon-image", "loading_state"),
)


dash.clientside_callback(
    """
    function(n_clicks) {
        return window.dash_clientside.clientside.playPokemonCry(n_clicks);
    }
    """,
    Output("play-cry-btn", "id"),
    Input("play-cry-btn", "n_clicks"),
)
