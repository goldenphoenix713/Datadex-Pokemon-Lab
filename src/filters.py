"""Filter components for the Data-Dex application."""

from dash import (
    html,
    MATCH,
    Output,
    Input,
    State,
    clientside_callback,
    ClientsideFunction,
)
import dash_mantine_components as dmc
from src.constants import REGIONS, TYPES, STAT_OPTIONS

# Default initial state for the filter store.
# All downstream callbacks should read filter values from here.
FILTER_STORE_DEFAULTS = {
    "filters": {
        "region-filter": [],
        "type-filter": [],
        "sort-order": "number",
        "trainer-height": 4.5,
        "trainer-weight": 150,
        **{f"stat-{stat}": [0, 255] for stat in STAT_OPTIONS},
    },
    "toggles": {
        "mega-toggle": True,
        "regional-toggle": True,
        "final-evolution-toggle": False,
        "legendary-toggle": True,
        "mythical-toggle": True,
        "gmax-toggle": False,
        "ultra-beast-toggle": True,
    },
    "modified": None,
    "last_updated_id": None,
    "last_updated_value": None,
}


def create_filter_stack(group_name: str):
    return dmc.Stack(
        children=[
            dmc.Button(
                "Reset All Filters",
                id={"group": group_name, "type": "button", "id": "reset-filters-btn"},
                variant="subtle",
                color="gray",
                size="compact-xs",
                fullWidth=True,
                mb="sm",
            ),
            dmc.Accordion(
                multiple=True,
                value=["basic-filters"],
                styles={
                    "label": {
                        "overflow": "visible",
                        "paddingLeft": "15px",
                    },
                    "control": {"overflow": "visible"},
                },
                children=[
                    dmc.AccordionItem(
                        value="basic-filters",
                        children=[
                            dmc.AccordionControl(
                                "Basic Filters",
                                className="pokemon-section-title",
                            ),
                            dmc.AccordionPanel(
                                children=[
                                    dmc.MultiSelect(
                                        id={
                                            "group": group_name,
                                            "type": "filter",
                                            "id": "region-filter",
                                        },
                                        label="Regions",
                                        placeholder="Select Regions",
                                        data=REGIONS,
                                        value=[],
                                        mb="md",
                                    ),
                                    dmc.MultiSelect(
                                        id={
                                            "group": group_name,
                                            "type": "filter",
                                            "id": "type-filter",
                                        },
                                        label="Types",
                                        placeholder="Select Types",
                                        data=TYPES,
                                        value=[],
                                        mb="md",
                                    ),
                                    dmc.Select(
                                        id={
                                            "group": group_name,
                                            "type": "filter",
                                            "id": "sort-order",
                                        },
                                        label="Sort By",
                                        data=[
                                            {
                                                "label": "Pokédex Number",
                                                "value": "number",
                                            },
                                            {
                                                "label": "Name",
                                                "value": "name",
                                            },
                                        ],
                                        value="number",
                                        mb="md",
                                    ),
                                ]
                            ),
                        ],
                    ),
                    dmc.AccordionItem(
                        value="stat-ranges",
                        children=[
                            dmc.AccordionControl(
                                "Stat Ranges",
                                className="pokemon-section-title",
                            ),
                            dmc.AccordionPanel(
                                children=[
                                    html.Div(
                                        children=[
                                            html.Div(
                                                [
                                                    dmc.Text(
                                                        f"{stat} Range",
                                                        size="sm",
                                                        mb=5,
                                                    ),
                                                    dmc.RangeSlider(
                                                        id={
                                                            "group": group_name,
                                                            "type": "filter",
                                                            "id": f"stat-{stat}",
                                                        },
                                                        value=[0, 255],
                                                        min=0,
                                                        max=255,
                                                        step=1,
                                                        marks=[
                                                            {
                                                                "value": 0,
                                                                "label": "0",
                                                            },
                                                            {
                                                                "value": 128,
                                                                "label": "128",
                                                            },
                                                            {
                                                                "value": 255,
                                                                "label": "255",
                                                            },
                                                        ],
                                                        updatemode="mouseup",
                                                        mb="xl",
                                                    ),
                                                ]
                                            )
                                            for stat in STAT_OPTIONS
                                        ]
                                    ),
                                ]
                            ),
                        ],
                    ),
                    dmc.AccordionItem(
                        value="form-filters",
                        children=[
                            dmc.AccordionControl(
                                "Special Variants",
                                className="pokemon-section-title",
                            ),
                            dmc.AccordionPanel(
                                children=[
                                    dmc.Stack(
                                        gap="xs",
                                        children=[
                                            dmc.Switch(
                                                id={
                                                    "group": group_name,
                                                    "type": "toggle",
                                                    "id": "mega-toggle",
                                                },
                                                label="Show Mega evolutions",
                                                checked=True,
                                            ),
                                            dmc.Switch(
                                                id={
                                                    "group": group_name,
                                                    "type": "toggle",
                                                    "id": "regional-toggle",
                                                },
                                                label="Show Regional forms",
                                                checked=True,
                                            ),
                                            dmc.Switch(
                                                id={
                                                    "group": group_name,
                                                    "type": "toggle",
                                                    "id": "final-evolution-toggle",
                                                },
                                                label="Final Evolutions Only",
                                                checked=False,
                                            ),
                                            dmc.Switch(
                                                id={
                                                    "group": group_name,
                                                    "type": "toggle",
                                                    "id": "legendary-toggle",
                                                },
                                                label="Include Legendaries",
                                                checked=True,
                                            ),
                                            dmc.Switch(
                                                id={
                                                    "group": group_name,
                                                    "type": "toggle",
                                                    "id": "mythical-toggle",
                                                },
                                                label="Include Mythicals",
                                                checked=True,
                                            ),
                                            dmc.Switch(
                                                id={
                                                    "group": group_name,
                                                    "type": "toggle",
                                                    "id": "gmax-toggle",
                                                },
                                                label="Show G-Max forms",
                                                checked=False,
                                            ),
                                            dmc.Switch(
                                                id={
                                                    "group": group_name,
                                                    "type": "toggle",
                                                    "id": "ultra-beast-toggle",
                                                },
                                                label="Show Ultra Beasts",
                                                checked=True,
                                            ),
                                        ],
                                    ),
                                ]
                            ),
                        ],
                    ),
                    dmc.AccordionItem(
                        value="trainer-comparison",
                        children=[
                            dmc.AccordionControl(
                                "Trainer Comparison",
                                className="pokemon-section-title",
                            ),
                            dmc.AccordionPanel(
                                children=[
                                    dmc.Group(
                                        grow=True,
                                        children=[
                                            dmc.NumberInput(
                                                id={
                                                    "group": group_name,
                                                    "type": "filter",
                                                    "id": "trainer-height",
                                                },
                                                label="Your Height (ft)",
                                                value=4.5,
                                                min=2,
                                                max=7,
                                                step=0.01,
                                                debounce=500,
                                            ),
                                            dmc.NumberInput(
                                                id={
                                                    "group": group_name,
                                                    "type": "filter",
                                                    "id": "trainer-weight",
                                                },
                                                label="Your Weight (lbs)",
                                                value=150,
                                                min=10,
                                                max=500,
                                                step=1,
                                                debounce=500,
                                            ),
                                        ],
                                        mb="md",
                                    ),
                                ]
                            ),
                        ],
                    ),
                ],
            ),
            dmc.Divider(my="md"),
            dmc.Text("Selection Helper", size="xs", c="dimmed", mb="xs"),
            dmc.Text(
                "Use these filters to narrow down the list of Pokémon in the selector.",
                size="xs",
                c="dimmed",
            ),
        ]
    )


