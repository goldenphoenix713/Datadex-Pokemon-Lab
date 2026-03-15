# TODOs

- TODO: Change dataframe filtering to use duckdb instead of pandas
- TODO: Have duckdb read the parquet file directly and return a pyarrow table
- TODO: Completely remove pandas dependency from the project (it's too slow)
- TODO: Add caching for filtered data to improve performance
- TODO: Need to find additional ways to speed up app, it got really slow after the dash update.
- TODO: It seems various callbacks are being called multiple times, need to find a way to prevent this.
- TODO: Change layout with the detailed stats on the left and the radar chart on the right. The main dropdown will select the pokemon in the detailed stats section. Then there's a button to add the pokemon to the radar chart. There should be a list of pokemon as a selectable list that shows which pokemon are currently selected for the radar chart. This list should have a remove button next to each pokemon to remove it from the radar chart. The radar chart should be updated in real-time as pokemon are added or removed from the list. The list should be scrollable if there are more than 5 pokemon in the list.
- TODO: Add a button to clear the radar chart and the selected pokemon list.
