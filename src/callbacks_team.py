from typing import List
from dash import (
    callback,
    Input,
    Output,
    ctx,
    ALL,
    State,
    ClientsideFunction,
    clientside_callback,
)
from loguru import logger


@callback(
    Output("team-store", "data"),
    Input("add-pokemon-btn", "n_clicks"),
    Input("clear-team-btn", "n_clicks"),
    Input({"type": "remove-team", "name": ALL}, "n_clicks"),
    State("focus-selector", "value"),
    State("team-store", "data"),
    prevent_initial_call=True,
)
def update_team(
    add_clicks: int,
    clear_clicks: int,
    remove_clicks: List[int],
    focus_pokemon: str,
    current_team: List[str],
) -> List[str]:
    """Add or remove a Pokémon from the team store."""
    if not ctx.triggered:
        return current_team

    triggered_id = ctx.triggered_id
    logger.debug(f"Team update triggered by: {triggered_id}")

    if triggered_id == "add-pokemon-btn":
        if (
            focus_pokemon
            and focus_pokemon not in current_team
            and len(current_team) < 6
        ):
            current_team.append(focus_pokemon)
            logger.info(f"Added {focus_pokemon} to team.")
    elif triggered_id == "clear-team-btn":
        current_team = []
        logger.info("Cleared team.")
    elif isinstance(triggered_id, dict) and triggered_id.get("type") == "remove-team":
        pokemon_name = triggered_id["name"]
        if pokemon_name in current_team:
            current_team.remove(pokemon_name)
            logger.info(f"Removed {pokemon_name} from team.")

    return current_team


clientside_callback(
    ClientsideFunction(namespace="clientside", function_name="render_team_list"),
    Output("team-list", "children"),
    Input("team-store", "data"),
    Input("pokemon-id-map", "data"),
)