clientside_callback(
    ClientsideFunction(namespace="clientside", function_name="sync_filters_clientside"),
    Output({"group": "navbar", "type": "filter", "id": MATCH}, "value"),
    Output({"group": "drawer", "type": "filter", "id": MATCH}, "value"),
    Output("filter-store", "data", allow_duplicate=True),
    Input({"group": "drawer", "type": "filter", "id": MATCH}, "value"),
    Input({"group": "navbar", "type": "filter", "id": MATCH}, "value"),
    State("filter-store", "data"),
    prevent_initial_call=True,
)


clientside_callback(
    ClientsideFunction(namespace="clientside", function_name="sync_toggles_clientside"),
    Output({"group": "navbar", "type": "toggle", "id": MATCH}, "checked"),
    Output({"group": "drawer", "type": "toggle", "id": MATCH}, "checked"),
    Output("filter-store", "data", allow_duplicate=True),
    Input({"group": "drawer", "type": "toggle", "id": MATCH}, "checked"),
    Input({"group": "navbar", "type": "toggle", "id": MATCH}, "checked"),
    State("filter-store", "data"),
    prevent_initial_call=True,
)


def _reset_outputs_for_group(group: str):
    """Build the Output list for resetting all filter/toggle components in a group."""
    outputs = []
    # filter outputs (value property)
    for f_id in [
        "region-filter",
        "type-filter",
        "sort-order",
        "trainer-height",
        "trainer-weight",
    ]:
        outputs.append(
            Output(
                {"group": group, "type": "filter", "id": f_id},
                "value",
                allow_duplicate=True,
            )
        )
    for stat in STAT_OPTIONS:
        outputs.append(
            Output(
                {"group": group, "type": "filter", "id": f"stat-{stat}"},
                "value",
                allow_duplicate=True,
            )
        )
    # toggle outputs (checked property)
    for t_id in [
        "mega-toggle",
        "regional-toggle",
        "final-evolution-toggle",
        "legendary-toggle",
        "mythical-toggle",
        "gmax-toggle",
        "ultra-beast-toggle",
    ]:
        outputs.append(
            Output(
                {"group": group, "type": "toggle", "id": t_id},
                "checked",
                allow_duplicate=True,
            )
        )
    return outputs


def _reset_values():
    """Return the default values matching _reset_outputs_for_group ordering."""
    f = FILTER_STORE_DEFAULTS["filters"]
    t = FILTER_STORE_DEFAULTS["toggles"]
    values = []
    for f_id in [
        "region-filter",
        "type-filter",
        "sort-order",
        "trainer-height",
        "trainer-weight",
    ]:
        values.append(f[f_id])
    for stat in STAT_OPTIONS:
        values.append(f[f"stat-{stat}"])
    for t_id in [
        "mega-toggle",
        "regional-toggle",
        "final-evolution-toggle",
        "legendary-toggle",
        "mythical-toggle",
        "gmax-toggle",
        "ultra-beast-toggle",
    ]:
        values.append(t[t_id])
    return values


clientside_callback(
    ClientsideFunction(
        namespace="clientside", function_name="reset_filters_clientside"
    ),
    *_reset_outputs_for_group("navbar"),
    *_reset_outputs_for_group("drawer"),
    Output("filter-store", "data", allow_duplicate=True),
    Input({"group": "navbar", "type": "button", "id": "reset-filters-btn"}, "n_clicks"),
    Input({"group": "drawer", "type": "button", "id": "reset-filters-btn"}, "n_clicks"),
    prevent_initial_call=True,
)
