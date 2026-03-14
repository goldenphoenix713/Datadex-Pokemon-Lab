"""Callback definitions for the Data-Dex application."""

from typing import Any, List, Tuple
from dash import callback, Input, Output, State, ALL, ctx, html, Patch
import dash_mantine_components as dmc
from loguru import logger

from src.data import df
from src.constants import STAT_OPTIONS
from src.utils import get_filtered_df
from data_manager import ensure_pokemon_image, has_shiny_artwork
from visualizations import (
    create_scatter_plot,
    create_radar_chart,
    create_type_badge,
    create_type_leaderboard,
)

# TODO Instead of recreating the figures, update the existing ones using dash.Patch


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
    Input({"type": "stat", "name": ALL}, "value"),
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
    stat_values: List[List[int]],
) -> List[dict]:
    """Filter the list of available Pokémon names for the selector."""
    # Build stat_ranges dict from ALL input using context
    stat_ranges = {
        item["id"]["name"]: item["value"]
        for item in ctx.inputs_list
        if isinstance(item, list)
        for item in item
        if isinstance(item["id"], dict) and item["id"].get("type") == "stat"
    }

    # Identify which filter triggered the callback
    triggered_id = ctx.triggered_id
    if isinstance(triggered_id, dict) and triggered_id.get("type") == "stat":
        logger.debug(
            f"Selector update triggered by stat filter: {triggered_id['name']}"
        )

    filtered_df = get_filtered_df(
        regions,
        show_mega,
        show_regional,
        final_only,
        show_legendary,
        show_mythical,
        show_gmax,
        selected_types,
        stat_ranges,
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
    Input({"type": "stat", "name": ALL}, "value"),
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
    stat_values: List[List[int]],
) -> Any:
    """Update the type leaderboard based on a selected stat and filters."""
    # Build stat_ranges dict from ALL input using context
    stat_ranges = {
        item["id"]["name"]: item["value"]
        for item in ctx.inputs_list
        if isinstance(item, list)
        for item in item
        if isinstance(item["id"], dict) and item["id"].get("type") == "stat"
    }

    # Identify which filter triggered the callback
    triggered_id = ctx.triggered_id
    if isinstance(triggered_id, dict) and triggered_id.get("type") == "stat":
        logger.debug(
            f"Leaderboard update triggered by stat filter: {triggered_id['name']}"
        )

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
        stat_ranges,
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
    Input({"type": "stat", "name": ALL}, "value"),
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
    stat_values: List[List[int]],
) -> Any:
    """Update the scatter plot visualization for exploring outliers with filters."""
    # Build stat_ranges dict from ALL input using context
    stat_ranges = {
        item["id"]["name"]: item["value"]
        for item in ctx.inputs_list
        if isinstance(item, list)
        for item in item
        if isinstance(item["id"], dict) and item["id"].get("type") == "stat"
    }

    # Identify which filter triggered the callback
    triggered_id = ctx.triggered_id
    if isinstance(triggered_id, dict) and triggered_id.get("type") == "stat":
        logger.debug(
            f"Scatter plot update triggered by stat filter: {triggered_id['name']}"
        )

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
        stat_ranges,
    )
    return create_scatter_plot(filtered_df, x, y)


