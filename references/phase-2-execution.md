# Phase 2 — Execution, Quality Gates, and Final Output

Read this file when executing Phase 2 (agent waves, Gate 2, synthesis, final documents).

## Table of Contents
- Current Data Requirement
- Data Provenance Requirement
- Data Calibration Protocol (Checks 0-3)
- Implementation Correctness Verification
- Gate 2 Checklist + Spot-Check Protocol
- Wave 2 Three-Perspective Synthesis
- Final Output: D1 + Strategy Manual + HTML
- Content Loss Prevention Checklist

---

## Current Data Requirement (MANDATORY for ALL Wave 1 and Wave 2 agents)

Baselines are snapshots — they age. Each agent VERIFIES that its data is still current AT EXECUTION TIME, not just at baseline-writing time.

**The `2-day-old baseline` failure mode:** scouts complete June 25; Wave 1 executes June 26-27. By June 27, KOSPI has circuit-broken and Mag7 dropped further. Agents using June 25 numbers produce conclusions already 48 hours stale.

Requirements for EVERY Phase 2 agent:
1. **Before writing conclusions, run ≥1 SearchWeb** to confirm the latest data on the agent's specific topic. NOT optional.
2. **Tag data freshness** in the Data Provenance section:
   - `[VERIFIED-{DATE}]` — confirmed via SearchWeb on execution date
   - `[BASELINE-{DATE}]` — from Knowledge Baseline, not re-verified
   - `[STALE]` — from baseline, known to be potentially outdated
3. **Material change discovered** (price moved >10%, policy changed, product launched) → flag in a "Recent Developments" subsection at the TOP of the report, BEFORE the main analysis.
4. Gate 2 verifies: ≥1 search conducted, key claims carry `[VERIFIED-{DATE}]` tags. If not → agent is incomplete.

**Rationalization guard:** "The Knowledge Baseline already covers this" — the baseline is a SNAPSHOT. Markets move. The agent's job is to verify the foundation hasn't shifted.

## Data Provenance Requirement (MANDATORY for all agents handling data)

```
## Data Provenance

| Data Item | Source | Access Method | Cross-Validated? | Known Issues |
|-----------|--------|---------------|:----------------:|--------------|
| Price data | Vendor API-X | REST endpoint /prices | ❌ Not cross-validated | Pre-adjustment values may differ from alternate source |
```

Rules:
- Single source without cross-validation → mark as risk
- Cross-validated against an independent source → note comparison result
- Known source issues (gaps, restatements, API instability) → note them
- Orchestrator checks this during Gate 2 — uncrossvalidated data is flagged

## Data Calibration Protocol (MANDATORY for quantitative data)

The most dangerous data errors are *plausible but inflated* or *plausible but stale*. Four checks on key quantitative findings:

### Check 0: Freshness Gate — Search Before You Trust (runs BEFORE Check 1)

The most common failure mode is not bad calibration — it's using training data as if current.

1. Identify all quantitative parameters that: would change conclusions if wrong by >5%, are time-sensitive, or came from "common knowledge."
2. For each, run SearchWeb to confirm the current value. Do NOT trust training data for financial variables (index levels, exchange rates, interest rates, commodity prices).
3. Tag every data point:
   - `[SEARCHED]` — explicitly confirmed via SearchWeb in this run
   - `[TRAINING-DATA]` — internal knowledge, not searched — **cannot be used for quantitative conclusions**
   - `[DERIVED]` — computed from other searched values

**Anti-patterns that trigger rejection:**
- "上证综指当前约 3300 点" without a SearchWeb citation → reject
- 10Y yield without a dated source → reject
- USD/CNY from training data → reject
- Any `[TRAINING-DATA]` tag in a load-bearing quantitative claim → Gate 2 flags it

### Check 1: Anchor Against Known Baselines

Every quantitative claim sanity-checked against a known reference point:

```
Example (the 陈经纶 failure mode):
  Claim: "陈经纶中学 全校985率 ~45%"
  Anchor 1: 北京整体985率 = ~4.1%
  Anchor 2: 人大附中985率 ≈ 80-90%
  Anchor 3: 八十中985率 ≈ 35-50% (estimate)
  → 陈经纶 (非市重点) at 45% would rank ABOVE 八十中 — doesn't match its tier
  → FLAG for cross-validation or downgrade
```

The anchor needs order-of-magnitude accuracy, not exactness. Deviation >2x in an unexpected direction → flag as `[DATA-SUSPECT]`.

### Check 2: Reasonability Bounds (top-down constraint)

For aggregate numbers, compute the implied total and check physical possibility:

```
Example:
  Beijing 985 seats ≈ 2,600 total; top 10 schools capture ~40-50% ≈ 1,200
  Remaining 1,400 seats across 80+ schools
  陈经纶 45% × ~400 graduates = 180 seats = 13% of all non-elite seats
  → Implausible. Fails the top-down constraint.
```

