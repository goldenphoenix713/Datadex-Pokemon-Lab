from dash import Output, Input, ClientsideFunction, clientside_callback

# Clientside callbacks for performance-critical chart updates.
# These bypass the server entirely once the initial data is loaded.
# All filter-related inputs are consolidated into a single filter-store trigger.

# 1. Radar Chart: Updates based on team selection
clientside_callback(
    ClientsideFunction(namespace="clientside", function_name="update_radar_clientside"),
    Output("radar-chart", "figure"),
    Input("team-store", "data"),
    Input("pokemon-id-map", "data"),
    Input("full-pokemon-data", "data"),
    Input("reset-zoom-radar", "n_clicks"),
)

# 2. Type Leaderboard: Updates based on filter-store and stat selection
clientside_callback(
    ClientsideFunction(
        namespace="clientside", function_name="update_leaderboard_clientside"
    ),
    Output("leaderboard-chart", "figure"),
    Input("full-pokemon-data", "data"),
    Input("filter-store", "data"),
    Input("stats-names-store", "data"),
    Input("stat-selector", "value"),
    Input("reset-zoom-leaderboard", "n_clicks"),
)

# 3. Scatter Plot: Updates based on filter-store and axis selection
clientside_callback(
    ClientsideFunction(
        namespace="clientside", function_name="update_scatter_clientside"
    ),
    Output("scatter-plot", "figure"),
    Input("full-pokemon-data", "data"),
    Input("filter-store", "data"),
    Input("stats-names-store", "data"),
    Input("x-axis-selector", "value"),
    Input("y-axis-selector", "value"),
    Input("reset-zoom-scatter", "n_clicks"),
)
