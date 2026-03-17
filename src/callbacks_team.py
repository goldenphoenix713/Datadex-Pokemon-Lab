from typing import List
from dash import callback, Input, Output, ctx, ALL, State
from loguru import logger


@callback(
    Output("team-store", "data"),
    Input({"type": "add-team", "name": ALL}, "n_clicks"),
    Input({"type": "remove-team", "name": ALL}, "n_clicks"),
    State("team-store", "data"),
)
def update_team(
    add_clicks: List[int], remove_clicks: List[int], current_team: List[str]
) -> List[str]:
    """Add or remove a Pokémon from the team store."""
    if not ctx.triggered:
        return current_team

    triggered_id = ctx.triggered_id
    if triggered_id["type"] == "add-team":
        pokemon_name = triggered_id["name"]
        if pokemon_name not in current_team and len(current_team) < 6:
            current_team.append(pokemon_name)
            logger.info(f"Added {pokemon_name} to team.")
    elif triggered_id["type"] == "remove-team":
        pokemon_name = triggered_id["name"]
        if pokemon_name in current_team:
            current_team.remove(pokemon_name)
            logger.info(f"Removed {pokemon_name} from team.")

    return current_team
