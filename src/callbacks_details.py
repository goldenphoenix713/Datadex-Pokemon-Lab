import dash
from typing import Any, List
from dash import callback, Input, Output, ctx, html
import dash_mantine_components as dmc
from loguru import logger

from src.data import evolution_map
from src.constants import STAT_OPTIONS
from data_manager import ensure_pokemon_image, has_shiny_artwork, ensure_pokemon_sprite
from visualizations import create_type_badge


@callback(
    Output("pokemon-image", "src"),
    Output("pokemon-name-display", "children"),
    Output("pokemon-types", "children"),
    Output("stat-progress-bars", "children"),
    Output("shiny-toggle", "style"),
    Output("shiny-toggle", "checked"),
    Output("trainer-comparison-display", "children"),
    Output("evolution-chain-display", "children"),
    Output("add-pokemon-btn", "disabled"),
    Input("focus-selector", "value"),
    Input("shiny-toggle", "checked"),
    Input("trainer-height", "value"),
    Input("trainer-weight", "value"),
    Input("mega-toggle", "checked"),
    Input("gmax-toggle", "checked"),
    Input("regional-toggle", "checked"),
    Input("team-store", "data"),
)
def update_details(
    focus_name: str,
    is_shiny: bool,
    t_height: float | str,
    t_weight: float | str,
    show_mega: bool,
    show_gmax: bool,
    show_regional: bool,
    team: List[str],
) -> Any:
    """Update the detail card for the focused Pokémon using DuckDB/Arrow."""
    if not focus_name:
        logger.debug("No Pokémon selected, showing placeholder detail view.")
        return (
            "",
            "Select a Pokémon",
            [],
            [],
            {"display": "none"},
            False,
            "",
            "",
            True,
        )

    triggered_id = ctx.triggered_id
    logger.debug(f"Updating detailed view. Triggered by: {triggered_id}")

    if triggered_id in ["trainer-height", "trainer-weight"]:
        from src.data import conn, db_lock

        with db_lock:
            row = conn.execute(
                f'SELECT "Height" FROM pokemon WHERE "Name" = \'{focus_name}\''
            ).fetchone()

        p_height = row[0] if row else 0
        t_height_f = float(t_height)
        height_ratio = p_height / t_height_f if t_height_f > 0 else 1
        comparison_view = dmc.Stack(
            gap=4,
            children=[
                dmc.Text("Trainer Comparison", size="xs", fw=700, c="dimmed"),
                dmc.Text(
                    f"{f'{focus_name} is' if height_ratio > 1 else 'You are'} taller!",
                    size="sm",
                ),
                dmc.Text(f"Ratio: {height_ratio:.1f}x", size="sm"),
            ],
        )
        return (dash.no_update,) * 6 + (comparison_view, dash.no_update, dash.no_update)

    if triggered_id == "shiny-toggle":
        from src.data import conn, db_lock

        with db_lock:
            row = conn.execute(
                f"SELECT id FROM pokemon WHERE \"Name\" = '{focus_name}'"
            ).fetchone()

        p_id = row[0] if row else 0
        image_src = ensure_pokemon_image(int(p_id), focus_name, shiny=is_shiny)
        return (
            image_src,
            dash.no_update,
            dash.no_update,
            dash.no_update,
            dash.no_update,
            is_shiny,
            dash.no_update,
            dash.no_update,
            dash.no_update,
        )

    name = focus_name
    from src.data import conn, db_lock

    try:
        with db_lock:
            p_data = (
                conn.execute(f"SELECT * FROM pokemon WHERE \"Name\" = '{name}'")
                .to_arrow_table()
                .to_pylist()[0]
            )
    except (IndexError, KeyError):
        return "", "Select a Pokémon", [], [], {"display": "none"}, False, "", "", True

    evolution_display = []
    if "Evolution_Chain_Members" in p_data and p_data["Evolution_Chain_Members"]:
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
                                    src=ensure_pokemon_sprite(
                                        base_form["id"], base_form["Name"]
                                    ),
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
                                            src=ensure_pokemon_sprite(
                                                v["id"], v["Name"]
                                            ),
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

    p_id, p_height = int(p_data["id"]), p_data["Height"]
    t_height_val = float(t_height)
    height_ratio = p_height / t_height_val if t_height_val > 0 else 1
    comparison_view = dmc.Stack(
        gap=4,
        children=[
            dmc.Text("Trainer Comparison", size="xs", fw=700, c="dimmed"),
            dmc.Text(
                f"{f'{name} is' if height_ratio > 1 else 'You are'} taller!",
                size="sm",
            ),
            dmc.Text(f"Ratio: {height_ratio:.1f}x", size="sm"),
        ],
    )

    shiny_exists = has_shiny_artwork(p_id)
    toggle_style = {"display": "block"} if shiny_exists else {"display": "none"}
    current_shiny = is_shiny if shiny_exists else False

    from src.data import MAX_BASE_STAT

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

    return (
        ensure_pokemon_image(p_id, name, shiny=current_shiny),
        name,
        [create_type_badge(t) for t in types],
        progress_bars,
        toggle_style,
        current_shiny,
        comparison_view,
        evolution_display,
        add_disabled,
    )
