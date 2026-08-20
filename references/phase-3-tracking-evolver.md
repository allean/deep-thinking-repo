# Phase 3 — Tracking Proposal and Evolver

Read this file when executing Phase 3 (tracking handoff) or when any Evolver trigger fires.

## Table of Contents
- Phase 3: Tracking Proposal (OPT-IN)
- Evolver: purpose and triggers (A-G)
- Evolver prompts (standard / lightweight / cross-session)
- Evolver output and user options

---

## Phase 3: Establish Tracking (OPT-IN — only when user says "开始跟踪"/"start tracking")

Convert analysis output into a trackable state entity. This is a LIGHTWEIGHT proposal generator — the `tracking` skill owns execution. Weak dependency: the proposal is a suggestion, not a binding contract.

**Hard gates:**
- **NEVER propose tracking unprompted unless the output contains trackable elements** — periodic data points (prices/ratios/valuations), signal/threshold systems, or decisions needing post-hoc validation. If none, skip Phase 3 entirely.
- **NEVER force tracking.** "稍后再说" and "不需要" are both valid terminal states. Default is no tracking.
- **The proposal is a draft.** User can add/remove/modify any metric before tracking begins.
- **Tracking entities are independent of analysis topics.** One analysis can spawn multiple tracking topics; one topic can reference multiple analyses (N:M via `references` in state.json).

**Procedure:**

1. From the Phase 2 output, extract candidates:
   - **Metrics:** periodic data points referenced in the analysis. Mark `auto` if fetchable via free public source; `manual` if requires human judgment.
   - **Milestones:** threshold triggers warranting re-analysis (e.g., "metric_X crosses below threshold_Y").
   - **Frequency:** infer from the analysis timeframe (monthly/quarterly/annual).

2. Present to the user:

   ```
   ## 跟踪建议

   基于分析结果，建议跟踪以下指标：

   **自动获取 (auto):**
   - metric_key: label — data_source

   **需要你手动填 (manual):**
   - metric_key: label

   **里程碑:**
   - description → trigger_condition

   **频率:** monthly/quarterly/annual

   以上是否OK？可以增删修改。
   ```

3. User confirms/modifies → save proposal and hand off to the `tracking` skill's init flow (reference the deep-thinking topic as source). Do NOT create the tracking entity here — Phase 3 only generates the proposal.

**Output file:** `<topic-slug>/tracking-proposal.json` — ephemeral, consumed by tracking init or discarded if user says no.

---

## Evolver: Course Correction Between Iterations

The iteration mechanism (v1 → v2 → ...) is inherently **exploitative**: each round deepens the PREVIOUS direction and never asks whether the direction itself is wrong. Analysis can march efficiently into a dead end — v2 produces more precise numbers for a strategy already failing in v1.

The Evolver is a mandatory gate between iterations. Its job is to challenge the trajectory before resources are spent on the next round.

### Triggers

**Trigger A: User requests new iteration** ("继续 v2", "再来一轮", "深化一下") → **Standard Evolver (full mode)**.

**Trigger B: New data overturns core premises** → **Lightweight Evolver (60-second mode)**, dispatched BEFORE any report revisions. Examples: "IELTS 实际是 4 不是 6" (English assumed improvable to 6.5); "排名实际是 20-30%"; "不移居" (relocation previously assumed possible).

**Trigger C: Related follow-up analysis** — user starts a NEW deep-thinking clearly related to a previous one (same slug prefix, same family/entity, same problem domain) → **Cross-Session Evolver**, dispatched BEFORE Phase 0.5.

**Trigger D: Major report revision** — revision changes >20% of key quantitative claims or re-ranks top-3 recommendations → 60-second check before applying: is this papering over a framing problem? Would a reframe beat a revision?

**Trigger E: Data Contradiction (auto — tracking data overturns premises):** a tracking check detects a metric crossing a defined threshold. Evolver reads `state.json`, identifies triggered milestone(s), proposes: "Tracking data shows [metric] triggered [condition]. Original assumptions may need re-examination. Start a new deep-thinking round?" If yes → new round with tracking data as Phase 0 input.

