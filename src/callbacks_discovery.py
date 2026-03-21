import dash
from typing import List
from dash import (
    callback,
    Input,
    Output,
    ALL,
    ctx,
    ClientsideFunction,
    clientside_callback,
)
from src.utils import get_filtered_table as get_filtered_pokemon_table


@callback(
    Output("focus-selector", "data"),
    Input("region-filter", "value"),
    Input("mega-toggle", "checked"),
    Input("regional-toggle", "checked"),
    Input("final-evolution-toggle", "checked"),
    Input("legendary-toggle", "checked"),
    Input("mythical-toggle", "checked"),
    Input("gmax-toggle", "checked"),
    Input("ultra-beast-toggle", "checked"),
    Input("type-filter", "value"),
    Input("sort-order", "value"),
    Input({"type": "stat", "name": ALL}, "value"),
)
def update_focus_options(
    regions: List[str],
    show_mega: bool,
    show_regional: bool,
    final_only: bool,
    show_legendary: bool,
    show_mythical: bool,
    show_gmax: bool,
    show_ultra_beasts: bool,
    selected_types: List[str],
    sort_by: str,
    stat_values: List[List[int]],
) -> List[dict]:
    """Filter the list of available Pokémon names for the focus selector."""
    stat_ranges = {
        item["id"]["name"]: item["value"]
        for item in ctx.inputs_list
        if isinstance(item, list)
        for item in item
        if isinstance(item["id"], dict) and item["id"].get("type") == "stat"
    }

    filtered_table = get_filtered_pokemon_table(
        regions,
        show_mega,
        show_regional,
        final_only,
        show_legendary,
        show_mythical,
        show_gmax,
        show_ultra_beasts,
        selected_types,
        stat_ranges,
    )

    options = []
    for row in filtered_table.to_pylist():
        options.append(
            {
                "label": row["Name"],
                "value": row["Name"],
                "number": row["number"],
            }
        )

    if sort_by == "number":
        sorted_options = sorted(options, key=lambda x: x["number"])
    else:
        sorted_options = sorted(options, key=lambda x: str(x["value"]))

    return [{"label": opt["label"], "value": opt["value"]} for opt in sorted_options]


dash.clientside_callback(
    """
    function(options) {
        if (!options || options.length === 0) {
            return {"display": "none"};
        }
        return {"display": "block"};
    }
    """,
    Output("focus-selector", "style"),
    Input("focus-selector", "data"),
)

dash.clientside_callback(
    dash.ClientsideFunction(
        namespace="clientside", function_name="handleEvolutionClick"
    ),
    Output("focus-selector", "value"),
    Input({"type": "evo-link", "name": ALL}, "n_clicks"),
    prevent_initial_call=True,
)


# "Reset All Filters" — handled fully client-side, no server round-trip.
# The JS function returns the default values for all filter components directly.
clientside_callback(
    ClientsideFunction(namespace="clientside", function_name="reset_filters"),
    Output("region-filter", "value"),
    Output("type-filter", "value"),
    Output("mega-toggle", "checked"),
    Output("regional-toggle", "checked"),
    Output("final-evolution-toggle", "checked"),
    Output("legendary-toggle", "checked"),
    Output("mythical-toggle", "checked"),
    Output("gmax-toggle", "checked"),
    Output("ultra-beast-toggle", "checked"),
    Output({"type": "stat", "name": ALL}, "value"),
    Input("reset-filters-btn", "n_clicks"),
    prevent_initial_call=True,
)