@callback(
    Output("focus-selector", "data"),
    Output("focus-selector", "value"),
    Output("focus-selector", "style"),
    Output("focus-selector", "key"),
    Output("pokemon-selector", "value"),
    Input("pokemon-selector", "value"),
    Input({"type": "evo-link", "name": ALL}, "n_clicks"),
    Input("mega-toggle", "checked"),
    Input("gmax-toggle", "checked"),
    Input("regional-toggle", "checked"),
    Input("final-evolution-toggle", "checked"),
    Input("legendary-toggle", "checked"),
    Input("mythical-toggle", "checked"),
    State("focus-selector", "value"),
    prevent_initial_call=True,
)
def manage_focus_selection(
    selected_pokemon: List[str],
    evo_clicks: List[int],
    show_mega: bool,
    show_gmax: bool,
    show_regional: bool,
    final_only: bool,
    show_legendary: bool,
    show_mythical: bool,
    current_focus: str,
) -> Tuple[List[str], str, dict, str, List[str]]:
    """Sync the focus selector with the multi-selector, evolution links, and filter toggles."""
    triggered_id = ctx.triggered_id

    # Add safety check for first load or empty selection
    if selected_pokemon is None:
        selected_pokemon = []

    # Filter selected Pokémon based on current toggle states
    valid_selection = []
    for p_name in selected_pokemon:
        try:
            p_match = df[df["Name"] == p_name]
            if p_match.empty:
                continue
            p_row = p_match.iloc[0]

            if p_row["Is_Mega"] and not show_mega:
                continue
            if p_row["Is_GMax"] and not show_gmax:
                continue
            if p_row["Is_Regional"] and not show_regional:
                continue
            if final_only and not p_row["Is_Final_Evolution"]:
                continue
            if p_row["Is_Legendary"] and not show_legendary:
                continue
            if p_row["Is_Mythical"] and not show_mythical:
                continue

            valid_selection.append(p_name)
        except (IndexError, KeyError):
            continue

    # Determine new focus value
    if (
        triggered_id == "pokemon-selector"
        and valid_selection
        and (not current_focus or valid_selection[-1] != current_focus)
    ):
        new_focus = valid_selection[-1]
    elif (
        isinstance(triggered_id, dict)
        and triggered_id.get("type") == "evo-link"
        and any(click for click in evo_clicks if click)
    ):
        new_focus = triggered_id["name"]
        if new_focus not in valid_selection:
            valid_selection = valid_selection + [new_focus]
    elif current_focus in valid_selection:
        new_focus = current_focus
    else:
        # Species-aware fallback
        try:
            p_data = df[df["Name"] == current_focus]
            if not p_data.empty:
                old_focus_species = p_data["Species_Name"].iloc[0]
                related_members = [
                    name
                    for name in valid_selection
                    if df[df["Name"] == name]["Species_Name"].iloc[0]
                    == old_focus_species
                ]
                new_focus = (
                    related_members[0] if related_members else valid_selection[0]
                )
            else:
                new_focus = valid_selection[0] if valid_selection else ""
        except (IndexError, KeyError):
            new_focus = valid_selection[0] if valid_selection else ""

    logger.debug(
        f"Syncing focus: triggered={triggered_id}, new_focus={new_focus}, valid_count={len(valid_selection)}"
    )

    # Use simple list of strings for data - often more reliable in dmc v0.14
    data = sorted(list(set(valid_selection)), key=lambda x: valid_selection.index(x))
    style = {"display": "block"} if len(data) > 1 else {"display": "none"}

    # Force a rerender of the component by changing the key when selection changes
    # This fixes the dmc v0.14 label sync issue
    component_key = f"focus-sel-{'-'.join(data)}"

    return data, new_focus, style, component_key, valid_selection


