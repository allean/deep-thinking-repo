# deep-thinking

> 把模糊的"帮我分析一下 X"变成结构化的多智能体深度研究 —— 一个适用于 Claude Code / Kimi CLI 等 AI Agent 运行时的 Skill。
>
> Turn vague "analyze X" requests into structured, multi-agent deep dives. An agent skill for Claude Code, Kimi CLI, and similar runtimes.

## 这个 Skill 解决什么问题

让 AI 直接"分析一个话题"，典型失败模式是：立刻开搜、立刻写报告 —— 输出技术上正确但对你没用（深度不对、角度不对、语言不对）。`deep-thinking` 用一套**带硬性闸门的四阶段工作流**解决这个问题：

- **用户往往是自己问题的门外汉** —— 所以 Phase 0 先结构化地搞清楚"到底要分析什么、给谁看、约束是什么"，而不是直接开干。
- **Agent 会凭空造轮子** —— 所以 Phase 0.5 先建立知识基线（已有哪些成熟方法、关键参数的最新值是多少），后续所有分析必须站在已验证知识之上。
- **数据错误会级联放大** —— 所以每个数据 Agent 必须做来源溯源 + 四步校准，Wave 1 → Wave 2 之间有强制质量门（Gate 2），任何一个被标记的可疑数字都不会悄悄流进最终结论。
- **编排者偏见会让多视角合成变成和稀泥** —— 所以 Wave 2 强制 🐂乐观 / 🐻悲观 / 🔮框架反思 三视角对抗，再由 🦉 合成者做概率加权，而不是取平均。

## 工作流一览

```
Phase 0   结构化信息收集（五层探针：现状→目标→约束→认知→盲区）
          + 被排除路径审计（找出提问方式隐含排除掉的选项）   → 00-collected-context.md
Phase 0.5 知识基线：N 个知识侦察兵 + 现状侦察兵（并行）
          + 事实交叉验证 + 参数时效性检查                   → agents/knowledge-baseline*.md
          → 【用户确认门】
Phase 1   四视角拆解 → 合并 → 合并审计（2 个审计员）        → agents/merged-tree.md
          → 【用户确认门】
Phase 2   Wave 1 并行分析 → Gate 2 质量抽查 →
          Wave 2 三视角对抗合成（🐂🐻🔮🦉）→
          双文档产出：D1 框架报告（400+ 行）+ strategy-manual.md（250+ 行，中文）
          + HTML 报告（自动生成）
Phase 3   跟踪提案（可选）/ Evolver（迭代之间的方向纠偏）
```

每个 Phase 的完整规程、提示词模板、反模式清单在 [`references/`](references/) 目录，按需加载，不占主上下文。

## 环境要求

- 一个支持以下能力的 AI Agent 运行时：**子代理派发（可写文件）、联网搜索、向用户提问**。已验证：Claude Code、Kimi CLI。
- `python3 >= 3.8`（仅用于 Markdown → HTML 报告转换，**纯标准库，无第三方依赖**）。

## 安装

```bash
git clone https://github.com/allean/deep-thinking-repo.git
cd deep-thinking-repo

# 部署到所有检测到的目标（Claude Code + Kimi CLI）
./scripts/deploy.sh

# 只部署到其中一个
./scripts/deploy.sh --target claude    # → ~/.claude/skills/deep-thinking
./scripts/deploy.sh --target kimi      # → ~/.config/agents/skills/deep-thinking

# 自定义目录 / 预演
./scripts/deploy.sh --dir /path/to/skills/deep-thinking
./scripts/deploy.sh --dry-run
```

部署脚本会先运行环境检查（`scripts/check_env.sh`），已有安装会自动备份为 `<target>.backup-<时间戳>` 后再覆盖。也可以单独运行检查：

```bash
./scripts/check_env.sh
```

安装后重启 Agent 会话即可生效。

## 使用

对 Agent 说出触发词即可：

```
深度解析 2026 年世界杯冠军归属
deep thinking 茅台的长期持有价值
/deep AI 资本开支周期
```

