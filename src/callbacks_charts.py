from dash import Output, Input, ClientsideFunction, clientside_callback, ALL

# Clientside callbacks for performance-critical chart updates.
# These bypass the server entirely once the initial data is loaded.

# 1. Radar Chart: Updates based on team selection
clientside_callback(
    ClientsideFunction(namespace="clientside", function_name="update_radar_clientside"),
    Output("radar-chart", "figure"),
    Input("team-store", "data"),
    Input("pokemon-id-map", "data"),
    Input("full-pokemon-data", "data"),
)

# 2. Type Leaderboard: Updates based on filters and stat selection
clientside_callback(
    ClientsideFunction(
        namespace="clientside", function_name="update_leaderboard_clientside"
    ),
    Output("leaderboard-chart", "figure"),
    [
        Input("full-pokemon-data", "data"),
        Input("region-filter", "value"),
        Input("mega-toggle", "checked"),
        Input("regional-toggle", "checked"),
        Input("final-evolution-toggle", "checked"),
        Input("legendary-toggle", "checked"),
        Input("mythical-toggle", "checked"),
        Input("gmax-toggle", "checked"),
        Input("ultra-beast-toggle", "checked"),
        Input("type-filter", "value"),
        Input({"type": "stat", "name": ALL}, "value"),
        Input("stats-names-store", "data"),
        Input("stat-selector", "value"),
    ],
)

# 3. Scatter Plot: Updates based on filters and axis selection
clientside_callback(
    ClientsideFunction(
        namespace="clientside", function_name="update_scatter_clientside"
    ),
    Output("scatter-plot", "figure"),
    [
        Input("full-pokemon-data", "data"),
        Input("region-filter", "value"),
        Input("mega-toggle", "checked"),
        Input("regional-toggle", "checked"),
        Input("final-evolution-toggle", "checked"),
        Input("legendary-toggle", "checked"),
        Input("mythical-toggle", "checked"),
        Input("gmax-toggle", "checked"),
        Input("ultra-beast-toggle", "checked"),
        Input("type-filter", "value"),
        Input({"type": "stat", "name": ALL}, "value"),
        Input("stats-names-store", "data"),
        Input("x-axis-selector", "value"),
        Input("y-axis-selector", "value"),
    ],
)
