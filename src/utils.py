from typing import List, Any


def get_filtered_table(
    regions: List[str],
    show_mega: bool,
    show_regional: bool,
    final_only: bool,
    show_legendary: bool,
    show_mythical: bool,
    show_gmax: bool,
    show_ultra_beasts: bool,
    selected_types: List[str],
    stat_ranges: dict,
) -> Any:
    """Centralized filtering logic for all visualizations using DuckDB."""
    from src.data import conn

    where_clauses = []

    if regions:
        region_list = ", ".join([f"'{r}'" for r in regions])
        where_clauses.append(f"Region IN ({region_list})")

    if not show_mega:
        where_clauses.append("NOT Is_Mega")

    if not show_regional:
        where_clauses.append("NOT Is_Regional")

    if final_only:
        where_clauses.append("Is_Final_Evolution")

    if not show_legendary:
        where_clauses.append("NOT Is_Legendary")

    if not show_mythical:
        where_clauses.append("NOT Is_Mythical")

    if not show_gmax:
        where_clauses.append("NOT Is_GMax")

    if not show_ultra_beasts:
        where_clauses.append("NOT Is_Ultra_Beast")

    if selected_types:
        type_list = ", ".join([f"'{t}'" for t in selected_types])
        where_clauses.append(
            f'("Primary Type" IN ({type_list}) OR "Secondary Type" IN ({type_list}))'
        )

    # Apply Stat Range Filters
    for stat, r in stat_ranges.items():
        where_clauses.append(f'"{stat}" BETWEEN {r[0]} AND {r[1]}')

    query = """
    SELECT *,
           CASE
               WHEN "Secondary Type" = 'None' THEN "Primary Type"
               ELSE "Primary Type" || '/' || "Secondary Type"
           END AS "Typing"
    FROM "pokemon"
    """
    if where_clauses:
        query += " WHERE " + " AND ".join(where_clauses)

    from src.data import db_lock

    with db_lock:
        return conn.execute(query).to_arrow_table()


# For backward compatibility during migration
get_filtered_df = get_filtered_table