@callback(
    Output("pokemon-image", "src"),
    Output("pokemon-name-display", "children"),
    Output("pokemon-types", "children"),
    Output("stat-progress-bars", "children"),
    Output("shiny-toggle", "style"),
    Output("shiny-toggle", "checked"),
    Output("trainer-comparison-display", "children"),
    Output("evolution-chain-display", "children"),
    Input("focus-selector", "value"),
    Input("shiny-toggle", "checked"),
    Input("trainer-height", "value"),
    Input("trainer-weight", "value"),
    Input("mega-toggle", "checked"),
    Input("gmax-toggle", "checked"),
    Input("regional-toggle", "checked"),
    State("pokemon-selector", "value"),
)
def update_details(
    focus_name: str,
    is_shiny: bool,
    t_height: float | str,
    t_weight: float | str,
    show_mega: bool,
    show_gmax: bool,
    show_regional: bool,
    selected_pokemon: List[str],
) -> Tuple[str, str, List[Any], List[Any], dict, bool, Any, Any]:
    """Update the detail card for the focused Pokémon."""
    # If no selection at all, or focus_name is somehow missing
    if not selected_pokemon or not focus_name:
        logger.debug("No Pokémon selected, showing placeholder detail view.")
        return "", "Select a Pokémon", [], [], {"display": "none"}, False, "", ""

    name = focus_name
    logger.debug(f"Updating detailed view for focus: {name}")
    try:
        p_data = df[df["Name"] == name].iloc[0]
    except IndexError:
        # Fallback if the focused name is not in the dataframe (shouldn't happen)
        return "", "Select a Pokémon", [], [], {"display": "none"}, False, "", ""

    # Evolution Chain Rendering
    evolution_display = []
    if "Evolution_Chain_Members" in p_data and p_data["Evolution_Chain_Members"]:
        members = p_data["Evolution_Chain_Members"].split(",")

        chain_items = []
        for member_species in members:
            # Find the best representative image (prefer base form)
            member_matches = df[df["Species_Name"] == member_species]
            if member_matches.empty:
                continue

            # Select the base form (usually the one with the lowest ID #)
            base_form = member_matches.sort_values("#").iloc[0]

            # Highlight if it's the current one being viewed
            is_active = base_form["Species_Name"] == p_data["Species_Name"]
            border_style = "2px solid #5D9CEC" if is_active else "1px solid transparent"

            # Create a group for this evolution stage + its variants
            stage_children = []

            # Main sprite for this stage
            stage_children.append(
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
                                    fallbackSrc="/assets/images/pokeball_placeholder.png",
                                    h=64,
                                    w="auto",
                                )
                            ],
                        )
                    ],
                )
            )

            # Add small icons for variants (Mega, Gmax, Regional) if they exist and are toggled ON
            variants = member_matches[member_matches["#"] != base_form["#"]]

            # Sub-filter the variants based on the toggle states
            if not variants.empty:
                variant_icons = []
                for _, v in variants.iterrows():
                    # Apply filters
                    if v.get("Is_Mega") and not show_mega:
                        continue
                    if v.get("Is_GMax") and not show_gmax:
                        continue
                    if v.get("Is_Regional") and not show_regional:
                        continue

                    v_label = v["Name"]
                    variant_icons.append(
                        dmc.Tooltip(
                            label=v_label,
                            children=[
                                html.Div(
                                    id={"type": "evo-link", "name": v_label},
                                    className="evolution-node",
                                    n_clicks=0,
                                    style={"cursor": "pointer"},
                                    children=[
                                        dmc.Image(
                                            src=v["Sprite_URL"],
                                            fallbackSrc="/assets/images/pokeball_placeholder.png",
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

    p_id = int(p_data["#"])
    p_height = p_data["Height"]
    p_weight = p_data["Weight"]

    # Trainer Comparison Logic
    t_height = float(t_height)
    t_weight = float(t_weight)
    height_ratio = p_height / t_height if t_height > 0 else 1
    weight_ratio = p_weight / t_weight if t_weight > 0 else 1

    if height_ratio > 1.2:
        h_text = f"This Pokémon is {height_ratio:.1f}x taller than you!"
    elif height_ratio < 0.8:
        h_text = f"You are {1 / height_ratio:.1f}x taller than this Pokémon!"
    else:
        h_text = "You are roughly the same height!"

    if weight_ratio > 1.5:
        w_text = f"It's {weight_ratio:.1f}x heavier than you!"
    elif weight_ratio < 0.6:
        w_text = f"You are {1 / weight_ratio:.1f}x heavier!"
    else:
        w_text = "You are in the same weight class!"

    comparison_view = dmc.Stack(
        gap=4,
        children=[
            dmc.Text("Trainer Comparison", size="xs", fw=700, c="dimmed"),
            dmc.Text(h_text, size="sm"),
            dmc.Text(w_text, size="sm"),
        ],
    )

    # Check for shiny availability to show/hide toggle
    shiny_exists = has_shiny_artwork(p_id)
    toggle_style = {"display": "block"} if shiny_exists else {"display": "none"}
    # Reset shiny toggle if it doesn't exist for this mon
    current_shiny = is_shiny if shiny_exists else False

    max_stat = df[STAT_OPTIONS].max().max()

    progress_bars = []
    for stat in STAT_OPTIONS:
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
        comparison_view,
        evolution_display,
    )
