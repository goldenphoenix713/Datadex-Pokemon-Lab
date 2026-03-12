# Data-Dex: Ultimate Stat Lab — Final Walkthrough

The Data-Dex application is now fully implemented and verified. It serves as an interactive educational tool for 3rd–5th graders to learn data visualization using Pokémon stats.

## Key Accomplishments

- **Full Dataset:** Fetched and processed 1,350 Pokémon entries (including all forms with statistical or type differences) from PokéAPI.
- **Instant Performance:** Data is served from a local, compressed Parquet file ([data/pokemon.parquet](file:///Users/eduardo.ruiz/PycharmProjects/Datadex-Pokemon-Lab/data/pokemon.parquet)) ensuring zero latency during classroom use.
- **Interactive Visualizations:**
  - **Face-Off Radar:** Compare stats for up to 3 Pokémon simultaneously.
  - **Type Leaderboard:** Horizontal bar chart comparing stat averages by type against a global average line.
  - **Outlier Hunt:** Scatter plot for exploring relationships between any two stats (e.g., Weight vs. Speed).
- **Premium UI:**
  - Built with **Dash Mantine Components 0.14** for a modern, responsive layout.
  - Custom **Pokémon-themed styling** with the "Pokemon Solid" font, yellow/blue title effects, and glowing cards.
  - Detailed Pokémon sidebar with live artwork and animated stat progress bars.
- **Modern Environment:** Fully migrated to **Python 3.12** using **uv** for high-speed dependency management.

---

## Visual Verification

````carousel
![Radar Comparison](/Users/eduardo.ruiz/.gemini/antigravity/brain/be516feb-38c4-4887-b037-7dd9b8f262fe/radar_chart_3_pokemon_1773200152319.png)
<!-- slide -->
![Leaderboard & Scatter Plot](/Users/eduardo.ruiz/.gemini/antigravity/brain/be516feb-38c4-4887-b037-7dd9b8f262fe/.system_generated/click_feedback/click_feedback_1773200185319.png)
<!-- slide -->
![MultiSelect Visibility Fix](/Users/eduardo.ruiz/.gemini/antigravity/brain/be516feb-38c4-4887-b037-7dd9b8f262fe/multiselect_dropdown_opened_1773201205104.png)
````

---

## Implementation Details

| Component | File | Description |
|-----------|------|-------------|
| **App Entry** | [app.py](file:///Users/eduardo.ruiz/PycharmProjects/Datadex-Pokemon-Lab/app.py) | Main layout and Dash callbacks. |
| **Data Logic** | [data_manager.py](file:///Users/eduardo.ruiz/PycharmProjects/Datadex-Pokemon-Lab/data_manager.py) | Parquet loading and stat renaming. |
| **Charts** | [visualizations.py](file:///Users/eduardo.ruiz/PycharmProjects/Datadex-Pokemon-Lab/visualizations.py) | Pure Plotly functions for Radar, Bar, and Scatter charts. |
| **Pipeline** | [fetch_api_data.py](file:///Users/eduardo.ruiz/PycharmProjects/Datadex-Pokemon-Lab/fetch_api_data.py) | Multi-threaded PokéAPI scraper. |
| **Styling** | [assets/custom.css](file:///Users/eduardo.ruiz/PycharmProjects/Datadex-Pokemon-Lab/assets/custom.css) | Global styles and custom font registration. |

---

## How to Run

1. Ensure the virtual environment is active:

   ```bash
   source .venv/bin/activate
   ```

2. Launch the app:

   ```bash
   python app.py
   ```

3. Open <http://127.0.0.1:8050/> in your browser.
