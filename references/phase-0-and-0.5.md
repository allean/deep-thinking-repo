# Phase 0 & 0.5 — Information Collection and Knowledge Baseline

Read this file when executing Phase 0 (Structured Information Collection) or Phase 0.5 (Knowledge Baseline).

## Table of Contents
- Five-Layer Probe Framework
- Excluded Pathways Audit
- Knowledge Scout Dispatch (dynamic count)
- Current State Scout
- Fact Cross-Validation
- Parameter Freshness Check
- Knowledge Scout Prompt Template
- Notable Discoveries & Baseline Reflection
- Exit Condition

---

## Phase 0: Five-Layer Probe Framework

Goal: turn a vague question into a concrete, well-bounded analysis target. **One layer per round, never mixing layers.** Use `AskUserQuestion` (or plain text) to ask; don't dump all layers at once.

| Layer | Question focus | Example probes |
|-------|---------------|----------------|
| 1. 现状 (Current state) | What is the situation today? | 持仓/资产/孩子年级与排名/现有方案？已尝试过什么？ |
| 2. 目标 (Goal) | What does success look like? | 目标收益/目标学校/期限？什么是"够好"，什么是"理想"？ |
| 3. 约束 (Constraints) | What limits the option space? | 资金量/时间/风险承受/户口/能否移居/流动性要求？ |
| 4. 认知 (Beliefs) | What does the user already believe? | 目前倾向哪个选项？为什么？最大的担心是什么？ |
| 5. 盲区 (Blind spots) | What hasn't the user considered? | 有没有完全没考虑过的路径？信息主要来自哪里？ |

Write everything collected to `<topic-slug>/00-collected-context.md`.

## Excluded Pathways Audit (MANDATORY, after context confirmed, before Phase 0.5)

The way a question is framed implicitly excludes categories of answers. "DSE vs 高考" excludes overseas direct entry, Sino-foreign programs, arts pathways, and gap years — not because they're irrelevant, but because the binary framing makes them invisible. This step makes exclusions explicit.

Procedure:
1. Identify 3-5 categories of paths/approaches that the current question framing **implicitly excludes**.
2. Present them to the user as a checklist:

   ```
   ## 边界检查

   当前问题措辞"{用户的问题}"隐含排除了以下路径：

   - [ ] {路径类别 1} — {为什么被排除，例子}
   - [ ] {路径类别 2} — ...
   - [ ] {路径类别 3} — ...

   以上是否有需要纳入分析的？如有，我会调整搜索范围。
   ```
3. User checks any to re-include → adjust Knowledge Scout search scope accordingly.
4. If user says "都不需要" or "继续" → proceed with original scope, but document excluded categories in the collected context.

**Rationalization guard:** "The user asked about DSE, so I should only analyze DSE" — the user asks about what they KNOW to ask about. The most valuable path may be one the user has never heard of.

---

## Phase 0.5: Knowledge Scout Dispatch

Dispatch scouts in parallel — multiple `Agent(subagent_type="coder")` calls in ONE response (they must save report files, so `explore` is unsuitable).

**Dynamic Scout Count — score the topic on 4 dimensions:**

| Dimension | Score 0 | Score 1 | Score 2 |
|-----------|:------:|:------:|:------:|
| **Domain breadth** | Single tool/technique | One industry/field | Cross-domain/multiple fields |
| **Data intensity** | Qualitative only | Mixed qual/quant | Heavy quantitative/data-driven |
| **Contestability** | Established consensus | Active debate | Highly controversial/polarized |
| **Novelty** | Well-studied problem | Emerging field | Genuinely new/uncharted |

Total → scout count: 0-2 → **1 scout**; 3-5 → **2 scouts**; 6-8 → **3 scouts**. Always ≥2 when quantitative data or active debate is involved.

## Current State Scout (MANDATORY, dispatched alongside Knowledge Scouts)

Knowledge Scouts search backward (established frameworks, validated data, known pitfalls). The Current State Scout searches FORWARD — what's happening RIGHT NOW that could reshape the analysis before it even begins.