### Check 3: Source Reliability Tier

| Tier | Source Type | Confidence | Action |
|:----:|------------|:----------:|--------|
| **T1** | Official statistics (统计局/教育部/考试院) | High | Cite directly |
| **T2** | Academic papers, institutional reports | Medium-High | Note methodology limits |
| **T3** | Major media (新华社/财新/China Daily) | Medium | Cross-check if critical |
| **T4** | School marketing, test-prep blogs, 小红书/论坛 | **Low** | **MUST cross-validate with T1-T3 before citing** |
| **T5** | Single forum post, unsourced claim | **Do not cite** | Use only as search lead |

### Calibration Output

After Data Provenance, every quantitative agent includes:

```
## Data Calibration
| Claim | Value | Source Tier | Anchor Check | Reasonability Check | Verdict |
|-------|:-----:|:-----------:|:------------:|:-------------------:|:-------:|
| 陈经纶985率 | 45% | T4 (网传) | ⚠️ 偏离北京基线10x | ⚠️ 隐含值不合理 | FLAGGED → 降级为估计值 12-18% |
```

All three checks pass → cite with confidence. Any check fails → cross-validate with T1-T2, or explicitly downgrade to an estimate with stated uncertainty range. **Never pass a FLAGGED number into the pipeline unflagged.**

## Implementation Correctness Verification (when agents produce code)

1. **Self-verification (agent):** run the code once before saving; confirm no errors; include ≥1 sanity check ("total return within plausible bounds," "row counts consistent").
2. **Peer review (orchestrator, spot-check):** during Gate 2, randomly select ≥1 code-producing agent and dispatch a lightweight review subagent to: read the code; check common bugs (off-by-one, look-ahead bias, uninitialized variables, wrong column references); check implementation matches the described strategy; check output numbers are internally consistent. Bugs found → re-dispatch original agent with feedback.
3. **Cross-validation (critical results):** results serving as the primary basis for a final recommendation should ideally be confirmed by two independent implementations or a published benchmark. If only one exists, note it as a limitation in the final report.

## Gate 2 Checklist (Wave 1 → Wave 2, MANDATORY)

- [ ] Contains specific data (numbers, dates, percentages)
- [ ] Addresses the specific question assigned
- [ ] Acknowledges data gaps explicitly
- [ ] Key assumptions stated in first 30 lines
- [ ] Data Provenance section present (if agent used data)
- [ ] Data Calibration section present (if quantitative) — claims checked against anchors and reasonability bounds
- [ ] No `[DATA-SUSPECT]` claims passed through unflagged
- [ ] Code self-verification evidence present (if agent wrote code)
- [ ] At least one code-producing agent peer-reviewed (spot-check)
- [ ] **Common-Sense Number Audit:** identify any quantitative claim from "common knowledge" rather than explicit search/citation. Flag it. Cross-check against `parameter-freshness.md`. Not in the table → agent must provide source or mark `[ESTIMATE]`. Contradicts the table → stale data, re-dispatch with corrected parameter.
- [ ] **Parameter recency double-check:** spot-check 2-3 parameters from `parameter-freshness.md` via quick search — especially "rare" update-frequency parameters.

### Gate 2 Spot-Check Protocol (execute before launching Wave 2)

Spot-check at minimum:
1. **One agent from Cluster A (prerequisites/foundation)** — these feed ALL downstream agents; errors cascade everywhere.
2. **One agent from the highest-impact cluster** — typically the one producing core quantitative claims.

Each spot-check is lightweight (~60 seconds): read key quantitative claims; run anchor + reasonability checks on the 2-3 most impactful numbers; FLAGGED → cross-validate or downgrade before Wave 2 consumes it; document the result.

No Data Calibration section in a checked agent → agent incomplete. Re-dispatch with calibration instructions, or run calibration inline.

**Rationalization guard:** "Agents are high-quality based on summaries" is NOT sufficient. Summaries omit data sources. The 陈经纶 failure mode was invisible from summaries — the number looked fine in one line but failed the anchor check on inspection.

## Wave 2: Three-Perspective Synthesis (MANDATORY before final report)

Dispatch ONE synthesis agent (`Agent(subagent_type="coder")`) playing all roles explicitly — prevents orchestrator bias from resolving conflicts too easily.

| Role | Source | Function |
|------|--------|----------|
| 🐂 **Optimist** | Decomposer A + B | Most favorable reading: best-case outcome, most aggressive recommendation. Takes evidence at face value. |
| 🐻 **Pessimist** | Decomposer C | Worst-case scenario and its trigger conditions. Challenges every assumption; defines where the thesis breaks. |
| 🔮 **Reflector** | Decomposer D | Are we asking the right question? What has every other role accepted without question? Challenges the framework itself. |
| 🦉 **Synthesizer** | Orchestrator | Probability-weighted EV. Conditional IF/THEN logic. "Bull says X, Pessimist says Y, Reflector says reframe to Z. Resolution: [conditional logic]" — NOT an average. |

