# SQLMesh Tutor — Product & Technical Spec (v0.1, draft)

**Status:** Draft for discussion. Not yet approved for implementation.
**Author:** Michael (mdaytn@gmail.com), drafted with Claude
**Date:** 2026-08-04

## 1. Summary

SQLMesh Tutor is a standalone, browser-based website that looks and feels like a terminal running the `sqlmesh` CLI. It teaches people how SQLMesh actually works — not by describing it, but by letting them run real commands against a real dataset and watch, through synchronized animated diagrams, what SQLMesh is doing under the hood (snapshotting, virtual environments, promotion). Along the way, it calls out — inline, not as a separate document — how the same moment would look in dbt, for the significant fraction of the audience that's evaluating SQLMesh against a dbt background.

It is a single, guided, linear tutorial for v1 (not an open sandbox), built as a static site with no backend: DuckDB-WASM executes real SQL, and a TypeScript reimplementation of SQLMesh's core mechanics (fingerprinting, snapshots, virtual environments, plan diffing) drives everything that isn't raw SQL execution.

## 2. Problem statement

SQLMesh's hardest-to-explain ideas — virtual environments, zero-copy promotion, snapshot fingerprinting — are exactly the ideas that most differentiate it from dbt and most justify switching. But they're abstract until you've felt the "wait, it didn't recompute anything?" moment yourself. Reading docs or a comparison table doesn't produce that moment. Running the CLI against a real project does — but that requires installing a project, a warehouse or DuckDB, and enough context to know what to run and why.

SQLMesh Tutor closes that gap: zero install, one URL, a guided path to the "aha," and an explicit bridge for anyone arriving with dbt muscle memory.

## 3. Goals / non-goals

**Goals (v1):**
- Teach the `init → plan → apply → promote` loop and, specifically, why virtual environments make dev environments free and promotion instant.
- Work for both audiences equally: people with zero SQLMesh/dbt background, and dbt users translating what they already know.
- Feel real: SQL execution and data results are real (DuckDB-WASM); SQLMesh's own mechanics are re-derived with real logic, not scripted strings.
- Ship as a static site with no backend, no accounts, no ops burden.

**Non-goals (v1):**
- Not a general-purpose sandbox or REPL — no free-form exploration outside the guided chapters.
- Not a full CLI reimplementation — only the commands needed for the flagship story are wired up (§7).
- Not a replacement for `docs/comparisons.md` or the real docs — it complements them.
- Not multi-user, not accounts, not cross-device progress sync.

## 4. Audience & positioning

Two audiences, one narrative:
1. **New users** with no prior transformation-tool background, learning SQLMesh's model from scratch.
2. **dbt users** evaluating SQLMesh, mapping new concepts onto what they already know.

Neither audience is primary; the tutorial is written so the core narrative works standalone, with dbt comparisons layered in as optional, skippable callouts (§8) rather than a fork in the content.

## 5. Product concept & naming

Placeholder name: **SQLMesh Tutor**.

Prior art worth knowing before settling on a name — other OSS communities that built a similar "learn the tool by playing with a simulated version of it" site:

| Name | Domain/tool it teaches | Notable pattern |
|---|---|---|
| [Learn Git Branching](https://learngitbranching.js.org/) | Git | Animated commit-graph that reacts live to real git commands; the closest analog to what's proposed here |
| [Flexbox Froggy](https://flexboxfroggy.com/) | CSS Flexbox | Puzzle-per-level, visual feedback, no login |
| [Explain Shell](https://explainshell.com/) | POSIX shell / man pages | Not a tutorial, but the "annotate each token of a real command" pattern is relevant to §9 |
| [Katacoda](https://killercoda.com/) (now Killercoda) | Many (Docker, k8s, etc.) | Real in-browser terminal sandboxes, scenario-based |
| [PostgreSQL Exercises](https://pgexercises.com/) | SQL/Postgres | Task-based challenges against a real embedded DB |
| [SQL Murder Mystery](https://mystery.knightlab.com/) | SQL basics | Narrative wrapper around real queries — a model for making the flagship story feel like a story, not a checklist |
| [Vim Adventures](https://vim-adventures.com/) | Vim | Game skin over real tool semantics |
| [CSS Diner](https://flukeout.github.io/) | CSS selectors | Minimal, level-based, no fluff |

If a new name is wanted instead of the placeholder, options in the same register: **Learn SQLMesh** (directly mirrors the most relevant prior art), **SQLMesh Playground**, **Mesh Academy**, **PlanIt** (pun on `sqlmesh plan`). Recommend deciding this after a working prototype exists — it's cheap to change and easy to bikeshed prematurely.

## 6. Tone & voice

Friendly and a little playful — approachable, occasionally funny, encouraging (closer to Codecademy/Flexbox Froggy than to reference documentation). This serves both audiences: it keeps first-timers from bouncing off unfamiliar jargon, and it doesn't read as try-hard marketing to skeptical dbt evaluators. Error states and dbt callouts in particular should stay factual and confident rather than snarky — the playfulness lives in narration and success states, not in "dbt bad" jokes.

## 7. Curriculum (v1)

One flagship storyline, two chapters. Everything else is named and deferred (§13).

### Chapter 1 — Fundamentals: `init`, `plan`, `apply`

Teaches the base loop before environments make sense:
1. `sqlmesh init` scaffolds a project (pre-seeded with the sushi example, §10).
2. Edit a model file (e.g. `customer_revenue_by_day.sql`) in an embedded editor pane.
3. Run `sqlmesh plan` — read a real plan diff (added/modified models, breaking vs. non-breaking classification).
4. Run `sqlmesh plan` again to apply it — watch the animated diagram (§9) show the physical table getting built.

### Chapter 2 — Virtual Environments & Promotion (the flagship "aha")

Builds directly on Chapter 1's project state:
1. Make a change and run `sqlmesh plan dev` — a **virtual** dev environment is created instantly; the diagram shows a new environment layer pointing at (mostly) the *same* physical tables as prod, with only the changed model's snapshot materialized fresh.
2. Query through the dev environment and see the change live, with the diagram highlighting that no full-warehouse rebuild happened.
3. Run `sqlmesh plan prod` to promote — the diagram shows this as a pointer swap (environment view redefinition), not a recompute, with a visible "0 rows moved" moment as the payoff.
4. A closing beat ties it back explicitly to the dbt mental model: "in dbt, this step would have re-run the whole warehouse."

This chapter is the point of the whole product; Chapter 1 exists to make it legible.

## 8. dbt comparison mechanism

**Inline "dbt equivalent" callouts**, attached to individual tutorial steps, collapsed by default (a small toggle/badge, not a wall of text). Each callout: what the equivalent dbt command/pattern is, and the one sentence of *why* it differs — sourced from and consistent with the existing `docs/comparisons.md` in this repo, which already has well-developed, accurate framing for environments, incremental models, and promotion. That doc is the source of truth for comparison *content*; this product is a new way to *deliver* a subset of it experientially.

Example (Chapter 2, step 3):
> **dbt equivalent:** There isn't a real one — dbt has no concept of promotion. The closest analog is re-running `dbt run --target prod`, which recomputes everything. That's the gap this step is demonstrating.

Dedicated comparison chapters and a side-by-side dual-terminal mode were both considered and explicitly deferred (§13) — they're heavier to build and better suited to a v2 once the core narrative is validated.

## 9. Visual guidance

**Animated diagram alongside the terminal**, synced to command execution — this is the product's main differentiator from just reading docs. Layout: terminal pane on one side, live diagram on the other; every command that changes SQLMesh state animates the diagram in step with the terminal output finishing.

What the diagram shows, concretely:
- **Nodes** = models (from the sushi DAG actually in use, §10), grouped visually by environment (prod vs. dev).
- **`plan`** highlights which nodes are new/modified/downstream-affected, colored by breaking/non-breaking classification, before anything is applied.
- **`apply`** animates physical table creation for only the affected nodes — everything else visibly stays untouched, which is the point.
- **Virtual environment creation** (`plan dev`) draws a new environment layer whose unmodified nodes are rendered as arrows *pointing back at* the existing prod physical tables (shared, not copied), and only the changed node gets a new physical table.
- **Promotion** (`plan prod`) animates the prod layer's pointers swapping to the dev snapshot's tables — deliberately *not* re-drawing the tables themselves, to make "no recompute" visible rather than asserted.

This is the single largest scope/complexity item in the spec and should be prototyped early (§14).

## 10. Sample project

Use SQLMesh's own `examples/sushi` project (this repo), specifically a curated subset of its models for pacing — likely `customers`, `orders`, `items`, `order_items`, and `customer_revenue_by_day`, which is small enough to diagram clearly but has real upstream/downstream dependency structure. Reusing sushi keeps the tutorial's "truth" aligned with the example already used in SQLMesh's docs and tests, rather than maintaining a second bespoke schema.

## 11. Architecture

**No backend. Static site, entirely client-side.**

- **DuckDB-WASM** runs real SQL against the sushi subset, seeded into the browser on load. Query results, row counts, and table contents shown in the tutorial are real, not scripted.
- **A TypeScript "SQLMesh core-lite"** reimplements, with real logic (not canned strings), the SQLMesh-specific mechanics needed for the flagship story:
  - Snapshot fingerprinting (hash of model definition + upstream fingerprints, mirroring `sqlmesh/core/snapshot`'s approach closely enough to be honest, not necessarily byte-for-byte identical to the Python implementation).
  - Breaking vs. non-breaking change categorization for the plan diff.
  - Virtual environment modeling: environments as named sets of pointers to physical snapshot tables, matching SQLMesh's actual environment/promotion semantics.
  - Plan diff generation (added/modified/removed, categorized).
- This hybrid was chosen over the alternatives on the table (real Python SQLMesh via Pyodide, or a real backend running actual `sqlmesh`) because it gets authentic data behavior and authentic-*feeling* mechanics without a backend to operate or the bundle-size/compatibility risk of running the full Python package in-browser. See §15 for the risk this carries.

### Command surface (v1)

Deliberately minimal — just enough to tell the flagship story, not a general CLI:
- `sqlmesh init`
- `sqlmesh plan` / `sqlmesh plan dev` / `sqlmesh plan prod` (apply is folded into the plan confirmation step, matching real SQLMesh UX)
- A lightweight embedded file tree + code editor for viewing/editing model files (not simulated `ls`/`cat`/`cd` as shell commands — the terminal is for `sqlmesh` commands specifically, file browsing is its own UI affordance)

Everything else (`sqlmesh test`, `sqlmesh audit`, `sqlmesh diff`, etc.) is out of scope for v1 and listed under roadmap (§13).

## 12. Progress & persistence

**Local browser storage only** (`localStorage`), no accounts, no backend, fully anonymous. Progress persists per-browser across visits; there is no cross-device sync. This matches the "no backend" architecture decision and the scope of a short (target: 10–20 minute), single-session-oriented tutorial.

## 13. Roadmap / explicitly deferred

Named here so they're not silently forgotten, not committed to:
- **Incremental models & intervals** — flagged as a strong second "aha" moment for dbt users (data-gap/data-leakage handling has no dbt equivalent); good candidate for the first post-v1 chapter.
- **Snapshots & fingerprinting deep dive** — a chapter that goes under the hood of what Chapter 2 shows visually but doesn't fully explain.
- **Testing & CI/CD bot workflow** — `sqlmesh test`, and the plan-in-PR flow mirroring the real GitHub bot (`sqlmesh/integrations/github`).
- **Free-form sandbox mode** — open terminal against the sushi project outside the guided chapters, once the guided path is validated.
- **Dedicated dbt-comparison chapters and side-by-side dual-terminal mode** — heavier comparison UX than the inline callouts in §8.
- **Broader command surface** — `sqlmesh diff`, `sqlmesh audit`, etc., for a less scripted feel once the core is solid.

## 14. Tech stack

**React + TypeScript + Vite**, deployed as a static site (Vercel/Netlify/Cloudflare Pages/GitHub Pages all viable — no server-side requirement). This matches the stack conventions already used in `web/client/` in the SQLMesh monorepo, though this project lives in its own **new, standalone repository**, not inside `sqlmesh/`, so it can move independently of SQLMesh's own release cadence.

## 15. Risks & open questions

- **Fidelity risk (biggest one):** the TypeScript "core-lite" reimplementation of fingerprinting/diffing must stay honest to real SQLMesh behavior, or the tutorial teaches a subtly wrong mental model — worse than not existing. Mitigation: have it reviewed against `sqlmesh/core/snapshot/` and `sqlmesh/core/plan/` directly, and treat any divergence as a bug, not a simplification.
- **Diagram complexity:** the animated diagram (§9) is the product's core value and its largest unknown in build cost. Recommend prototyping it standalone, against static/fake data, before wiring up DuckDB-WASM or the plan engine.
- **DuckDB-WASM constraints:** need to confirm the chosen sushi model subset's SQL (including any Python models like `orders.py`/`waiters.py`) is expressible as plain SQL for the browser runtime, since DuckDB-WASM won't execute SQLMesh's Python model path.
- **Drift over time:** as real SQLMesh's plan/environment semantics evolve, the reimplemented core-lite can silently drift out of sync. Worth deciding ownership/maintenance cadence once this ships.

## 16. Success criteria (proposed, needs owner sign-off)

- A first-time visitor completes both chapters without external help.
- A dbt-background visitor can articulate, unprompted, why promotion in SQLMesh doesn't recompute data.
- No backend costs; hosting is effectively free at any realistic traffic level.

## 17. Immediate next steps

1. Prototype the animated diagram (§9, §15) against static fake state — de-risk the highest-uncertainty piece first.
2. Spike DuckDB-WASM against the chosen sushi model subset to confirm it runs as-is in-browser.
3. Draft the exact copy/script for Chapter 1 and Chapter 2, cross-checked against `docs/comparisons.md` for the dbt callouts.
4. Stand up the new repo with the React/TS/Vite skeleton and static hosting pipeline.
