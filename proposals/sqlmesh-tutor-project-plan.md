# SQLMesh Tutor — Execution Plan

**Status:** Draft. Companion to `sqlmesh-tutor-spec.md` — read that first for the product rationale; this doc is the "how and in what order."
**Date:** 2026-08-04

## How to use this doc

Phases are sequenced by dependency, not by calendar time — no target date exists yet (see Q11). Each phase has a checklist. Some checklists have unresolved questions blocking them; those are called out inline and listed together in §1 so nothing gets started on a guess that turns out wrong later.

## 1. Outstanding questions

Organized by how much they block. Answer the "blocking" ones before the phase they gate; the rest can be decided as you get there.

### Blocking

1. **Branding/trademark.** Is using "SQLMesh" in the product name and terminal chrome okay for an independent, non-`sqlmesh`-org project? Worth a quick check with the SQLMesh/Tobiko maintainers before settling on a public name — better to find out now than after launch copy is written. Doesn't block *building* the prototype, but should resolve before Phase 7 (and ideally before Phase 5 content-writing locks in the name everywhere).
2. **Repo/license/ownership.** New repo under your personal account or a new org? License (MIT, matching SQLMesh's own, or something else)? Blocks Phase 1.
3. **Positioning.** Is this meant to eventually get linked from SQLMesh's real docs/README (e.g. from `docs/comparisons.md`), or stay fully independent? Affects how much accuracy review is worth chasing from actual SQLMesh maintainers, and whether it's worth coordinating timing with them at all.
4. **Diagram engineering approach.** Custom SVG/canvas, React Flow, or Framer Motion driving DOM elements? This is the highest-uncertainty, highest-value piece of the product (spec §9/§15) — worth a short bake-off, not a guess. Blocks Phase 4, and ideally gets picked during the Phase 0 spike.
5. **Sushi model subset.** Spec proposes `customers`, `orders`, `items`, `order_items`, `customer_revenue_by_day` — but `orders` and a few others exist as `.py` models in `examples/sushi/models/` (`orders.py`, `waiters.py`, `order_items.py`), and DuckDB-WASM can't run SQLMesh's Python model path. Need to confirm the final subset is pure SQL, or plan to hand-port a Python model to SQL for tutorial purposes. Blocks Phase 0/1.

### Non-blocking (decide when you get there)

6. **Terminal UI approach.** A real terminal emulator (e.g. xterm.js) vs. a lighter custom "looks like a terminal" input box — reasonable to default to the lighter option since the command surface is intentionally small (spec §11), but flagging as a real choice, not an assumption.
7. **Fingerprinting fidelity review.** Spec §15 says the TS reimplementation should be checked against `sqlmesh/core/snapshot/` and `sqlmesh/core/plan/` — worth deciding now who actually does that check (you, a future agent session, or a SQLMesh maintainer) so it doesn't quietly get skipped.
8. **Mobile/responsive support.** Terminal-pane + diagram-pane side by side wants real screen width. Fine to explicitly scope v1 as desktop-only with a "come back on a bigger screen" message rather than build responsive layout for it — but should be a decision, not a default.
9. **Accessibility bar.** Terminal-styled UIs are typically poor for screen readers. Decide the v1 bar (e.g. "keyboard-navigable, diagram states have text alternatives" vs. "explicitly out of scope, revisit post-launch").
10. **Analytics.** Fully none (matches the "no backend" architecture cleanly), or a privacy-friendly client-side option (Plausible/Fathom) to see where people drop off in the funnel? Useful signal for whether the tutorial is working, purely optional.
11. **Timeline.** No target date exists yet. If there's an event or launch window in mind (e.g. a conference, a SQLMesh release), worth stating so Phase sequencing can be compressed or reordered around it.
12. **Build resourcing.** Is this solo, with collaborators, or do you want a future Claude Code session/agents to actually scaffold and build the repo? Determines whether Phase 1 is "you set up the repo" or "ask Claude to do it in a fresh session against the new repo."

## 2. Phase 0 — Validation spikes (de-risk before full build)

Goal: prove the two riskiest assumptions before investing in the full build.

- [ ] Prototype the animated diagram against static/fake state (no DuckDB, no engine) — validate the *visual concept* alone (Q4)
- [ ] Confirm final sushi model subset is pure SQL, or hand-port what isn't (Q5)
- [ ] Spike DuckDB-WASM against that subset; sanity-check browser load time and bundle size
- [ ] Spike the TS fingerprinting/snapshot logic against real `sqlmesh plan` output (Python CLI, same subset) to check the reimplementation's honesty early, not after Phase 2 is fully built
- [ ] Get at least an informal read on Q1 (branding) before content/copy starts assuming a name

## 3. Phase 1 — Foundation

- [ ] Resolve repo/license/ownership (Q2) and create the standalone repo
- [ ] React + TypeScript + Vite skeleton
- [ ] Static hosting + CI (preview deploy per PR)
- [ ] Base layout: terminal pane + diagram pane split view
- [ ] DuckDB-WASM wired up with the finalized sushi subset as seed data

## 4. Phase 2 — Core simulation engine ("SQLMesh core-lite")

- [ ] Model representation: parse tutorial project files into an internal model graph
- [ ] Snapshot fingerprinting (content hash + upstream hash)
- [ ] Plan diff engine: added/modified/removed, breaking vs. non-breaking categorization
- [ ] Virtual environment model: environments as named pointer sets over physical snapshot tables
- [ ] Promotion logic: pointer-swap semantics, explicitly not a recompute
- [ ] Test suite comparing engine output against real SQLMesh behavior for the same model subset (built on the Phase 0 spike)

## 5. Phase 3 — Command surface & terminal UX

- [ ] `sqlmesh init` flow
- [ ] `sqlmesh plan` / `sqlmesh plan dev` / `sqlmesh plan prod`, output formatted to match real CLI conventions
- [ ] Terminal UI component per Q6
- [ ] File tree + embedded editor pane for model files
- [ ] Command history and minimal help/autocomplete scoped to the supported commands only

## 6. Phase 4 — Visual guidance / diagram system

- [ ] Build out the diagram library/approach chosen in Phase 0 (Q4)
- [ ] Node/edge model reflecting the sushi subset's real dependency DAG
- [ ] Animation: plan preview (new/modified/downstream nodes, breaking-change color coding)
- [ ] Animation: apply → physical materialization for affected nodes only, everything else visibly static
- [ ] Animation: virtual dev environment layer creation, unmodified nodes shown pointing at shared prod tables
- [ ] Animation: promotion pointer-swap — the "nothing recomputed" payoff moment
- [ ] Diagram state driven directly by engine state (Phase 2), not hand-tuned per tutorial step — keeps it honest as content changes

## 7. Phase 5 — Tutorial content & narrative

- [ ] Chapter 1 script: step sequence, copy, success/failure states
- [ ] Chapter 2 script: step sequence, copy, success/failure states
- [ ] Inline dbt callouts written and cross-checked against `docs/comparisons.md`
- [ ] Tone pass for friendly-but-not-snarky copy (spec §6) — especially the dbt callouts, which should read as factual, not dunking
- [ ] Progress indicator UI + `localStorage` persistence wired to chapter/step state

## 8. Phase 6 — Polish & QA

- [ ] Cross-browser check for WASM support (Chrome, Firefox, Safari at minimum)
- [ ] Performance pass: initial load time, WASM bundle size
- [ ] Execute the Q8 decision (real responsive support, or an explicit desktop-only notice)
- [ ] Execute the Q9 decision (accessibility bar)
- [ ] Informal usability pass with one person from each target audience — a SQLMesh newcomer and a dbt user — watched live, not just self-tested

## 9. Phase 7 — Launch

- [ ] Finalize name (pending Q1)
- [ ] Domain (if any) + hosting go-live
- [ ] Execute the Q10 decision (analytics)
- [ ] Announce — SQLMesh community channels, socials, and (only if Q3 lands as "yes, link it") a pointer from `docs/comparisons.md` or the SQLMesh README

## 10. Definition of done (v1)

- Both chapters completable end-to-end by a first-time user with no outside help.
- The diagram's portrayal of promotion/virtual environments has been checked against real SQLMesh behavior, not just against what "looks right."
- No backend, no accounts — reachable at a single static URL.
- Works in at least Chrome, Firefox, and Safari.