Procedure:
1. Feed the synthesis agent: all Wave 1 outputs + merged-tree.md + all 4 decomposer outputs.
2. It produces (saved to `<topic-slug>/agents/synthesis-bull-bear.md`):

```
## 🐂 Optimist View
[Best-case scenario, most aggressive recommendation, key assumptions that must hold]

## 🐻 Pessimist View
[Worst-case scenario, where the thesis breaks, minimal acceptable action or termination conditions]

## 🔮 Reflector View
[Framing challenges: what if the question itself is wrong? Alternative framings?
What assumptions do Optimist and Pessimist both accept without question?]

## 🦉 Synthesis
[Probability-weighted expectation, conditional IF/THEN logic, explicit conflict
resolution: "Optimist says X, Pessimist says Y, Reflector says reframe to Z.
Resolution: [conditional logic], because [reason]". Do NOT average — keep the tension.]

## Key Number: Expected Value
[Probability table: bear/base/bull scenarios with estimated magnitudes and probabilities]
```

3. Orchestrator reads the synthesis as direct input for writing strategy-manual.md.

**Rationalization guard:** "I already know what optimist/pessimist would say" — writing them down forces explicit conflict resolution. An "obvious" conflict never written down becomes a hidden assumption in the final manual.

## Final Output: Dual Documents + HTML

### Document 1: D1 Framework Report (PRIMARY — detailed reference)

**File:** `<topic-slug>/agents/wave3-d1-framework.md` — the COMPREHENSIVE report. ALL substantive findings from ALL agents. Nothing important omitted.

Mandatory sections:
1. **Executive Summary** (~300 words)
2. **Structural Comparison Matrix** — 10-12 dimensions with reasoning per dimension
3. **Scenario Matrix** — 3-4 scenarios, each: probability, narrative (1-2 paragraphs), winners/losers, falsifiable signposts
4. **Signpost Dashboard** — 10-15 indicators with current values, thresholds, update frequency, signal quality
5. **Bull/Bear/Contrarian Synthesis** — three-body problem with conditional resolution
6. **Falsifiable Claims Table** — 8-10 claims, each: confidence, validation data, invalidation data, observation window
7. **Actionable Investment Theses** — 3-5 theses with confidence levels and invalidation conditions
8. **Data Provenance Summary** — source tier distribution across the analysis

**Minimum depth: 400+ lines.** Readable standalone — someone reading ONLY this gets the complete picture.

### Document 2: Strategy Manual (CONDENSED — quick-reference deck)

**File:** `<topic-slug>/strategy-manual.md` — the EXECUTIVE version. Every SECTION HEADER and every KEY NUMBER from D1, abbreviated narratives. Complete logical structure + all numbers in 5 minutes.

Mandatory structure: Dashboard summary cards · core verdict (one sentence + 3 bullet rationale) · analogy/claim validation table · structural comparison matrix (full) · value chain economics map (full) · scenario matrix with probabilities · probability-weighted layer outlook · Bull/Bear/Contrarian/Action synthesis · investment theses (3-5 bullets each) · monitoring dashboard (full table) · domain applicability verdict · key numbers summary · `[FACT]`/`[JUDGMENT]` markers on all key claims.

**Minimum depth: 250+ lines, Chinese.** Must NOT feel thin.

### Document 3: HTML Reports (MANDATORY)

```bash
python3 <skill-dir>/assets/generate_html.py <topic-slug>/strategy-manual.md
cp <topic-slug>/<slug>-final-report.html <topic-slug>/agents/agents-final-report.html
```

Template triggers to ensure fire:
- `### Dashboard` immediately after `## Dashboard` → summary cards
- `[FACT]` and `[JUDGMENT]` markers throughout → color-coded badges
- Section titles containing `Bull Case`, `Bear Case`, `Contrarian`, `Action Recommendations` → highlight boxes

Verification after generation: ✓ summary-grid (1+) · ✓ summary-card (3+) · ✓ highlight-box (3+) · ✓ badge-green/badge-yellow (10+ combined) · ✓ tables (8+). WARNING if fewer than 3 highlight boxes → check section titles.

## Content Loss Prevention Checklist (MANDATORY before declaring done)

- [ ] Every agent's key quantitative finding appears in D1
- [ ] Every scenario has a full narrative (not just one-line labels)
- [ ] Every falsifiable claim has validation AND invalidation data + observation window
- [ ] The signpost dashboard has current values, not just threshold columns
- [ ] The Bull/Bear/Contrarian synthesis includes explicit conflict resolution (not averaging)
- [ ] The strategy manual has ALL section headers from D1 (condensed, not deleted)
- [ ] Both HTML files are generated and verified
