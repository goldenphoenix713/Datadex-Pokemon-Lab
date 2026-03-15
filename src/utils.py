from typing import List, Any


def get_filtered_table(
    regions: List[str],
    show_mega: bool,
    show_regional: bool,
    final_only: bool,
    show_legendary: bool,
    show_mythical: bool,
    show_gmax: bool,
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

    if selected_types:
        type_list = ", ".join([f"'{t}'" for t in selected_types])
        where_clauses.append(
            f'("Primary Type" IN ({type_list}) OR "Secondary Type" IN ({type_list}))'
        )

    # Apply Stat Range Filters
    for stat, r in stat_ranges.items():
        # Mapping for SQL column names if needed, but they match the table columns
        where_clauses.append(f'"{stat}" BETWEEN {r[0]} AND {r[1]}')

    query = 'SELECT * FROM "pokemon"'
    if where_clauses:
        query += " WHERE " + " AND ".join(where_clauses)

    return conn.execute(query).to_arrow_table()


# For backward compatibility during migration
get_filtered_df = get_filtered_table
