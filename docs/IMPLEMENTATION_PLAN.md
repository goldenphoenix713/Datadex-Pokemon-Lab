# Data-Dex Pokémon Lab: Implementation Plan

Based on the findings in [`technical_document.md`](./technical_document.md), this plan groups improvements into logical, sequential phases. Phases are ordered so that earlier phases lay the groundwork for later ones—and every phase can be independently shipped and tested.

---

## Phase 1: Data Pipeline — Eliminate Runtime HTTP Calls

**Goal:** Embed all static derivable data into the Parquet file at build time, so the running app never needs to make an outbound HTTP request just to look up metadata.

**Why first:** This is the highest-ROI change. It directly eliminates blocking network I/O that affects every user interaction with the Detail card. It also simplifies downstream code.

### 1.1 — Add `Has_Shiny` column to `fetch_api_data.py`

**Files:** [`fetch_api_data.py`](../fetch_api_data.py)

- In `fetch_single_pokemon`, after the species data is fetched, make a `requests.head()` call to `SHINY_ARTWORK_URL/{id}.png` and store the result as a boolean `Has_Shiny` field in the returned dictionary.
- This is already done in a thread pool, so the cost is absorbed by the parallel fetch.
- Add `Has_Shiny` to the PyArrow schema and `pq.write_table` output.

**Verification:** Run `fetch_api_data.py`, open the resulting Parquet in DuckDB (`SELECT id, Has_Shiny FROM 'data/pokemon.parquet' LIMIT 20`), and confirm the column is present and populated.

### 1.2 — Propagate `Has_Shiny` through `data_manager.py`

**Files:** [`data_manager.py`](../data_manager.py), [`src/data.py`](../src/data.py)

- In `load_and_clean_data`, pass `Has_Shiny` through to `final_columns`.
- In `src/data.py`, ensure `Has_Shiny` is available in `name_to_pokemon` entries.

### 1.3 — Remove `has_shiny_artwork()` call path from `callbacks_details.py`

**Files:** [`src/callbacks_details.py`](../src/callbacks_details.py), [`data_manager.py`](../data_manager.py)

- Replace `_cached_has_shiny(p_id)` with `p_data.get("Has_Shiny", False)` — a pure dictionary lookup with zero I/O.
- Remove `_cached_has_shiny` helper, `has_shiny_artwork` import, and the `diskcache`-backed `registry_cache` in `data_manager.py` (it only exists to cache the shiny HTTP check).

**Estimated Time:** 1.5–2 hours
**Complexity:** Low

---

## Phase 2: Asset Fetching — Move Image Loading to the Browser

**Goal:** Stop downloading images on the Dash server. Instead, expose direct CDN URLs to the browser so it fetches, caches, and displays them natively—the browser is purpose-built for this.

**Why second:** Builds on Phase 1 (shiny toggle logic is already cleaned up). Eliminates the last remaining blocking synchronous requests in `callbacks_details.py`.

### 2.1 — Stream artwork URLs directly from the CDN

**Files:** [`data_manager.py`](../data_manager.py), [`src/callbacks_details.py`](../src/callbacks_details.py)

- For **official artwork**: the `Image_URL` column already stores `assets/images/{id}.png`. When a local file exists, use it; otherwise fall back to the `OFFICIAL_ARTWORK_URL` CDN string directly (e.g. `https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/{id}.png`).
- Update `update_pokemon_image` to return the CDN URL instead of calling `ensure_pokemon_image`. Use `dmc.Image`'s `fallbackSrc` prop to show a placeholder if the URL fails.
- Remove `ensure_pokemon_image` and `ensure_pokemon_sprite` from the hot callback path. Retain them only in a one-time pre-warming script if desired.

### 2.2 — Stream Pokémon cries from CDN

**Files:** [`src/callbacks_details.py`](../src/callbacks_details.py)

- `cry_src` already uses `POKEAPI_CRY_URL` directly — confirm no path through `ensure_pokemon_cry` is triggered at runtime for new Pokémon. If it is, remove it and rely solely on the CDN URL in the `<audio>` element.

### 2.3 — Deprecate sync asset helpers in `data_manager.py`

- Mark `ensure_pokemon_image`, `ensure_pokemon_sprite`, `ensure_pokemon_cry` as deprecated or move them to a standalone `scripts/prefetch_assets.py` utility that can be run offline to warm the local cache.

**Estimated Time:** 2–3 hours
**Complexity:** Medium

---

## Phase 3: Python Performance — Vectorize PyArrow Operations

**Goal:** Replace per-row Python loops in `data_manager.py` with native vectorized operations, reducing startup data-loading time.

**Why third:** Lower urgency (dataset is ~1,000 rows so user-visible impact is minor), but improves code quality and eliminates the "Python loop over Arrow array" anti-pattern.

### 3.1 — Vectorize `apply_name_rules`

**Files:** [`data_manager.py`](../data_manager.py)