工作流会在两个确认门（Phase 0.5 结束后、Phase 1 维度计划出来后）停下来等你确认；任何时候说"停"/"就这样吧"会立即终止。

### 输出结构

```
<topic-slug>/
  strategy-manual.md              ← 精炼执行报告（250+ 行，中文）
  <slug>-final-report.html        ← 深色主题 HTML 报告
  00-collected-context.md
  agents/
    knowledge-baseline*.md        ← 知识基线 + 现状侦察
    parameter-freshness.md        ← 关键参数时效表
    merged-tree.md                ← 最终 Agent 拆解树
    merge-audit-{split,merge}.md
    wave1-*.md / wave2-*.md
    synthesis-bull-bear.md        ← 三视角对抗合成
    wave3-d1-framework.md         ← 主详细报告（400+ 行）
    agents-final-report.html
```

### HTML 报告的 Markdown 约定

`assets/generate_html.py` 会识别以下标记：

| 写法 | 渲染效果 |
|---|---|
| `[FACT]` / `[JUDGMENT]` | 绿/黄徽章（区分已验证事实与分析判断） |
| `### Dashboard` | 摘要卡片组 |
| 标题含 `Bull Case` / `Bear Case` / `Contrarian` / `Action Recommendations` | 高亮框 |
| `<!-- dashboard:off -->`（文件任意处） | 关闭 Dashboard 卡片化 |

```bash
python3 <skill-dir>/assets/generate_html.py your-report.md
# 批量转换某个目录下所有 md：
python3 <skill-dir>/assets/convert_all_md.py <directory>
```

## 仓库结构

```
deep-thinking-repo/
  SKILL.md                        ← Skill 主文件（工作流 + 硬性闸门 + 工具映射）
  references/                     ← 各 Phase 详细规程（按需加载）
    phase-0-and-0.5.md
    phase-1-decomposition.md
    phase-2-execution.md
    phase-3-tracking-evolver.md
  assets/                         ← HTML 报告生成（纯 Python 标准库）
    generate_html.py
    template.html
    convert_all_md.py
  scripts/
    deploy.sh                     ← 部署到 Claude Code / Kimi CLI / 自定义目录
    check_env.sh                  ← 环境与完整性检查
  LICENSE                         ← MIT
```

## 设计取舍与注意事项

- **成本**：这是一次"重投入"工作流 —— 一次完整分析通常派发 10-30 个子代理。适合重要决策，不适合随手一问。
- **最终输出默认为中文**（SKILL.md 中的硬性闸门），Agent 中间产物可以是英文。如果你的使用场景主要是英文，部署后修改 SKILL.md 中对应的 Hard Gate 即可。
- **Phase 3 的跟踪交接**依赖一个可选的 `tracking` skill；未安装时该步骤会自动跳过，不影响主流程。
- **安全**：本仓库不含任何密钥、Token 或个人路径；Python 脚本只读写你显式指定的文件，不访问网络。文档中的 `茅台`、`陈经纶` 等案例是用于说明失败模式的教学示例。

## Contributing

欢迎 Issue 和 PR。修改 `SKILL.md` 或 `references/` 时，请同步检查 `scripts/check_env.sh` 中的文件清单是否需要更新，并在提交前运行 `./scripts/check_env.sh`。

## License

[MIT](LICENSE)

---

## English Summary

`deep-thinking` is an agent skill that turns vague "analyze X" requests into structured multi-agent deep research. It enforces a four-phase workflow with hard gates: structured information collection (five-layer probe + excluded-pathways audit), a knowledge baseline with fact cross-validation and parameter freshness checks, four-lens decomposition with merge audits, and parallel analysis waves with a mandatory quality gate and bull/bear/reflector adversarial synthesis. Output is a dual-document deliverable (a 400+ line framework report plus a condensed strategy manual) rendered into dark-themed HTML by the bundled stdlib-only Python converter.

**Install:** `./scripts/deploy.sh` (supports `--target claude|kimi|all`, `--dir <custom>`, `--dry-run`). Requires an agent runtime with subagents + web search, and Python ≥ 3.8 (stdlib only). See the Chinese sections above for full documentation.
