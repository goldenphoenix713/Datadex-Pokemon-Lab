"""Utility functions for data filtering and processing."""

from typing import List
import pandas as pd
from src.data import df


def get_filtered_df(
    regions: List[str],
    show_mega: bool,
    show_regional: bool,
    final_only: bool,
    show_legendary: bool,
    show_mythical: bool,
    show_gmax: bool,
    selected_types: List[str],
    stat_ranges: dict,
) -> pd.DataFrame:
    """Centralized filtering logic for all visualizations."""
    # TODO: Change dataframe filtering to use duckdb instead of pandas
    # TODO: Have duckdb read the parquet file directly and return a pyarrow table
    # TODO: Completely remove pandas dependency from the project (it's too slow)
    # TODO: Add caching for filtered data to improve performance
    # TODO: Add type-ahead search for Pokémon names
    # TODO: Need to find additional ways to speed up app, it got really slow after the dash update

    filtered_df = df.copy()

    if regions:
        filtered_df = filtered_df[filtered_df["Region"].isin(regions)]

    if not show_mega:
        filtered_df = filtered_df[~filtered_df["Is_Mega"]]

    if not show_regional:
        filtered_df = filtered_df[~filtered_df["Is_Regional"]]

    if final_only:
        filtered_df = filtered_df[filtered_df["Is_Final_Evolution"]]

    if not show_legendary:
        filtered_df = filtered_df[~filtered_df["Is_Legendary"]]

    if not show_mythical:
        filtered_df = filtered_df[~filtered_df["Is_Mythical"]]

    if not show_gmax:
        filtered_df = filtered_df[~filtered_df["Is_GMax"]]

    if selected_types:
        filtered_df = filtered_df[
            (filtered_df["Primary Type"].isin(selected_types))
            | (filtered_df["Secondary Type"].isin(selected_types))
        ]

    # Apply Stat Range Filters
    for stat, r in stat_ranges.items():
        filtered_df = filtered_df[filtered_df[stat].between(r[0], r[1])]

    return filtered_df
