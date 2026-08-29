# deep-thinking

> Turn vague "analyze X" requests into structured, multi-agent deep research.
> An agent skill for Claude Code, Kimi CLI, and compatible AI agent runtimes.

**[English](README.md) · [中文文档](README.zh.md)**

---

## Why this skill exists

Ask an AI agent to "analyze X" and the typical failure mode is instant: search a little, write a report. The output is technically correct and practically useless — wrong depth, wrong angle, wrong assumptions. `deep-thinking` replaces ad-hoc analysis with a **four-phase workflow enforced by hard gates**, where each gate exists because of a specific, observed failure mode:

| Failure mode | Countermeasure |
|:---|:---|
| **The user is an outsider to their own question** — they don't know what information matters | **Phase 0**: a structured five-layer probe (current state → goal → constraints → knowledge → blind spots) plus an excluded-pathways audit that surfaces options the framing of the question silently ruled out |
| **Agents reinvent wheels** — they "design solutions" ignoring decades of validated work | **Phase 0.5**: a knowledge baseline built by parallel scouts, with fact cross-validation and a parameter-freshness check before any analysis starts |
| **Data errors cascade and amplify** — one stale number silently poisons every downstream agent | Every data agent must produce source provenance and pass a 4-check calibration (freshness, anchor, reasonability, source tier). A mandatory quality gate (**Gate 2**) sits between the analysis waves: flagged numbers never flow into conclusions unflagged |
| **Orchestrator bias turns multi-perspective synthesis into averaging** | **Wave 2** forces three adversarial roles — 🐂 optimist, 🐻 pessimist, 🔮 framework reflector — resolved by a 🦉 synthesizer producing probability-weighted scenarios, never an average |

## How it works

```
Phase 0    Structured information collection (five-layer probe)
           + excluded-pathways audit                    → 00-collected-context.md
Phase 0.5  Knowledge baseline: N knowledge scouts + current-state scouts (parallel)
           + fact cross-validation + parameter freshness → agents/knowledge-baseline*.md
           → [USER CONFIRMATION GATE]
Phase 1    Four-lens decomposition → merge → merge audit (2 auditors) → agents/merged-tree.md
           → [USER CONFIRMATION GATE]
Phase 2    Wave 1 parallel analysis → Gate 2 quality spot-check →
           Wave 2 bull/bear/reflector adversarial synthesis (🐂🐻🔮🦉) →
           dual deliverables: D1 framework report (400+ lines) + strategy-manual.md
           (250+ lines) + dark-themed HTML report (auto-generated)
Phase 3    Tracking proposal (optional) / Evolver (course correction between iterations)
```

Full per-phase procedures, prompt templates, and anti-pattern checklists live in [`references/`](references/) and are loaded on demand — they don't occupy the orchestrator's main context.

### Hard gates (excerpt)

The complete gate list is in [SKILL.md](SKILL.md). In short:

- **Never skip Phase 0 or Phase 0.5** — they are the cheapest correctness insurance in the pipeline.
- **Two user confirmation gates** — after the knowledge baseline, and after the dimension plan. The workflow stops and waits for you.
- **Gate 2 is non-negotiable** — at minimum a 60-second spot-check of one prerequisite-cluster agent and one highest-impact agent.
- **Final deliverables default to Chinese** (single hard-gate line in SKILL.md — flip it if your audience is English-first).
- **Abort anytime** — saying "stop" / "就这样吧" at any point terminates the workflow immediately.

## Requirements

- An AI agent runtime with: **subagent dispatch (with file write)**, **web search**, and **the ability to ask the user questions**. Verified: Claude Code, Kimi CLI.
- `python3 >= 3.8` — used only by the Markdown → HTML converter. **Pure standard library, zero third-party dependencies.**

## Installation

```bash
git clone https://github.com/allean/deep-thinking-repo.git
cd deep-thinking-repo

./scripts/deploy.sh                    # deploy to all detected targets (Claude Code + Kimi CLI)
./scripts/deploy.sh --target claude    # → ~/.claude/skills/deep-thinking
./scripts/deploy.sh --target kimi      # → ~/.config/agents/skills/deep-thinking
./scripts/deploy.sh --dir /custom/path # custom target directory
./scripts/deploy.sh --dry-run          # preview without writing
```

`deploy.sh` runs the environment check (`scripts/check_env.sh`) first and backs up any existing installation to `<target>.backup-<timestamp>` before overwriting. Restart your agent session after install.

## Usage

Say the trigger phrase to your agent:

```
深度解析 2026 年世界杯冠军归属
deep thinking 茅台的长期持有价值
/deep AI 资本开支周期
```

### Output structure

```
<topic-slug>/
  strategy-manual.md              ← condensed executive report (250+ lines)
  <slug>-final-report.html        ← dark-themed HTML report
  00-collected-context.md
  agents/
    knowledge-baseline*.md        ← knowledge baseline + current-state scouting
    parameter-freshness.md        ← key parameter freshness table
    merged-tree.md                ← final agent decomposition tree
    merge-audit-{split,merge}.md
    wave1-*.md / wave2-*.md
    synthesis-bull-bear.md        ← three-perspective adversarial synthesis
    wave3-d1-framework.md         ← primary detailed report (400+ lines)
    agents-final-report.html
```

### HTML report conventions

`assets/generate_html.py` (stdlib-only) renders Markdown into a dark-themed report and recognizes these markers:

| Marker | Rendered as |
|:---|:---|
| `[FACT]` / `[JUDGMENT]` | green / yellow badge (separates verified facts from analytical judgment) |
| `### Dashboard` | summary card grid |
| Section titles containing `Bull Case` / `Bear Case` / `Contrarian` / `Action Recommendations` | highlight boxes |
| `<!-- dashboard:off -->` anywhere in the file | disables dashboard cardification |

```bash
python3 <skill-dir>/assets/generate_html.py your-report.md     # single file
python3 <skill-dir>/assets/convert_all_md.py <directory>       # batch convert
```

## Repository layout

```
deep-thinking-repo/
  SKILL.md          ← skill entrypoint (workflow + hard gates + tool mapping)
  references/       ← per-phase detailed procedures (loaded on demand)
    phase-0-and-0.5.md
    phase-1-decomposition.md
    phase-2-execution.md
    phase-3-tracking-evolver.md
  assets/           ← Markdown → HTML report generator (pure Python stdlib)
    generate_html.py
    template.html
    convert_all_md.py
  scripts/
    deploy.sh       ← deploy to Claude Code / Kimi CLI / custom directory
    check_env.sh    ← environment & integrity checks
  LICENSE           ← MIT
```

## Design tradeoffs

- **This is a heavy-run workflow.** A complete analysis typically dispatches 10–30 subagents. Built for decisions that matter, not for quick questions.
- **Final output defaults to Chinese** (hard gate in SKILL.md); intermediate agent artifacts may be English. Flip the gate line for English-first use.
- **Phase 3 tracking** depends on an optional `tracking` skill; if absent, that step is skipped automatically and the main flow is unaffected.
- **Security**: the repo contains no keys, tokens, or personal paths. The Python scripts only read/write files you explicitly pass and never touch the network. Cases like `茅台` / `陈经纶` in the docs are teaching examples illustrating failure modes.

## Contributing

Issues and PRs are welcome. When modifying `SKILL.md` or `references/`, check whether the file manifest in `scripts/check_env.sh` needs updating, and run `./scripts/check_env.sh` before committing.

## License

[MIT](LICENSE)
