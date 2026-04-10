import dash
from typing import List
from dash import (
    callback,
    Input,
    Output,
)
from src.utils import get_filtered_table as get_filtered_pokemon_table
from src.filters import FILTER_STORE_DEFAULTS


@callback(
    Output("focus-selector", "data"),
    Input("filter-store", "data"),
)
def update_focus_options(filter_store: dict) -> List[dict]:
    """Filter the list of available Pokémon names for the focus selector."""
    filters = (filter_store or {}).get("filters", FILTER_STORE_DEFAULTS["filters"])
    toggles = (filter_store or {}).get("toggles", FILTER_STORE_DEFAULTS["toggles"])

    regions = filters.get("region-filter", [])
    selected_types = filters.get("type-filter", [])
    sort_by = filters.get("sort-order", "number")
    show_mega = toggles.get("mega-toggle", True)
    show_regional = toggles.get("regional-toggle", True)
    final_only = toggles.get("final-evolution-toggle", False)
    show_legendary = toggles.get("legendary-toggle", True)
    show_mythical = toggles.get("mythical-toggle", True)
    show_gmax = toggles.get("gmax-toggle", False)
    show_ultra_beasts = toggles.get("ultra-beast-toggle", True)

    stat_ranges = {
        key.removeprefix("stat-"): value
        for key, value in filters.items()
        if key.startswith("stat-")
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
    Input({"type": "evo-link", "name": dash.ALL}, "n_clicks"),
    prevent_initial_call=True,
)