**The `6/22-6/27 韩国-HBM-Mag7` failure mode:** an 18-agent analysis completed June 27. During the window, SK Hynix surpassed Samsung as Korea's most valuable company (June 22, first in 26 years), KOSPI circuit-broke 5 times, Mag7 dropped ~22% from peak. None of the 18 agents captured these — every agent looked backward. The Phase 5 "分化" narrative was obsolete by render time.

Procedure:
- **Always dispatch ≥1 Current State Scout**, regardless of complexity score.
- For market/financial topics, dispatch 2: one for the primary market, one for related/correlated markets.
- Receives the same Phase 0 collected context as Knowledge Scouts.
- A topic scoring 7 (3 Knowledge Scouts) gets 3 Knowledge Scouts + 1-2 Current State Scouts = 4-5 total.

**Current State Scout mission:**
1. What MAJOR EVENTS happened in this domain in the LAST 30 DAYS?
2. What is the CURRENT market/industry state? (Latest index levels, prices, sentiment indicators)
3. What BREAKING DEVELOPMENTS could reshape the analysis? (Policy changes, product launches, market shocks)
4. What are practitioners TALKING ABOUT RIGHT NOW? (Social media, forums, news headlines)

**Output:** same format as Knowledge Scouts but saved to `<topic-slug>/agents/knowledge-baseline-current.md`. Must include: Breaking Events Timeline (last 30 days, dated) · Current State Snapshot (key metrics with this week's values) · Sentiment Check · Search Log.

**Exit:** Current State findings are presented ALONGSIDE Knowledge Baseline findings. User can flag any development as "need deeper analysis" → becomes an additional Phase 1 dimension.

## Fact Cross-Validation (MANDATORY)

After ALL scouts return, before presenting the Phase 0.5 summary:
1. Cross-read all scout reports; identify factual CLAIMS that appear in only ONE scout's report but are quantitative or load-bearing.
2. For each, quickly cross-check against the other scouts' findings. Aligned? Contradicted?
3. Contradiction → note in summary: "Scout A 说 X，Scout B 的相关发现暗示可能是 Y。需要更多验证。"
4. T4-or-lower source tier AND single-scout → explicitly warn: "[Claim] 来自单一 T4 来源，需要谨慎对待。"
5. Document in the collected context which facts were cross-validated and which flagged.

Rationale: a scout finds "陈经纶 985 率 ~45%" on a T4 source (学校宣传); it looks plausible and propagates through all downstream agents. This step catches single-source, low-tier claims before they infect the analysis.

## Parameter Freshness Check (MANDATORY, after scouts return, before presenting summary)

The most dangerous stale-data failure mode: rarely-changing parameters are treated as "constants" by every agent; no one verifies them. When they DO change, the stale value survives every pipeline layer.

**The 茅台出厂价 failure mode (June 2026):** 出厂价 was 1,169; changed to 1,269 on March 31, 2026 — 2.5 months before analysis. Every agent used 1,169. The error propagated through 29 agents + Gate 2 + synthesis. Root cause: changes every ~5 years → stored as "common knowledge"; no checkpoint asked "is this number current?"

Procedure — the orchestrator MUST:
1. **Extract all key parameters** downstream agents will use: appear in multiple agents' analyses; would change conclusions if wrong by >5%; time-sensitive.
2. **For each parameter record:** current value · source · date last confirmed · expected update frequency (daily/monthly/quarterly/annual/rare).
3. **Flag any parameter where:** value comes from "common knowledge"/training data with no explicit source → MUST search to confirm; last confirmed > update frequency ago → MUST search; rare-update (annual+) not checked this analysis → MUST search; multiple agents used different values → MUST resolve.
4. **Save the table** to `<topic-slug>/agents/parameter-freshness.md`.

Example:

| Parameter | Value | Source | Last Confirmed | Update Freq | Status |
|-----------|:-----:|--------|:-------------:|:----------:|:------:|
| 飞天批价 | 1,485 | 酒价参考/今日酒价 | 2026-06-15 | Daily | ✅ |
| 茅台出厂价 | 1,269 | 茅台公告 2026-03-30 | 2026-06-17 | Rare (~5yr) | ✅ Verified |
| 白酒行业产量 | 415万千升 | 国家统计局 | 2025-01-20 | Annual | ⚠️ 待更新 |

**Rationalization guard:** "I already know 出厂价 is 1,169" — rare-update parameters are the MOST dangerous, not the safest. The harder a number is to remember changing, the more important explicit verification is.

## Knowledge Scout Prompt Template

Each scout receives the Phase 0 collected context. Dispatch via `Agent(subagent_type="coder")` with this mission:

```
You are a Knowledge Scout. Your job is NOT to analyze or solve the problem.
Your job is to find out what is ALREADY KNOWN.

Search for:
1. EXISTING SOLUTIONS: What approaches have been tried? What worked? What failed?
   - Professional forums, documentation, academic papers, practitioner blogs
   - "Known good" approaches that are widely validated
   - "Known failure modes" — approaches that look good on paper but fail in practice

2. DATA SOURCES: What data is available? How reliable is it?
   - Commonly used data sources for this domain
   - Known data quality issues, gaps, workarounds
   - Which sources are authoritative vs. unreliable

3. KEY PITFALLS: What are the most common mistakes?
   - Post-mortems, failure analyses, "what I wish I knew" posts
   - Domain-specific traps (survivorship bias, look-ahead bias, etc.)

4. VALIDATED FRAMEWORKS: What conceptual frameworks already exist?
   - Standard ways of thinking about this problem
   - Which frameworks stood the test of time vs. trendy but unproven

TOOL REQUIREMENT (HARD): You MUST use the SearchWeb tool for at least 3 distinct searches.
Do NOT rely solely on internal knowledge — it may be outdated and cannot reflect
recent developments or real-time consensus. For each search, state the query used
and cite the specific URLs found. If SearchWeb returns nothing useful after 3
attempts, document this explicitly and fall back to internal knowledge with the
disclaimer: "以下结论基于内部知识，未经实时搜索验证，可能已过时。"

OUTPUT APPENDIX:
## Search Log
| # | Query | Results (URLs) | Useful? |
|---|-------|---------------|:------:|

OUTPUT FORMAT — save to: <topic-slug>/agents/knowledge-baseline.md
## What Exists
[Existing approaches, ranked by validation level: widely validated / promising but unproven / known to fail]
## Key Data Sources
[Sources, reliability notes, known issues]
## Common Pitfalls
[The top mistakes practitioners make in this domain]
## Validated Frameworks
[Conceptual frameworks that are widely accepted]
```

## Notable Discoveries (MANDATORY for every scout)

Each scout MUST include a **"Notable Discoveries"** section at the TOP of their report (before the detailed taxonomy):

```
## Notable Discoveries
[3-5 findings that were SURPRISING, COUNTER-INTUITIVE, or otherwise worth highlighting.
NOT a summary — the discoveries most likely to change the analysis direction.
Flag with impact ratings:
🔴 HIGH IMPACT — would change core recommendations
🟡 MEDIUM IMPACT — would change weights or rankings
🟢 LOW IMPACT — interesting but doesn't change decisions]
```

Why: a 566-line taxonomy buries hidden gems (e.g., Germany tuition-free, 4+0 in Beijing, Art×Tech crossover) as footnotes. Decomposers' attention goes to obvious entries. Notable Discoveries forces gems to the surface.

## Decomposer Baseline Reflection (MANDATORY)

Before producing their agent tree, each decomposer MUST answer (in their output preamble):

```
## Baseline Reflection
1. What did I learn from the Knowledge Baseline that I did NOT already know?
2. Which Notable Discovery, if validated, would most change the recommended agent tree?
```

If the answer to Q1 is "nothing" → the decomposer didn't read the baseline carefully. Re-read.

## Scout Output Usage

1. Presented to the user alongside the Phase 0.5 summary
2. Fed as input to ALL 4 Phase 1 decomposer agents (who MUST complete Baseline Reflection)
3. Fed as input to ALL Wave 1 analysis agents
4. Referenced in the final report's Information Completeness Statement

## Exit Condition

Present the Knowledge Baseline + Current State summary (3-5 bullet takeaways). User can:
- "继续" → proceed to Phase 1 decomposition
- "补充XX" → dispatch additional scout for uncovered areas
- "这个不对" → correct misunderstandings before they propagate
