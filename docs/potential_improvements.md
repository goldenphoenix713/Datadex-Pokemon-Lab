# Data-Dex Roadmap: Potential Improvements

This document outlines several high-impact features and technical enhancements to further evolve the Data-Dex Pokémon Lab.

---

## 🎨 User Experience (UX) & Design

### 1. Evolution Chains

Display the visual evolution lineage for the selected Pokémon.

* **Implementation**:
    1. Update [fetch_api_data.py](file:///Users/eddie/PycharmProjects/Datadex-Pokemon-Lab/fetch_api_data.py) to hit the `/pokemon-species/{id}/` endpoint to find the `evolution_chain` URL.
    2. Fetch the chain data and flatten the nested JSON into a simple list of Pokémon IDs/names.
    3. Add a new component in the Detail Card in [app.py](file:///Users/eddie/PycharmProjects/Datadex-Pokemon-Lab/app.py) using `dmc.Timeline` or a horizontal `dmc.Group` of small images.

### 2. Generation & Region Filters

Allow users to filter the Pokémon selection list by specific generations (Kanto, Johto, etc.).

* **Implementation**:
    1. Add a `Generation` column to the Pokémon DataFrame in [data_manager.py](file:///Users/eddie/PycharmProjects/Datadex-Pokemon-Lab/data_manager.py) (Gen 1 is IDs 1-151, etc.).
    2. Add a `dmc.SegmentedControl` or `dmc.Chips` component above the `pokemon-selector` in `app.layout`.
    3. Create a callback that updates the [data](file:///Users/eddie/PycharmProjects/Datadex-Pokemon-Lab/data_manager.py#17-86) property of the `MultiSelect` dropdown based on the selected generation.

### 3. Shiny Artwork Toggle

Let users switch between standard and "shiny" colors for the main artwork.

* **Implementation**:
    1. Update [download_image](file:///Users/eddie/PycharmProjects/Datadex-Pokemon-Lab/data_manager.py#88-115) in [data_manager.py](file:///Users/eddie/PycharmProjects/Datadex-Pokemon-Lab/data_manager.py) to optionally fetch `.../official-artwork/shiny/{id}.png`.
    2. Add a `dmc.Switch` labeled "Shiny Mode" in the detailed view.
    3. Update the `update_detailed_view` callback to swap the `src` of the image based on the switch state.

---

## 📊 Enhanced Analytics

### 4. Dual-Type Sensitivity Analysis

Improve the leaderboard and type analysis to account for Pokémon with two types.

* **Implementation**:
    1. In [visualizations.py](file:///Users/eddie/PycharmProjects/Datadex-Pokemon-Lab/visualizations.py), modify the grouping logic to "explode" the DataFrame (using `df.explode('Secondary Type')`) so a dual-type Pokémon contributes to the average of both its types.
    2. Create a heatmap visualization showing which type combinations have the highest average stats.

### 5. Stat Global Ranking

Show exactly where a Pokémon stands compared to the rest of the world.

* **Implementation**:
    1. Calculate percentiles for each stat in [data_manager.py](file:///Users/eddie/PycharmProjects/Datadex-Pokemon-Lab/data_manager.py) using `df[stat].rank(pct=True)`.
    2. In the detail view, add a badge or text next to each progress bar (e.g., "Top 5% for Speed").

---

## 🛠 Technical Polish

### 6. Advanced Caching (Performance)

Reduce startup time and improve responsiveness using server-side caching.

* **Implementation**:
    1. Install `dash-cache` or `Flask-Caching`.
    2. Use the `@cache.memoize()` decorator on [load_and_clean_data](file:///Users/eddie/PycharmProjects/Datadex-Pokemon-Lab/data_manager.py#17-86) to ensure the Parquet file is only read once per session or on a timed interval.

### 7. UI Error Boundaries

Provide a graceful fallback if data fails to load or a callback errors out.

* **Implementation**:
    1. Wrap key layout components in a custom Error Boundary component.
    2. Use a global `dmc.Modal` or `dmc.Notification` that triggers on callback errors (using `dash.no_update` and a dedicated error signal) to tell the user "Something went wrong" instead of leaving the UI in a frozen state.

### 8. Full Unit Test Suite

Ensure stability through automated verification of the data pipeline.

* **Implementation**:
    1. Create [tests/test_data_manager.py](file:///Users/eddie/PycharmProjects/Datadex-Pokemon-Lab/tests/test_data_manager.py) to mock `requests` and verify the cleaning logic.
    2. Use `pytest-dash` to write integration tests that simulate user selection and verify that charts update correctly.
