---
name: deep-thinking
description: >
  Use when the user says "深度解析", "深度分析", "深入分析", "/deep", "deep thinking",
  or "deep dive" followed by a specific topic. Also use when the user explicitly asks
  for a multi-angle, thorough analysis rather than a quick answer. This skill enforces
  a mandatory 4-phase workflow with structured information collection, dimension
  decomposition, parallel agent execution with cross-synthesis, and dual output
  (conversation summary + file report). Do NOT skip to analysis without completing Phase 0.
---

# Deep Thinking

## Overview

Turn vague "analyze X" requests into structured multi-agent deep dives. The core insight: **the user is often an outsider to their own question** — they don't know what information matters. Phase 0 is the most critical step.

Platform-agnostic: works with Claude Code and Kimi CLI (and any agent runtime with subagent + web-search + file-write capabilities). See the Tool Mapping table below.

## Hard Gates

- **NEVER skip Phase 0.** Baseline failure mode: receive topic → immediately dispatch agents → technically correct but useless output (wrong depth, wrong language, wrong angle).
- **NEVER skip Phase 0.5 (Knowledge Baseline).** Second failure mode: agents invent solutions from scratch without checking what already exists.
- **NEVER proceed to Phase 1 without user confirmation.** After Phase 0.5, present knowledge baseline + Phase 0 context summary; ask "does this match your situation?"
- **NEVER proceed to Phase 2 without user approving the dimension plan.** Show the agent split and orchestration topology, get explicit confirmation.
- **NEVER skip Gate 2 (Wave 1→Wave 2 Quality Gate).** Minimum: spot-check at least 2 agents (one from Cluster A/prerequisites, one from the highest-impact cluster). Can be lightweight (60-second sanity check each) but CANNOT be zero.
- **Final output MUST be in Chinese (中文).** Agent reports can be in English — the orchestrator translates and synthesizes into Chinese when writing strategy-manual.md and the D1 framework report. HTML reports must be Chinese.
- **ALWAYS generate HTML reports at the end.** After writing strategy-manual.md, run `python3 <skill-dir>/assets/generate_html.py <report.md>`, where `<skill-dir>` is the directory containing this SKILL.md (e.g. `~/.claude/skills/deep-thinking` on Claude Code, `~/.config/agents/skills/deep-thinking` on Kimi CLI). Use `[FACT]` and `[JUDGMENT]` markers throughout, `### Dashboard` for summary cards, and section titles containing `Bull Case`, `Bear Case`, `Contrarian`, `Action Recommendations` for highlight boxes.
- **User says "stop"/"enough"/"就这样吧" at any point → stop immediately.**
- **User refuses to answer Phase 0 questions:** explain once: "问这些问题是为了避免分析跑偏。如果你跳过这一步，我可能给你一个正确但对你没用的答案。" If they insist, proceed to Phase 0.5 with explicit note: "以下分析基于有限信息，可能有偏差。"

**Output root:** `<topic-slug>/` created under the current workspace root. If not in a workspace, use `~/deep-thinking/<topic-slug>/`.

## Tool Mapping

| Purpose | Claude Code | Kimi CLI |
|---|---|---|
| Dispatch analysis/scout/audit agents that must SAVE files | `Task` (general-purpose agent) | `Agent(subagent_type="coder")` |
| Read-only investigation | `Task` (Explore agent) | `Agent(subagent_type="explore")` |
| Web search inside agents | `WebSearch` / `WebFetch` | `SearchWeb` / `FetchURL` |
| Parallel dispatch | Multiple `Task` calls in one response | Multiple `Agent` calls in one response; `run_in_background=true` for long waves |
| User confirmation at gates | `AskUserQuestion` or plain-text question | `AskUserQuestion` or plain-text question |
| Phase 3 tracking handoff | `tracking` skill (optional, if installed) | `tracking` skill (optional, if installed) |

On other runtimes, map to the nearest equivalents: subagent dispatch with file-write, web search, and a way to ask the user questions.

## Workflow at a Glance