**Trigger F: Accumulated Review (auto — enough data for statistical review):** ≥6 periods accumulated. Evolver reads full history, computes signal accuracy (predicted vs actual per decision), proposes a retrospective/backtest analysis.

**Trigger G: Consecutive Anomaly (auto — consecutive signal failures):** ≥3 consecutive failed decisions. Evolver reads the decision log, identifies failing signal components, proposes a diagnostic/recalibration analysis.

**Phase 0 enhancement:** if a tracked topic exists for the analysis subject, read `state.json` history into Phase 0 Layer 1 (现状) automatically: "根据最近跟踪数据，[metric] 当前为 [value]，趋势 [上升/下降/稳定]。是否以此为基础进行分析？"

In ALL cases, Evolver output is discussed with the user before proceeding.

### Standard Evolver Prompt (Trigger A)

```
You are an Evolver. Your job is NOT to continue the current analysis direction.
Your job is to question it.

Read ALL outputs from all previous rounds. Then answer:

1. CONVERGENCE DIAGNOSIS
   - Is each round producing diminishing returns?
   - Are we getting more precise about a failing direction?
   - Is there evidence the current framing is exhausted?

2. FRAMING CHALLENGE
   - What assumptions has every round accepted without question?
   - What would the analysis look like if the core question were reframed?
   - Example reframes: "which option to choose" → "is any choice better than the status quo?",
     "design a better X" → "is any active approach better than the simple default?",
     "maximize gain" → "minimize regret"

3. UNEXPLORED DIRECTIONS
   - What paths were visible but never taken?
   - What did the Contrarian/Bear identify that the next round ignored?
   - What adjacent questions might be more tractable than the original one?

4. EXPLORATION vs EXPLOITATION
   - Should the next round:
     (a) DEEPEN: continue the current direction with refined parameters
     (b) BRANCH: explore an alternative approach alongside the current one
     (c) PIVOT: abandon the current direction, reframe the problem
     (d) RESTART: the current question may not be answerable; propose a different question
   - Give your recommendation with reasoning.

5. NEXT ROUND SCOPE
   - If continuing: what should the next round focus on?
   - What should it deliberately NOT do (to avoid repeating failures)?
   - What new data, perspective, or constraint would unlock progress?
```

### Lightweight Evolver Prompt (Triggers B, D — 60-second mode)

```
You are an Evolver (lightweight mode). New data has arrived that overturns core premises.

1. Which agent outputs are invalidated by this new data?
2. Does this change the RANKING of recommendations, or just the MAGNITUDES?
3. Is the current analysis direction still valid, or should it pivot?
4. ONE recommendation: revise-in-place, re-run affected agents, or reframe?

Read: the original report + the user's new data. Output: 3-5 bullets.
Save to agents/evolution-lightweight.md.
```

### Cross-Session Evolver (Trigger C)

Reads the previous analysis' final report and identifies: which premises are still assumed? What paths were excluded by the previous framing? What did the Contrarian say that was ignored? Output saved to `agents/evolution-cross-session.md`.

### Evolver Output

Saved to `<topic-slug>/agents/evolution-v{N}.md`. Presented to the user as a concise summary (3-5 bullets). User can:
- "继续原来的方向" → proceed with the current iteration as planned
- "试试分支X" → dispatch exploration on the Evolver's suggested branch
- "换方向" → reframe the problem based on the Evolver's challenge
- "就这样吧" → stop iterations, accept the current final report

### Evolution Example

Round v1 analyzed a problem and produced a complex recommendation. The Evolver, reading v1 outputs, would have noted:
- Convergence: all candidate solutions underperformed the simple baseline; diminishing returns from complexity.
- Framing challenge: the question was "design a better solution" but the data keeps saying "the simple baseline wins." Should it be "is intervention warranted at all?"
- Unexplored: radically simpler approaches, removing entire layers, questioning whether any active approach beats passive.
- Recommendation: PIVOT — simplify dramatically, test the minimal viable intervention first.

This saves entire rounds that would otherwise converge to the same conclusion: simpler is better.
