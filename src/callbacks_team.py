from dash import (
    Input,
    Output,
    ALL,
    State,
    ClientsideFunction,
    clientside_callback,
)


# Team store mutations — handled fully client-side, no server round-trip.
# The JS function inspects window.dash_clientside.callback_context.triggered
# to distinguish add / clear / remove actions.
clientside_callback(
    ClientsideFunction(namespace="clientside", function_name="update_team"),
    Output("team-store", "data"),
    Input("add-pokemon-btn", "n_clicks"),
    Input("clear-team-btn", "n_clicks"),
    Input({"type": "remove-team", "name": ALL}, "n_clicks"),
    State("focus-selector", "value"),
    State("team-store", "data"),
    prevent_initial_call=True,
)

clientside_callback(
    ClientsideFunction(namespace="clientside", function_name="render_team_list"),
    Output("team-list", "children"),
    Input("team-store", "data"),
    Input("pokemon-id-map", "data"),
)
