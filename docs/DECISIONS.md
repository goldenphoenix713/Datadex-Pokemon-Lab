# Data-Dex: Ultimate Stat Lab — Architectural Decisions

This document outlines the technical design and rationale behind the Data-Dex application.

## High-Level Architecture

The app follows a **modular Dash architecture** to separate data fetching, management, visualization, and UI layout.

### Technical Stack

1. **Dash & Plotly:** Chosen for fast prototyping of interactive, web-based data visualizations entirely in Python.
2. **Dash Mantine Components (DMC) 0.14:** Provides a premium, responsive UI framework. Version 0.14 was chosen for compatibility with the project's requirement for a modern React 18 base.
3. **Python 3.12:** Utilized for modern language features and performance.
4. **uv:** Used for dependency management due to its extreme speed and reliability compared to standard pip.

---

## Technical Decisions

### 1. Data Strategy: Offline Parquet

- **Decision:** We use an offline `.parquet` file ([data/pokemon.parquet](file:///Users/eduardo.ruiz/PycharmProjects/Datadex-Pokemon-Lab/data/pokemon.parquet)) instead of calling PokéAPI at runtime.
- **Rationale:** Classroom environments often have unreliable network latency. By scraping all 1,350 forms once and storing them in a compressed, strictly-typed columnar format, we ensure **instant load times** and zero runtime API dependency.

### 2. Form Inclusion Criteria

- **Decision:** The dataset includes all variety forms (Mega, Alolan, Galar, etc.) that have **statistical or type differences**.
- **Rationale:** To provide a scientifically accurate lab, kids need to see how form changes (like Mega Evolution) actually impact data distributions.

### 3. Visualization Design

- **Radar Charts:** Used for multi-dimensional comparison. We enforced a **static radial range [0, 160]** so that the size of the polygons is mathematically comparable between different Pokémon.
- **Leaderboard Avg Line:** Added a global average line to the Type Leaderboard. This teaches students the concept of a "baseline" or "control" when evaluating group data.

### 4. UI Aesthetics

- **Decision:** Pokémon-themed styling with high-contrast yellow/blue and custom fonts.
- **Rationale:** High engagement is critical for the 3rd–5th grade audience. The app uses "glassmorphism" (blurred transparent backgrounds) and card hover effects to feel like a premium laboratory tool.
