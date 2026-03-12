# Data-Dex: Ultimate Stat Lab — Implementation Plan

A Dash/Plotly educational app for 3rd–5th graders that teaches data visualization (Radar, Bar, Scatter) using Pokémon data. The app loads an offline Parquet dataset for instant classroom performance.

> [!IMPORTANT]
> **Python version:** The current [.python-version](file:///Users/eduardo.ruiz/PycharmProjects/Datadex-Pokemon-Lab/.python-version) is `3.7`, but `dash-mantine-components ≥ 0.14` requires **Python ≥ 3.8**. The plan upgrades the project to **Python 3.12** (latest stable). You will need a Python 3.12 interpreter available on your system. If you'd prefer a different version (3.8–3.11), let me know.

---

## Proposed Changes

### Phase 0 — Environment & Dependencies

#### [MODIFY] [pyproject.toml](file:///Users/eduardo.ruiz/PycharmProjects/Datadex-Pokemon-Lab/pyproject.toml)
- Change `requires-python` from `">=3.7"` to `">=3.12"`
- Add project dependencies:
  ```
  dash ~= 2.17
  plotly ~= 5.24
  dash-mantine-components ~= 0.14
  pandas ~= 2.2
  pyarrow ~= 17.0
  requests ~= 2.32
  ```

#### [MODIFY] [.python-version](file:///Users/eduardo.ruiz/PycharmProjects/Datadex-Pokemon-Lab/.python-version)
- Change content from `3.7` to `3.12`

After updating, recreate the venv and install:
```bash
python3.12 -m venv .venv && source .venv/bin/activate && pip install -e .
```

---

### Phase 1 — Data Pipeline

#### [NEW] [fetch_api_data.py](file:///Users/eduardo.ruiz/PycharmProjects/Datadex-Pokemon-Lab/fetch_api_data.py)

One-off script — **only run once** to generate the Parquet file, not at app runtime.

- Fetch the first **151 Pokémon** (Gen 1) from `https://pokeapi.co/api/v2/pokemon/{id}`
- Extract per-Pokémon: `#` (id), `Name`, `Type 1`, `Type 2`, `HP`, `Attack`, `Defense`, `Sp. Atk`, `Sp. Def`, `Speed`, `Height`, `Weight`
- Apply strict pandas dtypes (int for stats, category for types)
- Write to `data/pokemon.parquet` with Snappy compression
- Include progress logging (e.g., `Fetched 42/151…`)

#### [NEW] [data/pokemon.parquet](file:///Users/eduardo.ruiz/PycharmProjects/Datadex-Pokemon-Lab/data/pokemon.parquet)
- Generated output — ~15 KB compressed Parquet, 151 rows × 12 columns

---

### Phase 2 — Data Manager

#### [NEW] [data_manager.py](file:///Users/eduardo.ruiz/PycharmProjects/Datadex-Pokemon-Lab/data_manager.py)

Directly matches the handoff spec:

- `load_and_clean_data(filepath)` → `pd.DataFrame`
  - Reads Parquet with pyarrow engine
  - Renames columns to kid-friendly labels (`Sp. Atk` → `Energy Blast`, etc.)
  - Fills `NaN` in `Secondary Type` with `"None"`
  - Generates `Image_URL` from Pokédex `#` pointing to official artwork on GitHub

---

### Phase 3 — Visualizations

#### [NEW] [visualizations.py](file:///Users/eduardo.ruiz/PycharmProjects/Datadex-Pokemon-Lab/visualizations.py)

Three pure functions, each returning a `go.Figure`:

##### `create_radar_chart(df, pokemon_names) → go.Figure`
- Already specified in handoff — `Scatterpolar` with closed polygons
- Static radial range `[0, 160]`, smooth transitions, transparent background
- Categories: HP, Attack, Defense, Speed, Energy Shield, Energy Blast

##### `create_type_leaderboard(df, stat_column) → go.Figure`
- **New.** Horizontal bar chart grouped by `Primary Type`
- Computes mean of the selected stat per type, sorts descending
- Adds a vertical `shapes` line at the global average with annotation
- Color-codes bars by canonical Pokémon type colors (Fire = `#F08030`, Water = `#6890F0`, etc.)
- Transparent background, tasteful font sizing

##### `create_scatter_plot(df, x_col, y_col) → go.Figure`
- **New.** Scatter plot with Pokémon names on hover
- Axes configurable (default: Weight vs Speed)
- Marker color by `Primary Type`, size slightly varied
- Hover template: Name, both stat values, Type

---

### Phase 4 — App Layout & UI Components

#### [NEW] [app.py](file:///Users/eduardo.ruiz/PycharmProjects/Datadex-Pokemon-Lab/app.py)
*(replaces the stub [main.py](file:///Users/eduardo.ruiz/PycharmProjects/Datadex-Pokemon-Lab/main.py) which will be deleted)*

Top-level layout inside `dmc.MantineProvider` with dark/light theme:

| Zone | Card Title | Input Controls | Graph |
|------|-----------|----------------|-------|
| **Face-Off Radar** | "Face-Off Radar" | `dmc.MultiSelect` (2–3 Pokémon) | `dcc.Graph` → radar |
| **Type Leaderboard** | "Type Leaderboard" | `dmc.Select` (stat picker: HP, Attack, …) | `dcc.Graph` → bar |
| **Outlier Hunt** | "Outlier Hunt" | 2 × `dmc.Select` (X-axis, Y-axis) | `dcc.Graph` → scatter |

Additional sidebar/section:
- Selected Pokémon artwork (`html.Img` with `Image_URL`)
- Stat progress bars using `dmc.Progress` (value = stat/160 × 100)

Layout uses `dmc.Grid` / `dmc.GridCol` with responsive `span` and [md](file:///Users/eduardo.ruiz/PycharmProjects/Datadex-Pokemon-Lab/README.md) breakpoints for tablet-friendly rendering.

#### [DELETE] [main.py](file:///Users/eduardo.ruiz/PycharmProjects/Datadex-Pokemon-Lab/main.py)
- Stub file replaced by `app.py`

---

### Phase 5 — Dash Callbacks

All callbacks in `app.py`:

| Callback | Input | Output |
|----------|-------|--------|
| **Radar update** | `MultiSelect.value` → list of names | `radar-graph.figure` |
| **Leaderboard update** | `Select.value` → stat column name | `leaderboard-graph.figure` |
| **Scatter update** | `x-select.value`, `y-select.value` | `scatter-graph.figure` |
| **Pokémon detail** | `MultiSelect.value` (first selected) | `pokemon-image.src`, `progress-*.value` |

Each callback calls the corresponding `visualizations.py` function with the cleaned DataFrame and user-selected parameters.

---

### Phase 6 — Styling

#### [NEW] [assets/custom.css](file:///Users/eduardo.ruiz/PycharmProjects/Datadex-Pokemon-Lab/assets/custom.css)
- Register `PokemonSolid` `@font-face`
- `.pokemon-title` styling (yellow text, blue outline/shadow, letter-spacing)
- Card hover effects (subtle `box-shadow` transition)
- Body background gradient (dark navy → slate)
- Smooth transitions on all interactive elements
- Responsive adjustments for 1024×768 tablet viewport

#### [NEW] [assets/pokemon_solid.ttf](file:///Users/eduardo.ruiz/PycharmProjects/Datadex-Pokemon-Lab/assets/pokemon_solid.ttf)
- Pokémon-themed font file (needs to be sourced/provided)

> [!WARNING]
> The `pokemon_solid.ttf` font file must be provided by you or sourced from a free font site. I can use a freely available alternative (e.g., from [DaFont](https://www.dafont.com/pokemon.font)) or skip the custom font and use a fallback. **Please confirm your preference.**

---

## Verification Plan

### Automated Verification

1. **Data pipeline check** — after running `fetch_api_data.py`:
   ```bash
   python -c "import pandas as pd; df = pd.read_parquet('data/pokemon.parquet'); print(df.shape, df.dtypes)"
   ```
   Expected: [(151, 12)](file:///Users/eduardo.ruiz/PycharmProjects/Datadex-Pokemon-Lab/main.py#1-3) with correct types

2. **Import & function smoke test**:
   ```bash
   python -c "from data_manager import load_and_clean_data; df = load_and_clean_data(); print(df.columns.tolist(), len(df))"
   python -c "from visualizations import create_radar_chart, create_type_leaderboard, create_scatter_plot; print('All imports OK')"
   ```

3. **App startup test**:
   ```bash
   python app.py &
   sleep 3
   curl -s http://127.0.0.1:8050 | head -20
   kill %1
   ```
   Expected: HTML containing `"Data-Dex"` in the response

### Browser Verification (via browser tool)

4. **Full interactive test** — launch `python app.py`, open `http://127.0.0.1:8050` in the browser:
   - Verify the title renders with Pokémon styling
   - Select 2 Pokémon in the MultiSelect → confirm radar chart draws two polygons
   - Change the stat selector in Type Leaderboard → confirm bar chart updates
   - Change X/Y axis in Outlier Hunt → confirm scatter plot updates
   - Resize viewport to 1024×768 → confirm responsive grid stacks correctly

### Manual Verification (by you)

5. **Visual quality check** — after the app is running, open `http://127.0.0.1:8050` in your browser:
   - Confirm the Pokémon title font looks correct
   - Check that cards have hover effects and the layout feels polished
   - Try selecting different Pokémon and verify artwork + progress bars update
   - Test on a tablet-sized window if possible
