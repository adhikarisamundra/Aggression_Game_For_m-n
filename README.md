# Aggression: Nexus Engine
**A generalized m×n implementation of the Aggression board game with probabilistic AI, terrain-weighted combat mechanics, and a multithreaded Monte Carlo simulation lab**

*Research project — Department of Mathematics, Berea College (May–Oct 2025)*

---

## Overview

This project implements and extends the combinatorial board game **Aggression** to arbitrary m×n grid dimensions, developed as part of a research assistantship analyzing win probabilities, strategic outcomes, and first-mover advantage under varying board conditions and player strategies.

The core research questions driving the project:

- How does board geometry (m×n dimensions) affect win probability and first-mover advantage?
- Which starting positions maximize expected win rate, and how does this vary with opponent strategy?
- Can Monte Carlo Tree Search meaningfully outperform greedy heuristics in this game class, and at what computational cost?

The game runs entirely in the browser as a single HTML file — no build step, no dependencies beyond a CDN-hosted Three.js.

---

## Game Rules

Aggression is a two-player territory game played on a grid:

1. **Placement phase** — players alternate deploying units onto empty grid sectors, distributing a fixed reserve of n² units across the board
2. **Combat phase** — beginning with the first mover, players attack adjacent enemy sectors; a sector falls if the attacker's combined adjacent power exceeds the defender's unit count (adjusted for terrain); the phase ends when both players pass consecutively
3. **Victory** — the player controlling more sectors at game end wins

---

## Technical Architecture

The project is structured in seven modules within a single self-contained file:

### `Topo` — Topological Board Generator
Procedurally generates elevation maps using layered sinusoidal functions (4 octaves of frequency doubling, weighted 0.50 / 0.25 / 0.12 / 0.06), producing deterministic but varied terrain. Terrain is classified into four types — **Valley**, **Plains**, **Hills**, **Mountain** — each applying a defense bonus modifier (`−0.1` to `+0.30`) to combat resolution. Also implements Dijkstra's algorithm for strategic path cost analysis, weighting traversal cost by elevation differential between adjacent cells.

### `State` — Game State Manager
Manages the full mutable game state: grid ownership and unit counts, player reserves, turn order, phase transitions. Combat power is computed as the sum of adjacent friendly unit counts, each divided by a terrain multiplier that penalizes uphill attacks and rewards downhill ones:

```
power(r,c,who) = Σ adjacent_friendly_count / max(0.5, 1 + (def_elev − att_elev) × 0.5)
```

State serialization to typed arrays (`Int16Array`, `Float32Array`) enables efficient transfer to Web Workers via the structured clone algorithm.

### `Renderer` — Three.js 3D Visualization
Renders the board in **isometric perspective** (Three.js `PerspectiveCamera`) or **top-down orthographic** view. Each sector is a terrain pillar whose height encodes elevation; owned sectors display a colored unit tower scaled to troop count, with per-frame sinusoidal pulse animation. Features include:

- Orbit controls (drag, zoom) via manual spherical coordinate camera updates
- Raycasting for click/hover cell selection
- A **threat heatmap overlay** that color-codes each sector by `P2_power / (P1_power + P2_power)`, interpolating cyan → gold → red

### `Engine` — Game Logic Controller
Handles placement, combat resolution, phase transitions, and AI turn scheduling. AI moves are dispatched asynchronously — MCTS via a Web Worker, greedy inline — with a delay callback restoring UI control after each move. The greedy heuristic scores candidate placements by adjacency to friendly/enemy cells, proximity to board center, and terrain elevation.

### `MCTS` — Monte Carlo Tree Search (Web Worker)
Implemented inside an inline Web Worker (embedded as a `<script type="text/plain">` blob to avoid CORS issues). The search runs UCB1-guided tree expansion with random rollouts capped at 80 moves. During rollout, attack moves are selected with 75% probability toward the highest-margin target (exploitation) and 25% randomly (exploration). Default: **350 iterations per move** in live play.

### `SimDashboard` — Multithreaded Hyper-Simulation Lab
The core research tool. Spawns `navigator.hardwareConcurrency − 1` parallel Web Workers, distributes a user-specified game count (up to 5,000) across them, and aggregates results to produce:

- **P1 / P2 win rates and draw rate**
- **First-mover advantage** (win rate conditional on moving first, excluding draws)
- **Average game length** in turns
- **Starting position win-rate heatmap** — a canvas-rendered n×n grid where each cell's color encodes the win rate achieved when P1 placed their first unit at that position, computed from all games where that cell was P1's opening move

Workers report progress in batches (default 25 games/batch) via `postMessage`, enabling a live progress bar without blocking the main thread.

### `Archive` — Game History
Persists results to `localStorage` (up to 200 records), viewable in an in-game modal.

---

## Key Findings from Simulation Runs

Preliminary simulation results (greedy vs. greedy, 6×6 board, n=500 games):

- First-mover advantage is measurable but moderate (~54–57% win rate), consistent with theoretical predictions for symmetric two-player zero-sum games with positional asymmetry
- Starting positions in the **center-adjacent ring** (distance 1–2 from center) outperform corner positions by roughly 8–12 percentage points in win rate
- **Mountain sectors** (elevation ≥ 0.75, defense bonus +0.30) create durable defensive anchors; greedy AI consistently over-invests in contesting them relative to optimal play
- MCTS at 350 iterations wins approximately 62–65% against the greedy heuristic on 6×6, with diminishing returns beyond ~200 iterations on this board size

---

## How to Run

Open `index.html` in any modern browser. No server required. The inline Web Worker approach (blob URL) works in Chrome, Firefox, and Edge without CORS restrictions.

**Configuration options at startup:**
- Grid rows / columns (3–12 each)
- Units per side (defaults to n²)
- View mode: isometric 3D or top-down
- Opponent: Human, Greedy AI, or MCTS AI

**Hyper-Simulation Lab** is accessible from the start screen without launching a game — configure grid size, game count, and strategy matchup, then run.

---

## Dependencies

- [Three.js r128](https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js) — 3D rendering (CDN)
- [Google Fonts](https://fonts.google.com/) — Orbitron, Rajdhani, Share Tech Mono (CDN)
- No build tools, no npm, no backend

---

## Repository Context

This was developed as part of a research assistantship in the Department of Mathematics at Berea College, contributing to ongoing work on combinatorial game theory, heuristic strategy analysis, and simulation-based probability estimation. The primary academic contribution is the generalization of the fixed-board Aggression game to variable m×n geometry and the Monte Carlo framework for empirically characterizing the strategy space.
