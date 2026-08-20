# Phase 1 — Dimension Decomposition

Read this file when executing Phase 1 (Multi-Lens Decomposition and Merge).

## Table of Contents
- The Splitting Principle
- Target agent counts
- 4-lens decomposition
- Merge rules
- Merge Audit (2 auditors)
- merged-tree.md format

---

## The Splitting Principle (MANDATORY)

The goal is MAXIMUM granularity. Each agent should answer ONE specific question, not a bundle. The tree should be as deep as the recursion allows.

**Rule: Split until you can't.**
- If an agent could be described as "analyze X AND Y" → split into two agents
- If an agent answers more than ONE question → split
- If two sub-questions can be answered independently → split
- If a risk can be analyzed separately from its corresponding opportunity → split
- Default: more agents with narrower questions > fewer agents with broader questions

**Anti-patterns that should trigger a split:**
- An agent merging "validate a micro thesis" AND "assess macro risk" → two different questions, two agents
- An agent covering both "pricing power analysis" AND "vertical integration trajectory" → two agents
- An agent bundling "debt risk" + "depreciation risk" + "circular revenue" into a trilogy → three failure mechanisms, three agents
- One synthesis agent producing 6+ deliverables → split by deliverable category

## Target Agent Count by Complexity

| Complexity | Wave 1 (Foundation) | Wave 2 (Analysis) | Wave 3 (Synthesis) | Total |
|-----------|:--:|:--:|:--:|:--:|
| Simple | 2 | 2-3 | 1 | 5-6 |
| Medium | 2 | 4-5 | 1-2 | 7-9 |
| Complex | 2-3 | 5-7 | 2 | 9-12 |

## 4-Lens Decomposition

Dispatch 4 decomposer agents in parallel (multiple `Agent(subagent_type="coder")` calls in one response). Each receives: Phase 0 collected context + Knowledge Baseline (+ Current State baseline) and MUST complete the Baseline Reflection (see phase-0-and-0.5.md).

| Lens | Decomposer | Perspective |
|------|-----------|-------------|
| A | Structural Economics | How the system works: value chains, incentives, economics |
| B | Investment / Capital Markets | How money flows: valuation, positioning, market structure |
| C | Risk / Counter-Argument | How it breaks: bear cases, failure modes, disconfirming evidence |
| D | Reframing / First Principles | Is the question right? Alternative framings, analogies from other domains |

Each decomposer aims for **5-8 candidate agents**, each with: name, the ONE question it answers, expected output, and which baseline findings it builds on.

## Merge Rules

The orchestrator merges the 4 decomposer outputs alone:
- Union of all candidate agents → deduplicate
- **NEVER merge agents with genuinely different questions.** When in doubt, keep them separate — the merge audit will catch over-merging
- **Keep conflicts.** Two agents reaching opposite conclusions from different angles is a feature, not redundancy
- Preserve each decomposer's unique insights; check none got silently dropped

## Merge Audit (MANDATORY, after merge, before user confirmation)

The orchestrator performs the merge alone — a single perspective with no independent check. Common merge failures:
- **Under-splitting**: a branch stopped at Level 1 when Level 2 would reveal independent perspectives. Orchestrator familiarity blinds them to missed angles.
- **Over-merging**: two genuinely different agents deduplicated because descriptions sounded similar, losing a valuable conflicting perspective.
- **Merge bias**: orchestrator unconsciously favors decompositions matching their own mental model.

Dispatch 2 lightweight audit agents in parallel (`Agent(subagent_type="coder")`, foreground is fine). Each receives: the 4 original decomposer outputs + the orchestrator's merged tree.

| Auditor | Lens | Checks |
|---------|------|--------|
| **Split Auditor** | "Is this deep enough?" | For each branch: could this split one more level? Are there branches where recursion should have continued but didn't? |
| **Merge Auditor** | "Is anything lost?" | Did the merge drop a unique perspective? Deduplicate agents that were actually different? Is any decomposer's key insight absent? |

Each outputs a brief report saved to `<topic-slug>/agents/merge-audit-{split,merge}.md`:

```
## Findings
- [PASS/FLAG] Item 1: [specific branch or agent] — [reason]
- [PASS/FLAG] Item 2: ...

## Recommendations
- [If FLAGged]: specific suggested change to the merged tree
```

Orchestrator reads both audits:
- **0 FLAGs** → present merged tree to user
- **FLAGs but minor** → note them alongside the tree, let user decide
- **Structural FLAG** (e.g., missed an entire dimension) → revise the merge before presenting

## merged-tree.md Format (MANDATORY)

After audit approval, save the final agent tree to `<topic-slug>/agents/merged-tree.md`. Serves as:
- The authoritative record of which agents will be dispatched in Phase 2 Wave 1
- Reference when assigning questions to Wave 1 agents
- Traceability: if a Phase 2 agent's output is weak, check whether the tree spec was too vague

```
# Merged Agent Tree — <topic-slug>

## Cluster A: [Name] (Foundation)
- **Agent A1:** [Name] — [Question] → [Expected output]
- **Agent A2:** ...

## Cluster B: [Name] (Core Analysis)
- **Agent B1:** ...

## Cluster C: [Name] (Risk / Validation)
- **Agent C1:** ...

## Agent Weights & Conflict Resolution
[How agent outputs are combined, how conflicts between branches are resolved]
```

Then present the tree + orchestration topology to the user for explicit approval before Phase 2.
