import functools
import pyarrow.compute as pc
from typing import List, Any, Optional, Tuple


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
    """Centralized filtering logic for all visualizations using PyArrow for speed."""

    # Pre-process arguments to be hashable for lru_cache
    regions_tup = tuple(sorted(regions)) if regions else None
    types_tup = tuple(sorted(selected_types)) if selected_types else None
    # Sort dict items to ensure consistent hashing
    stats_tup = (
        tuple(sorted((k, tuple(v)) for k, v in stat_ranges.items()))
        if stat_ranges
        else None
    )

    return _get_filtered_table_cached(
        regions_tup,
        show_mega,
        show_regional,
        final_only,
        show_legendary,
        show_mythical,
        show_gmax,
        show_ultra_beasts,
        types_tup,
        stats_tup,
    )


@functools.lru_cache(maxsize=32)
def _get_filtered_table_cached(
    regions: Optional[Tuple[str, ...]],
    show_mega: bool,
    show_regional: bool,
    final_only: bool,
    show_legendary: bool,
    show_mythical: bool,
    show_gmax: bool,
    show_ultra_beasts: bool,
    selected_types: Optional[Tuple[str, ...]],
    stat_ranges: Optional[Tuple[Tuple[str, Tuple[int, int]], ...]],
) -> Any:
    """Cached implementation using PyArrow compute expressions."""
    from src.data import pokemon_table

    # Start with a mask of all True
    mask = pc.field("id") == pc.field("id")

    if regions:
        mask = mask & pc.field("Region").isin(list(regions))

    if not show_mega:
        mask = mask & ~pc.field("Is_Mega")

    if not show_regional:
        mask = mask & ~pc.field("Is_Regional")

    if final_only:
        mask = mask & pc.field("Is_Final_Evolution")

    if not show_legendary:
        mask = mask & ~pc.field("Is_Legendary")

    if not show_mythical:
        mask = mask & ~pc.field("Is_Mythical")

    if not show_gmax:
        mask = mask & ~pc.field("Is_GMax")

    if not show_ultra_beasts:
        mask = mask & ~pc.field("Is_Ultra_Beast")

    if selected_types:
        type_mask = pc.field("Primary Type").isin(list(selected_types)) | pc.field(
            "Secondary Type"
        ).isin(list(selected_types))
        mask = mask & type_mask

    if stat_ranges:
        for stat, (low, high) in stat_ranges:
            stat_mask = (pc.field(stat) >= low) & (pc.field(stat) <= high)
            mask = mask & stat_mask

    return pokemon_table.filter(mask)


# For backward compatibility during migration
get_filtered_pokemon_table = get_filtered_table