```
Phase 0   Structured Information Collection (Five-Layer Probe)      → 00-collected-context.md
          + Excluded Pathways Audit (MANDATORY)
Phase 0.5 Knowledge Baseline: N Knowledge Scouts + 1-2 Current State Scouts (parallel)
          + Fact Cross-Validation + Parameter Freshness Check       → agents/knowledge-baseline*.md, agents/parameter-freshness.md
          → USER CONFIRM GATE
Phase 1   4-Lens Decomposition → Merge → Merge Audit (2 auditors)   → agents/merged-tree.md
          → USER CONFIRM GATE
Phase 2   Wave 1 agents (parallel) → GATE 2 quality spot-check →
          Wave 2 three-perspective synthesis (🐂🐻🔮🦉) →
          Dual documents: D1 framework (400+ lines) + strategy-manual.md (250+ lines, Chinese)
          + HTML reports (MANDATORY)
Phase 3   Tracking proposal (OPT-IN) / Evolver (between iterations)
```

---

## Phase 0: Structured Information Collection

Goal: turn a vague question into a concrete, well-bounded analysis target. Use the **Five-Layer Probe Framework (现状→目标→约束→认知→盲区)**, one layer per round, never mixing layers. Write collected context to `<topic-slug>/00-collected-context.md`.

Full probe framework: see [references/phase-0-and-0.5.md](references/phase-0-and-0.5.md).

### Excluded Pathways Audit (MANDATORY, after context confirmed, before Phase 0.5)

The way a question is framed implicitly excludes categories of answers ("DSE vs 高考" excludes overseas direct entry, Sino-foreign programs, arts pathways...). The user doesn't know what they're excluding.

Procedure: identify 3-5 categories of paths the current framing implicitly excludes; present as a checklist; user may re-include any; document exclusions in the collected context. Full template in [references/phase-0-and-0.5.md](references/phase-0-and-0.5.md).

**Rationalization guard:** "The user asked about DSE, so I should only analyze DSE" — the user asks about what they KNOW to ask about. A DSE-only analysis that fails to mention Germany as an alternative is technically responsive but practically incomplete.

## Phase 0.5: Knowledge Baseline (MANDATORY)

Purpose: before decomposing into analysis agents, establish what is ALREADY KNOWN. Agents must build on verified knowledge, not invent from scratch. Failure modes prevented: (3) agents "design solutions" ignoring decades of validated work; (4) agents use single-source unverified data, poisoning all downstream conclusions.

**After Phase 0 context is confirmed, before Phase 1**, dispatch in parallel (multiple `Agent` calls in one response):

1. **Knowledge Scouts (1-3)** — count determined by 4-dimension scoring (domain breadth / data intensity / contestability / novelty, 0-2 each):
   - 0-2 → 1 scout; 3-5 → 2 scouts; 6-8 → 3 scouts. Always ≥2 when quantitative data or active debate is involved.
2. **Current State Scout (≥1, ALWAYS)** — searches FORWARD: last-30-days major events, current market/industry state, breaking developments, what practitioners are discussing now. For market/financial topics dispatch 2 (primary + correlated markets). Additive to Knowledge Scouts, not a replacement.

Then, before presenting the summary:
3. **Fact Cross-Validation (MANDATORY)** — flag load-bearing quantitative claims appearing in only ONE scout's report; cross-check; warn on single-source T4 claims.
4. **Parameter Freshness Check (MANDATORY)** — extract all key parameters downstream agents will use (would change conclusions if wrong by >5%); record value/source/last-confirmed/update-frequency; any "common knowledge" or overdue parameter MUST be re-searched. Save table to `<topic-slug>/agents/parameter-freshness.md`. (The 茅台出厂价 failure mode: a rare-update parameter stored as "common knowledge" silently poisoned 29 agents.)

**Exit condition:** present Knowledge Baseline + Current State summary (3-5 bullet takeaways) to the user. User: "继续" → Phase 1; "补充XX" → more scouts; "这个不对" → correct before it propagates.

Scout prompt template, Notable Discoveries requirement, Baseline Reflection requirement, and Current State Scout mission: see [references/phase-0-and-0.5.md](references/phase-0-and-0.5.md).

