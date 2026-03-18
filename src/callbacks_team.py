from typing import List, Any
from dash import callback, Input, Output, ctx, ALL, State
import dash_mantine_components as dmc
from dash_iconify import DashIconify
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


@callback(
    Output("team-list", "children"),
    Input("team-store", "data"),
)
def render_team_list(team: List[str]) -> Any:
    """Render the team members as badges with remove buttons."""
    if not team:
        return dmc.Text(
            "No Pokémon in your team yet. Add some from the Detail view!",
            c="dimmed",
            size="sm",
            fs="italic",
        )

    from data_manager import ensure_pokemon_sprite
    from src.data import pokemon_ids

    badges = []
    for name in team:
        p_id = pokemon_ids.get(name, 0)
        badges.append(
            dmc.Paper(
                withBorder=True,
                shadow="xs",
                p=4,
                radius="sm",
                style={
                    "display": "flex",
                    "alignItems": "center",
                    "gap": "8px",
                    "backgroundColor": "rgba(255, 255, 255, 0.05)",
                },
                children=[
                    dmc.Image(
                        src=ensure_pokemon_sprite(int(p_id), name),
                        h=30,
                        w=30,
                        fallbackSrc="/assets/sprites/pokeball_placeholder.png",
                    ),
                    dmc.Text(name, size="sm", fw=500, style={"flex": 1}),
                    dmc.ActionIcon(
                        id={"type": "remove-team", "name": name},
                        variant="subtle",
                        color="red",
                        size="sm",
                        children=DashIconify(icon="tabler:x"),
                    ),
                ],
            )
        )

    return dmc.Group(gap="xs", children=badges)