- Convert the Arrow column to a Pandas Series, apply `.str.replace()` with regex in a vectorized chain, then convert back with `pa.Array.from_pandas()`.
- Alternatively, implement with a sequence of `pc.replace_substring_regex` calls on the Arrow array directly (no Python-level loop).

```python
# Example: Mega prefix normalization
names_pd = table["Name"].to_pandas()
mask_mega = names_pd.str.contains(r"(?i) Mega ", regex=True) | names_pd.str.endswith(" Mega")
names_pd[mask_mega] = "Mega " + names_pd[mask_mega].str.replace(
    r"(?i) Mega$| Mega ", " ", regex=True
).str.strip()
clean_names = pa.Array.from_pandas(names_pd)
```

### 3.2 — Vectorize `get_region`

**Files:** [`data_manager.py`](../data_manager.py)

- Use `pc.case_when` with comparison predicates, or build the mapping from a Pandas Series using `pd.cut`:

```python
import pandas as pd
id_pd = table["#"].to_pandas()
regions_pd = pd.cut(
    id_pd,
    bins=[0, 151, 251, 386, 493, 649, 721, 809, 898, 1025, float("inf")],
    labels=["Kanto", "Johto", "Hoenn", "Sinnoh", "Unova", "Kalos", "Alola", "Galar", "Paldea", "Unknown"],
    right=True,
).astype(str)
regions = pa.Array.from_pandas(regions_pd)
```

**Estimated Time:** 1.5–2 hours
**Complexity:** Medium

---

## Phase 4: UI Responsiveness — Client-Side Callbacks

**Goal:** Offload pure UI-state mutations to the browser using Dash `clientside_callback`, removing unnecessary server round-trips for interactions that have no Python-side logic.

**Why fourth:** Most impactful for UX polish once the data pipeline and asset loading are clean. Requires more careful analysis of which callbacks are truly stateless.

### 4.1 — Audit callbacks for client-side eligibility

**Files:** [`src/callbacks_charts.py`](../src/callbacks_charts.py), [`src/callbacks_discovery.py`](../src/callbacks_discovery.py), [`src/callbacks_team.py`](../src/callbacks_team.py)

- Review each `@callback` and flag those whose logic is pure data transformation on inputs already available in the browser (i.e., reading from a `dcc.Store`).
- Candidates: Reset Filters button resetting multiple `dcc.Store`/component values, team display clearing, stat-slider tooltips.

### 4.2 — Convert eligible callbacks to `clientside_callback`

**Files:** As above + new `assets/callbacks.js` (or extend existing `assets/` JS)

- For each eligible callback, implement the equivalent JavaScript function and register it with `dash.clientside_callback`.
- Example: "Reset All Filters" — read default values from constants baked into a `dcc.Store` at layout time, then update component values purely client-side.

**Estimated Time:** 3–4 hours
**Complexity:** Medium–High

---

## Phase 5: Data Fetch Script Hardening (Nice-to-Have)

**Goal:** Make `fetch_api_data.py` safer and faster to run for incremental updates.

**Why last:** Run infrequently and offline; low user-facing urgency.

### 5.1 — Thread-safe `EVOLUTION_CHAIN_CACHE`

**Files:** [`fetch_api_data.py`](../fetch_api_data.py)

- Wrap dictionary reads/writes with a `threading.Lock` to prevent data races under `ThreadPoolExecutor`.

```python
import threading
_evo_cache_lock = threading.Lock()

def fetch_evolution_members(url: str) -> List[str]:
    with _evo_cache_lock:
        if url in EVOLUTION_CHAIN_CACHE:
            return EVOLUTION_CHAIN_CACHE[url]
    ...
    with _evo_cache_lock:
        EVOLUTION_CHAIN_CACHE[url] = members
    return members
```

### 5.2 — Delta-update / incremental fetch

**Files:** [`fetch_api_data.py`](../fetch_api_data.py)

- Load the existing Parquet (if it exists), extract the set of already-fetched Pokémon IDs, and skip those in the API fetch loop.
- Use a `--force` CLI flag to trigger a full refresh when needed.

**Estimated Time:** 3–5 hours
**Complexity:** Medium

---

## Summary Table

| Phase | Item | Priority | Complexity | Est. Time | Est. ROI |
| ----- | ---- | -------- | ---------- | --------- | -------- |
| 1 | Pre-cache `Has_Shiny` in Parquet | 🔴 High | Low | 1.5–2h | Very High |
| 2 | Stream assets via CDN URLs | 🔴 High | Medium | 2–3h | High |
| 3 | Vectorize PyArrow operations | 🟡 Medium | Medium | 1.5–2h | Medium |
| 4 | Client-side callbacks for UI state | 🟡 Medium | Medium–High | 3–4h | Medium |
| 5 | Harden `fetch_api_data.py` | 🟢 Low | Medium | 3–5h | Low |