## Phase 1: Dimension Decomposition

All decomposers and Wave 1 agents MUST read the Knowledge Baseline as input and cite which existing approaches they build on or depart from.

**The Splitting Principle (MANDATORY):** MAXIMUM granularity. Each agent answers ONE specific question.
- "Analyze X AND Y" → two agents. More than ONE question → split. Independently answerable → split. Risk separable from opportunity → split.
- Default: more agents with narrower questions > fewer agents with broader questions.

**Target agent count by complexity:**

| Complexity | Wave 1 (Foundation) | Wave 2 (Analysis) | Wave 3 (Synthesis) | Total |
|-----------|:--:|:--:|:--:|:--:|
| Simple | 2 | 2-3 | 1 | 5-6 |
| Medium | 2 | 4-5 | 1-2 | 7-9 |
| Complex | 2-3 | 5-7 | 2 | 9-12 |

**4-lens decomposition** (Structural Economics / Investment & Capital Markets / Risk & Counter-Argument / Reframing & First Principles): 4 decomposer agents, each aiming for 5-8 candidate agents, each completing a **Baseline Reflection** (what did I learn from the baseline I didn't know? which Notable Discovery would most change my tree?). Merge = union → deduplicate → NEVER merge genuinely different questions → keep conflicts.

**Merge Audit (MANDATORY, after merge, before user confirmation):** dispatch 2 lightweight auditors in parallel — Split Auditor ("is this deep enough?") and Merge Auditor ("is anything lost?"). 0 FLAGs → present tree; minor FLAGs → note alongside; structural FLAG → revise merge. Save audits to `agents/merge-audit-{split,merge}.md`.

**MANDATORY: save the merged tree** to `<topic-slug>/agents/merged-tree.md` (clusters, per-agent question + expected output, weights & conflict resolution). Present to user for approval before Phase 2.

Full anti-patterns, recursion rules, auditor specs: see [references/phase-1-decomposition.md](references/phase-1-decomposition.md).

## Phase 2: Execution + Cross-Synthesis

### Mandatory requirements for ALL Phase 2 agents

1. **Current Data Requirement** — before writing conclusions, run ≥1 `SearchWeb` to confirm the latest data on the agent's specific topic. Tag freshness: `[VERIFIED-{DATE}]` / `[BASELINE-{DATE}]` / `[STALE]`. Material changes (price moved >10%, policy changed) → flag in a "Recent Developments" subsection at the TOP of the report.
2. **Data Provenance** — every agent using quantitative data includes a provenance table (source, access method, cross-validated?, known issues). Single-source without cross-validation → mark as risk.
3. **Data Calibration (4 checks)** — Check 0 Freshness Gate (search before you trust; `[SEARCHED]`/`[TRAINING-DATA]`/`[DERIVED]` tags; `[TRAINING-DATA]` cannot support load-bearing quantitative conclusions); Check 1 Anchor against known baselines; Check 2 Reasonability bounds (top-down constraint); Check 3 Source reliability tier (T1 official → T5 unsourced; T4 must be cross-validated with T1-T3). Output a calibration table; FLAGGED numbers never pass through unflagged.
4. **Implementation Correctness** — code-producing agents must self-verify (run once, sanity checks); orchestrator spot-checks ≥1 code agent with a peer-review subagent; critical results ideally cross-validated by two implementations.

Full calibration protocol, tiers, and prompt snippets: see [references/phase-2-execution.md](references/phase-2-execution.md).

### Gate 2 (Wave 1 → Wave 2, MANDATORY, cannot be skipped)

Checklist per agent report: specific data present · addresses assigned question · data gaps acknowledged · key assumptions in first 30 lines · Data Provenance present · Data Calibration present · no unflagged `[DATA-SUSPECT]` · code self-verification evidence · ≥1 code agent peer-reviewed · **Common-Sense Number Audit** (flag any quantitative claim from "common knowledge"; cross-check against `parameter-freshness.md`) · **Parameter recency double-check** (spot-check 2-3 freshness-table parameters via quick search, especially "rare" update frequency ones).

**Spot-Check Protocol:** at minimum one Cluster A (prerequisites) agent + one highest-impact cluster agent. ~60s each: run anchor + reasonability checks on the 2-3 most impactful numbers. FLAGGED → cross-validate or downgrade before Wave 2 consumes it. Full checklist: [references/phase-2-execution.md](references/phase-2-execution.md).

**Rationalization guard:** "The agents are high-quality based on summaries" is NOT sufficient. Summaries omit data sources — the 陈经纶 failure mode was invisible from summaries.

### Wave 2: Three-Perspective Synthesis (MANDATORY before writing final report)

Dispatch ONE synthesis agent that explicitly plays three roles against each other (prevents orchestrator bias from resolving conflicts too easily):

| Role | Function |
|------|----------|
| 🐂 Optimist | Best-case outcome, most aggressive recommendation, assumptions that must hold |
| 🐻 Pessimist | Worst-case scenario, where the thesis breaks, termination conditions |
| 🔮 Reflector | Challenges the FRAMEWORK itself: is the question right? What do both sides accept without question? |
| 🦉 Synthesizer | Probability-weighted EV, conditional IF/THEN logic, explicit conflict resolution — NOT averaging |

Input: all Wave 1 outputs + merged-tree.md + 4 decomposer outputs. Output: `agents/synthesis-bull-bear.md` with Optimist/Pessimist/Reflector/Synthesis sections + probability-weighted scenario table (bear/base/bull with magnitudes and probabilities).

### Final Output: Dual Documents + HTML (MANDATORY)

**Document 1 — D1 Framework Report** (`agents/wave3-d1-framework.md`, 400+ lines, the COMPLETE reference): Executive Summary · Structural Comparison Matrix (10-12 dimensions) · Scenario Matrix (3-4 scenarios with probability, narrative, winners/losers, falsifiable signposts) · Signpost Dashboard (10-15 indicators with current values, thresholds, update frequency) · Bull/Bear/Contrarian Synthesis · Falsifiable Claims Table (8-10 claims with confidence, validation/invalidation data, observation window) · Actionable Investment Theses (3-5) · Data Provenance Summary.

**Document 2 — Strategy Manual** (`strategy-manual.md`, 250+ lines, Chinese, condensed executive version): every D1 section header + every key number, abbreviated narratives. Dashboard summary cards · core verdict (one sentence + 3 bullets) · validation tables · full matrices · scenario matrix · Bull/Bear/Contrarian/Action synthesis · theses condensed to 3-5 bullets · monitoring dashboard · `[FACT]`/`[JUDGMENT]` markers on all key claims.

**Document 3 — HTML reports:**

```bash
python3 <skill-dir>/assets/generate_html.py <topic-slug>/strategy-manual.md
cp <topic-slug>/<slug>-final-report.html <topic-slug>/agents/agents-final-report.html
```

Template triggers: `### Dashboard` after `## Dashboard` → summary cards; `[FACT]`/`[JUDGMENT]` → badges; section titles containing `Bull Case`/`Bear Case`/`Contrarian`/`Action Recommendations` → highlight boxes. Verify output: summary-grid ≥1, summary-card ≥3, highlight-box ≥3, badges ≥10, tables ≥8.

**Content loss prevention checklist (before declaring done):** every agent's key quantitative finding in D1 · every scenario has full narrative · every falsifiable claim has validation AND invalidation data + window · signpost dashboard has current values · Bull/Bear synthesis has explicit conflict resolution · strategy manual has ALL D1 section headers · both HTML files generated and verified.

### Complete Output Tree

```
<topic-slug>/
  strategy-manual.md              ← Condensed executive report (250+ lines, Chinese)
  <slug>-final-report.html        ← Dark-themed HTML (from strategy-manual.md)
  00-collected-context.md
  agents/
    knowledge-baseline.md         ← Phase 0.5 scout output
    knowledge-baseline-current.md ← Current State Scout output
    parameter-freshness.md        ← Parameter freshness table
    merged-tree.md                ← Phase 1 final agent tree
    merge-audit-{split,merge}.md
    decomposer-{a,b,c,d}.md
    wave1-*.md / wave2-*.md
    synthesis-bull-bear.md        ← Three-perspective synthesis
    wave3-d1-framework.md         ← PRIMARY detailed report (400+ lines)
    agents-final-report.html
```

## Phase 3: Tracking + Evolver

**Tracking (OPT-IN — only when user says "开始跟踪"/"start tracking"):** extract candidate metrics (auto vs manual), milestones, frequency from the analysis; present as a proposal; on confirmation hand off to the `tracking` skill. NEVER propose unprompted unless the output contains trackable elements; NEVER force tracking. Saves `tracking-proposal.json`.

**Evolver (MANDATORY between iterations):** challenges the trajectory before spending the next round. Triggers: (A) user requests new iteration; (B) new data overturns core premises (lightweight 60-second mode); (C) related follow-up analysis (cross-session mode); (D) major report revision (>20% of key numbers or top-3 re-rank); (E-G) tracking-driven: data contradiction / accumulated review (≥6 periods) / consecutive anomaly (≥3 fails). Evolver asks: convergence diagnosis · framing challenge · unexplored directions · deepen/branch/pivot/restart · next-round scope. Output `agents/evolution-v{N}.md`, discussed with user before proceeding.

Full procedures and prompts: see [references/phase-3-tracking-evolver.md](references/phase-3-tracking-evolver.md).

## Common Mistakes

| Mistake | Reality |
|---------|---------|
| "We don't need to search — I already know this domain" | Knowledge changes. The baseline verifies that today's assumptions match today's reality. |
| "The agent can search the web while doing analysis" | Analysis + search = shallow version of both. Search first, analyze second. |
| "The data source is standard, no need to cross-validate" | "Standard" sources have bugs. Cross-validation is the difference between analyzing reality and analyzing a data artifact. |
| "The code ran without errors, so it's correct" | No-error ≠ correct. The most dangerous bugs produce plausible-looking numbers. |
| "I'll review the code myself" | The author is the worst reviewer of their own code. Fresh eyes catch what the author is blind to. |

## Rationalization Guards

| Excuse | Reality |
|--------|---------|
| "Phase 0.5 will slow things down — dispatch scouts alongside decomposers" | Decomposers need the baseline to design the right tree. 2-3 minutes of searching saves hours of wrong analysis. |
| "This domain is too niche for external search" | Every domain has practitioners. If truly nothing exists, the scout reporting that is itself valuable. |
| "Cross-validating data will double the work" | Spot-checking: 5 random dates, one key metric vs benchmark. 95% of value from 5% of effort. |
| "v1 direction is fine — go deeper in v2 without an Evolver" | Every iteration exploits the previous direction. The Evolver is the only mechanism that can say "wrong way." It costs one agent and 2-3 minutes. |
| "The Evolver is just the Contrarian role again" | Contrarian challenges conclusions WITHIN a framework. Evolver challenges the framework ITSELF. |
| "出厂价是 1,169 — 这个数我记得很清楚，不用查" | 变动越罕见的参数越容易被当作常量，过期时危害越大。任何训练数据截止后可能变化的参数必须显式搜索确认。 |

## Files

```
<skill-dir>/                       ← e.g. ~/.claude/skills/deep-thinking or ~/.config/agents/skills/deep-thinking
  SKILL.md                          ← This file (core workflow + hard gates)
  references/
    phase-0-and-0.5.md              ← Five-Layer Probe, Excluded Pathways Audit, scout prompts, cross-validation, parameter freshness
    phase-1-decomposition.md        ← Splitting principle, 4-lens decomposition, merge audit, merged-tree format
    phase-2-execution.md            ← Data provenance, 4-check calibration, Gate 2 checklist, synthesis roles, output specs
    phase-3-tracking-evolver.md     ← Tracking proposal procedure, all Evolver triggers + prompts
  assets/
    generate_html.py                ← Markdown → dark-themed HTML report
    template.html                   ← HTML template (resolved relative to the script)
    convert_all_md.py               ← Batch-convert every report under a topic directory
```
