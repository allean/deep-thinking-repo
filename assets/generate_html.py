#!/usr/bin/env python3
"""
Convert a deep-thinking Markdown report to styled HTML using the Beijing template.

Usage:
  python3 generate_html.py <path-to-report.md>

Features (v2):
  - Hero with version badge, label, h1+span, clean sub/meta (no MD artifacts)
  - Fixed nav with deduplicated anchors, human-readable title
  - Dashboard tables → stats row + summary-grid cards
  - h2 headings → <section> wrappers with fade-in + auto section-desc
  - 5-phase timeline detection (Phase 1-5 patterns)
  - grid-2/grid-3 auto-detection from consecutive card patterns
  - Info-box (KEY INSIGHT) and warn-box (WARNING, SINGLE POINT) detection
  - Verdict box for 核心判断/中心论点 sections
  - Highlight boxes for Bull/Bear/Contrarian/Action sections
  - Colored stat numbers (green/yellow/red based on content)
  - [FACT]/[JUDGMENT] → color-coded badges
  - Post-processing: dedup hidden h3, clean empty tags, card-border coloring

Output: <same-directory>/<topic-slug>-final-report.html
"""

import re
import html as html_mod
import sys
DASHBOARD_OFF = False
import os
import datetime

TEMPLATE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'template.html')

# ---- Inline helpers ----

def md_para(text):
    text = html_mod.escape(text)
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    return text

def strip_md(text):
    """Strip markdown formatting for plain text use (hero, nav, labels)."""
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'\*(.+?)\*', r'\1', text)
    text = re.sub(r'`([^`]+)`', r'\1', text)
    text = re.sub(r'\[FACT[^\]]*\]', '', text)
    text = re.sub(r'\[JUDGMENT[^\]]*\]', '', text)
    text = re.sub(r'---', '', text)
    return text.strip()

def make_badges(text):
    text = re.sub(r'\[FACT[^\]]*\]', '<span class="badge badge-green">FACT</span>', text)
    text = re.sub(r'\[JUDGMENT[^\]]*\]', '<span class="badge badge-yellow">JUDGMENT</span>', text)
    return text

def slugify(text):
    s = re.sub(r'[^\w\s-]', '', text.lower())
    s = re.sub(r'[-\s]+', '-', s).strip('-')
    return s[:40]

def num_color(value_str, label_str=''):
    """Determine stat number color from value and label content."""
    combined = (value_str + ' ' + label_str).lower()
    if any(w in combined for w in ['↓', '跌', '-', '负', 'collapse', 'crash', 'bear', '泡沫', '破裂', 'risk']):
        if any(w in combined for w in ['+', '↑', '涨', 'surge', 'bull', 'boom']):
            return 'yellow'
        return 'red'
    if any(w in combined for w in ['+', '↑', '涨', 'high', 'green', 'bull', 'surge', 'boom', 'leader']):
        return 'green'
    if any(w in combined for w in ['拐', '⚠', 'warn', 'watch', 'marginal', 'transition']):
        return 'yellow'
    return ''

# ---- Body rendering ----

def render_md_body(body):
    lines = body.strip().split('\n')
    result = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1; continue
        s = line.strip()

        if s.startswith('#### '):
            result.append(f'<h4>{make_badges(md_para(s[5:]))}</h4>')
            i += 1; continue
        if s.startswith('### '):
            result.append(f'<h3>{make_badges(md_para(s[4:]))}</h3>')
            i += 1; continue
        if s.startswith('```'):
            code_lines = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith('```'):
                code_lines.append(lines[i] + '\n'); i += 1
            i += 1
            result.append(f'<pre>{html_mod.escape("".join(code_lines))}</pre>')
            continue
        if s.startswith('>'):
            quote_lines = []
            while i < len(lines) and lines[i].strip().startswith('>'):
                quote_lines.append(lines[i].strip()[1:].strip()); i += 1
            result.append(f'<blockquote><p>{make_badges(md_para(" ".join(quote_lines)))}</p></blockquote>')
            continue
        if s == '---':
            result.append('<hr />')
            i += 1; continue
        if re.match(r'^- ', s):
            items = []
            while i < len(lines) and re.match(r'^- ', lines[i].strip()):
                items.append(f'<li>{make_badges(md_para(lines[i].strip()[2:]))}</li>'); i += 1
            result.append(f'<ul>{"".join(items)}</ul>')
            continue
        if re.match(r'^\d+\. ', s):
            items = []
            while i < len(lines) and re.match(r'^\d+\. ', lines[i].strip()):
                t = re.sub(r"^\d+\.\s*", "", lines[i].strip())
                items.append(f'<li>{make_badges(md_para(t))}</li>'); i += 1
            result.append(f'<ol>{"".join(items)}</ol>')
            continue
        if '|' in s and s.startswith('|'):
            table_lines = []
            while i < len(lines) and '|' in lines[i] and lines[i].strip().startswith('|'):
                table_lines.append(lines[i].strip()); i += 1
            rows = [[c.strip() for c in tl.split('|')[1:-1]] for tl in table_lines]
            data_rows = [r for r in rows if not all(re.match(r'^[-:]+$', c) for c in r)]
            if len(data_rows) >= 2:
                h, br = data_rows[0], data_rows[1:]
                hrow = '<thead><tr>' + ''.join(f'<th>{make_badges(md_para(c))}</th>' for c in h) + '</tr></thead>'
                brows = '<tbody>' + ''.join('<tr>' + ''.join(f'<td>{make_badges(md_para(c))}</td>' for c in r) + '</tr>' for r in br) + '</tbody>'
                result.append(f'<div class="table-wrap"><table>{hrow}{brows}</table></div>')
            elif len(data_rows) == 1:
                result.append(f'<div class="table-wrap"><table><tbody>{"".join("<tr>"+"".join(f"<td>{make_badges(md_para(c))}</td>" for c in r)+"</tr>" for r in data_rows)}</tbody></table></div>')
            continue
        result.append(f'<p>{make_badges(md_para(s))}</p>')
        i += 1
    return '\n'.join(result)


# ---- Dashboard ----

def build_stats_row(rows_data, max_items=8, use_summary_cards=True):
    """Build stats row + optional summary cards from table data rows."""
    stats = []
    for row in rows_data[:max_items]:
        label = row[0] if len(row) > 0 else ''
        value = row[1] if len(row) > 1 else ''
        direction = row[3] if len(row) > 3 else ''
        cls = num_color(direction + ' ' + value, label)
        stats.append(f'<div class="stat-item"><div class="num{(" "+cls) if cls else ""}">{md_para(value)}</div><div class="lbl">{md_para(label)}</div></div>')
    stats_html = '<div class="stats">\n  ' + '\n  '.join(stats) + '\n</div>'

    if not use_summary_cards or len(rows_data) <= max_items:
        return stats_html

    cards = []
    for row in rows_data:
        label = row[0] if len(row) > 0 else ''
        value = row[1] if len(row) > 1 else ''
        extra = row[2] if len(row) > 2 else ''
        direction = row[3] if len(row) > 3 else ''
        cards.append(f'<div class="summary-card"><div class="label">{md_para(label)}</div><div class="value">{md_para(value)}</div><div style="color: var(--muted); font-size: 0.82em; margin-top: 4px;">{md_para(direction)} | {md_para(extra)}</div></div>')
    return stats_html + '\n<div class="summary-grid">\n' + '\n'.join(cards) + '\n</div>'


def build_dashboard(section_body_text):
    lines = [l.strip() for l in section_body_text.split('\n') if l.strip().startswith('|')]
    if not lines: return None
    rows = [[c.strip() for c in l.split('|')[1:-1]] for l in lines]
    data_rows = [r for r in rows if not all(re.match(r'^[-:]+$', c) for c in r)]
    if len(data_rows) < 2: return None
    return build_stats_row(data_rows[1:], max_items=6)

def build_stats_only(section_body_text):
    lines = [l.strip() for l in section_body_text.split('\n') if l.strip().startswith('|')]
    if not lines: return None
    rows = [[c.strip() for c in l.split('|')[1:-1]] for l in lines]
    data_rows = [r for r in rows if not all(re.match(r'^[-:]+$', c) for c in r)]
    if len(data_rows) < 2: return None
    return build_stats_row(data_rows[1:], max_items=8, use_summary_cards=False)


# ---- Section ID & Label ----

SECTION_IDS = {
    'dash': 'dashboard', '核心': 'verdict', '判断': 'verdict', '结论': 'verdict',
    '阶段': 'phases', '周期': 'phases',
    '概念': 'rotations', '轮动': 'rotations',
    '主线': 'markets', '美股': 'markets', 'a股': 'markets', '港股': 'markets',
    '供应': 'supplychain',
    '一级市场': 'private', '信用': 'private', 'vc': 'private',
    'capex': 'caperoi', 'roi': 'caperoi', '泡沫': 'caperoi',
    '生产力': 'productivity', '经济': 'productivity',
    'bull': 'bullbear', 'bear': 'bullbear', 'contrarian': 'bullbear',
    '乐观': 'bullbear', '悲观': 'bullbear', '重构': 'bullbear', '建议': 'bullbear', 'action': 'bullbear',
    '预测': 'predictions', '未来': 'predictions',
    '信号': 'monitor', '监测': 'monitor', '看板': 'monitor',
    '数字': 'numbers', '关键': 'numbers',
}

def make_section_id(title):
    t = title.lower()
    for kw, sid in SECTION_IDS.items():
        if kw in t: return sid
    return slugify(title)[:30]

def detect_section_label(title, body_text=''):
    t = title.lower()
    if 'dashboard' in t: return 'Key Metrics Dashboard'
    if '核心' in title or '判断' in title: return 'Core Verdict'
    if '阶段' in title or '周期' in title: return 'Market Cycle'
    if '概念' in title or '轮动' in title: return 'Concept → Rotation Mapping'
    if '主线' in title or '美股' in title: return 'Market Structure'
    if '供应' in title: return 'Global Supply Chain'
    if '一级市场' in title or '信用' in title: return 'Private Markets & Credit'
    if 'capex' in t or '泡沫' in title: return 'Capex ROI · Bubble Detection'
    if '生产力' in title or ('经济' in title and 'ai' in t): return 'Productivity · The Ultimate Question'
    if 'bull' in t or 'bear' in t or 'contrarian' in t: return 'Three Perspectives'
    if '乐观' in title or '悲观' in title or '重构' in title: return 'Three Perspectives'
    if '建议' in title or 'action' in t: return 'Action Recommendations'
    if '预测' in title or '未来' in title: return 'Forward Predictions'
    if '信号' in title or '监测' in title: return 'Monitoring Dashboard'
    if '数字' in title or '关键' in title: return 'Key Numbers Summary'
    return None


# ---- Timeline detection ----

def detect_timeline(body_text):
    """Detect Phase patterns (list or table) and convert to timeline HTML."""
    # Pattern A: List-based phases (### Phase 1: ... or **Phase 1** ...)
    phases = re.findall(
        r'(?:###?\s*)?(?:Phase\s*(\d)|阶段\s*(\d))\s*[:：\s\-]*(.*?)(?=\n*(?:###?\s*(?:Phase|阶段)|\Z))',
        body_text, re.DOTALL | re.IGNORECASE
    )
    if len(phases) >= 3:
        return _build_timeline_from_phases(phases)

    # Pattern B: Table with 阶段/Phase column
    table_match = re.search(r'\|.+阶段.+特征.+触发事件.+\|[\s\S]*?(?=\n\n|\n---|\n##|\Z)', body_text)
    if table_match:
        return _build_timeline_from_table(table_match.group(0))

    return None


def _build_timeline_from_phases(phases):
    items = []
    for p in phases:
        num = p[0] or p[1]
        content = p[2].strip()
        clines = content.strip().split('\n')
        title = clines[0].strip() if clines else f'Phase {num}'
        meta = ''
        body_lines = clines[1:]
        if body_lines and re.match(r'\d{4}', body_lines[0].strip()):
            meta = body_lines[0].strip(); body_lines = body_lines[1:]
        bullets = [l.strip()[2:] for l in body_lines if l.strip().startswith('- ')]
        if not bullets:
            bullets = [l.strip() for l in body_lines if l.strip() and not l.strip().startswith('|')][:3]
        items.append(f'<div class="phase"><div class="phase-dot">{num}</div><h3>{make_badges(md_para(title))}</h3><div class="meta">{md_para(meta)}</div><ul>{"".join(f"<li>{make_badges(md_para(b))}</li>" for b in bullets)}</ul></div>')
    return '<div class="timeline">\n' + '\n'.join(items) + '\n</div>'


def _build_timeline_from_table(table_text):
    """Convert a phase table (阶段|时间|特征|触发事件|标志性数据) to timeline HTML."""
    lines = [l.strip() for l in table_text.split('\n') if l.strip().startswith('|')]
    rows = [[c.strip() for c in l.split('|')[1:-1]] for l in lines]
    data_rows = [r for r in rows if not all(re.match(r'^[-:]+$', c) for c in r)]
    if len(data_rows) < 3:
        return None

    header, body = data_rows[0], data_rows[1:]
    # Map columns: look for phase name, time, characteristic, trigger, data
    col_map = {}
    for idx, h in enumerate(header):
        hl = h.lower()
        if '阶段' in hl or 'phase' in hl: col_map['name'] = idx
        elif '时间' in hl or 'period' in hl: col_map['time'] = idx
        elif '特征' in hl or 'characteristic' in hl: col_map['feature'] = idx
        elif '触发' in hl or 'trigger' in hl: col_map['trigger'] = idx
        elif '数据' in hl or '标志' in hl or 'data' in hl: col_map['data'] = idx

    items = []
    for i, row in enumerate(body):
        name = row[col_map.get('name', 0)] if 'name' in col_map else f'Phase {i+1}'
        time_val = row[col_map.get('time', 1)] if 'time' in col_map else ''
        feature = row[col_map.get('feature', 2)] if 'feature' in col_map else ''
        trigger = row[col_map.get('trigger', 3)] if 'trigger' in col_map else ''
        data_val = row[col_map.get('data', 4)] if 'data' in col_map else ''

        bullets = []
        if feature: bullets.append(f'<strong>{make_badges(md_para(feature))}</strong>')
        if trigger: bullets.append(f'触发：{make_badges(md_para(trigger))}')
        if data_val: bullets.append(make_badges(md_para(data_val)))

        items.append(f'''<div class="phase">
      <div class="phase-dot">{i+1}</div>
      <h3>{make_badges(md_para(name))}</h3>
      <div class="meta">{md_para(time_val)}</div>
      <ul>{"".join(f"<li>{b}</li>" for b in bullets)}</ul>
    </div>''')

    return '<div class="timeline">\n' + '\n'.join(items) + '\n</div>'


# ---- Grid detection ----

def wrap_grids(body_html):
    """Detect consecutive card-like patterns and wrap in grid-2 or grid-3."""
    # Pattern: consecutive <h3> + <p> + <ul> or consecutive <p><strong> blocks
    # Wrap sequences of 2-3 similar adjacent blocks in grid divs

    # Split body into blocks (between h3 or h4 or hr or <p><strong> markers)
    blocks = re.split(r'(?=<h3>|<h4>|(?:<p><strong>(?!.*</strong></p>)))', body_html)
    if len(blocks) < 2:
        return body_html

    result = []
    i = 0
    while i < len(blocks):
        # Look ahead for 2-3 consecutive card-like blocks
        j = i
        while j < len(blocks) and (
            blocks[j].strip().startswith('<h3>') or
            blocks[j].strip().startswith('<h4>') or
            (blocks[j].strip().startswith('<p><strong>') and '<ul>' in blocks[j])
        ):
            j += 1
        count = j - i

        if count in (2, 3):
            cards = []
            for k in range(i, j):
                block = blocks[k].strip()
                # Color border based on content sentiment
                bl = block.lower()
                border_color = ''
                if any(w in bl for w in ['bear', '悲观', 'risk', 'fail', '失败', 'crash', 'collapse', 'danger', 'red', 'c-red']):
                    border_color = ' style="border-left: 3px solid var(--red);"'
                elif any(w in bl for w in ['bull', '乐观', 'green', 'growth', 'win', 'success', 'leader', 'c-green']):
                    border_color = ' style="border-left: 3px solid var(--green);"'
                elif any(w in bl for w in ['warn', 'watch', 'yellow', 'c-yellow', 'caution', 'marginal']):
                    border_color = ' style="border-left: 3px solid var(--yellow);"'
                elif count == 3 and k == i:
                    border_color = ' style="border-left: 3px solid var(--green);"'
                elif count == 3 and k == i + 1:
                    border_color = ' style="border-left: 3px solid var(--yellow);"'
                elif count == 3 and k == i + 2:
                    border_color = ' style="border-left: 3px solid var(--red);"'

                cards.append(f'<div class="card"{border_color}>\n{block}\n</div>')

            grid_cls = 'grid-3' if count == 3 else 'grid-2'
            result.append(f'<div class="{grid_cls}">\n' + '\n'.join(cards) + '\n</div>')
            i = j
        else:
            result.append(blocks[i])
            i += 1

    return '\n'.join(result)


def strip_html(text):
    """Remove HTML tags for use in plain-text contexts."""
    return re.sub(r'<[^>]+>', '', text).strip()

# ---- Info/Warn box detection ----

def detect_info_warn_boxes(body_html):
    """Wrap KEY INSIGHT / WARNING patterns in info-box or warn-box."""
    # Info box patterns (handle badge spans intermixed with strong text)
    info_patterns = [
        (r'<p(?: class="[^"]*")?><strong>(SOLOW PARADOX[\s\S]*?)</strong>([\s\S]*?)</p>',
         lambda m: f'<div class="info-box"><div class="icon">{strip_html(m.group(1))[:60]}</div><p style="font-size:0.85rem; color: var(--muted); line-height:1.7;">{m.group(2).strip()}</p></div>'),
        (r'<li>(?:<span[^>]*>[^<]*</span>\s*)*<strong>(概念衰减[^<]*)</strong>([\s\S]*?)</li>',
         lambda m: f'<div class="info-box"><div class="icon">KEY INSIGHT · {m.group(1).strip()}</div><p style="font-size:0.85rem; color: var(--muted); line-height:1.7;">{m.group(2).strip()}</p></div>'),
    ]
    for pat, repl in info_patterns:
        body_html = re.sub(pat, repl, body_html, flags=re.DOTALL)

    # Warn box patterns
    warn_patterns = [
        (r'<p(?: class="[^"]*")?><strong>(SINGLE POINT[\s\S]*?)</strong>([\s\S]*?)</p>',
         lambda m: f'<div class="warn-box"><div class="icon">⚠ {strip_html(m.group(1))[:60]}</div><p style="font-size:0.85rem; color: var(--muted); line-height:1.7;">{m.group(2).strip()}</p></div>'),
    ]
    for pat, repl in warn_patterns:
        body_html = re.sub(pat, repl, body_html, flags=re.DOTALL)
    return body_html


# ---- Verdict detection ----

def detect_verdict(body_html, section_title):
    """Wrap sections with verdict keywords in verdict box."""
    if re.search(r'核心判断|中心论点|一句话推荐|泡沫诊断|条件式结论', section_title):
        # Wrap first strong paragraph in verdict
        body_html = re.sub(
            r'(<p><strong>.+?</strong></p>)',
            r'<div class="verdict">\n<div class="k">裁决</div>\n\1\n</div>',
            body_html, count=1
        )
        # If already has verdict pattern, don't double-wrap
        if '<div class="verdict">' not in body_html:
            body_html = f'<div class="verdict">\n<div class="k">裁决</div>\n{body_html}\n</div>'
    return body_html


# ---- Highlight boxes ----

def detect_highlight_boxes(body_html, section_title):
    if re.search(r'Bull Case|bull case|乐观观点|BULL', section_title):
        return f'<div class="highlight-box green">\n{body_html}\n</div>'
    if re.search(r'Bear Case|bear case|悲观观点|BEAR', section_title):
        return f'<div class="highlight-box red">\n{body_html}\n</div>'
    if re.search(r'Contrarian|重构|CONTRARIAN', section_title):
        return f'<div class="highlight-box">\n{body_html}\n</div>'
    if re.search(r'Action|建议|ACTION', section_title):
        return f'<div class="highlight-box yellow">\n{body_html}\n</div>'
    return body_html


# ---- Post-processing ----

def post_process(body_html):
    """Clean up common artifacts."""
    # Remove duplicate h3 that matches h2 (Dashboard → Dashboard)
    body_html = re.sub(r'<h3>(Dashboard|看板|仪表盘|Key Metrics)</h3>\s*', '', body_html)
    # Remove empty <p></p>
    body_html = re.sub(r'<p>\s*</p>\s*', '', body_html)
    # Remove h3/h4 that are just numbers or section labels
    body_html = re.sub(r'<h3>\s*(Level \d|Phase \d)\s*</h3>', r'<h3 style="margin-top:1.5rem;">\1</h3>', body_html)
    # Add table-wrap to any naked <table> not already wrapped
    body_html = re.sub(r'(?<!wrap">)(<table>)', r'<div class="table-wrap">\1', body_html)
    body_html = re.sub(r'(</table>)(?!</div>)', r'\1</div>', body_html)
    return body_html


def extract_section_desc(body_text):
    """Extract first paragraph as section description."""
    lines = body_text.strip().split('\n')
    for line in lines:
        s = line.strip()
        if not s or s.startswith('#') or s.startswith('|') or s.startswith('-') or s.startswith('>') or s == '---':
            continue
        # Must be a real paragraph (not a single word)
        if len(s) > 20 and not s.startswith('```'):
            return make_badges(md_para(s))
    return ''


# ---- Main ----

def convert(md_path):
    with open(md_path, 'r') as f:
        md = f.read()

    report_dir = os.path.dirname(os.path.abspath(md_path))
    topic_slug = os.path.basename(report_dir)
    today = datetime.date.today().isoformat()

    # ---- Extract metadata ----
    title_match = re.search(r'^# (.+)$', md, re.MULTILINE)
    report_title = title_match.group(1).strip() if title_match else 'Deep Analysis Report'

    # Try to split title for hero: "Main Title：Subtitle" → h1 with <span>
    hero_title_html = make_badges(md_para(report_title))
    if '：' in report_title:
        parts = report_title.split('：', 1)
        hero_title_html = f'{make_badges(md_para(parts[0]))}：<br><span>{make_badges(md_para(parts[1]))}</span>'
    elif '——' in report_title:
        parts = report_title.split('——', 1)
        hero_title_html = f'{make_badges(md_para(parts[0]))}<br><span>{make_badges(md_para(parts[1]))}</span>'

    # Hero subtitle: first blockquote after title, cleaned
    hero_sub = ''
    hero_meta = ''
    bq_match = re.search(r'^# .+\n+(?:> .+\n*)+', md, re.MULTILINE)
    if bq_match:
        bq_lines = [strip_md(l.strip()[2:]) for l in bq_match.group(0).split('\n') if l.strip().startswith('>')]
        if bq_lines:
            hero_meta = ' · '.join(bq_lines[:2])
        if len(bq_lines) > 2:
            hero_sub = '<br>'.join(bq_lines[2:])

    # Count stats
    agent_matches = re.findall(r'(\d+)\s*(?:个\s*)?Agent', md)
    agent_count = agent_matches[0] if agent_matches else ''
    search_matches = re.findall(r'(\d+)\+?\s*(?:次\s*)?Web\s*Search', md)
    search_count = search_matches[0] if search_matches else ''

    # ---- Split into sections ----
    sections_raw = re.split(r'\n(?=## )', md)
    nav_links = []
    seen_ids = set()
    all_sections_html = []

    for section in sections_raw:
        lines = section.strip().split('\n')
        if not lines: continue

        first_line = lines[0].strip()

        # h1 — extract for hero
        if first_line.startswith('# ') and not first_line.startswith('## '):
            rest = '\n'.join(lines[1:]).strip()
            if rest and not hero_sub:
                cleaned = strip_md(re.sub(r'^> ', '', rest, flags=re.MULTILINE))
                hero_sub = cleaned[:200]
            continue

        if first_line.startswith('## '):
            title_text = first_line[3:].strip()
            body_text = '\n'.join(lines[1:])
            section_id = make_section_id(title_text)
            label = detect_section_label(title_text, body_text)

            # Render body
            body_html = render_md_body(body_text)

            # ---- Component detection pipeline ----

            # 1. Dashboard
            is_dashboard = any(w in title_text.lower() for w in ['dashboard', '看板', '仪表盘'])
            is_dashboard = is_dashboard or (label and 'Dashboard' in label)
            if is_dashboard and not DASHBOARD_OFF:
                table_match = re.search(r'\|.+?\|[\s\S]*?(?=\n\n|\n---|\n##|\Z)', body_text)
                if table_match:
                    cards = build_dashboard(table_match.group(0))
                    if not cards:
                        cards = build_stats_only(table_match.group(0))
                    if cards:
                        th = re.search(r'<div class="table-wrap"><table>(.+?)</table></div>', body_html, re.DOTALL)
                        if th:
                            body_html = body_html.replace(th.group(0), cards)

            # 2. Timeline (Phase 1-5 patterns)
            if any(w in title_text for w in ['阶段', '周期', 'Phase']):
                timeline = detect_timeline(body_text)
                if timeline:
                    # Replace first table with timeline
                    first_table = re.search(r'<div class="table-wrap"><table>.+?</table></div>', body_html, re.DOTALL)
                    if first_table:
                        body_html = body_html.replace(first_table.group(0), timeline)

            # 3. Info/warn boxes
            body_html = detect_info_warn_boxes(body_html)

            # 4. Verdict
            body_html = detect_verdict(body_html, title_text)

            # 5. Highlight boxes
            body_html = detect_highlight_boxes(body_html, title_text)

            # 6. Grid wrapping (for card patterns)
            body_html = wrap_grids(body_html)

            # 7. Post-process
            body_html = post_process(body_html)

            # Section-desc extraction
            section_desc = extract_section_desc(body_text)

            # Nav link (only add if ID is unique)
            nav_label = strip_md(title_text)[:14]
            if section_id not in seen_ids:
                nav_links.append((section_id, nav_label))
                seen_ids.add(section_id)

            # Section assembly
            label_html = f'<div class="section-label">{label}</div>\n' if label else ''
            desc_html = f'<p class="section-desc">{section_desc}</p>\n' if section_desc else ''
            section_html = f'''<section id="{section_id}" class="fade-in">
  {label_html}<h2 class="section-title">{make_badges(md_para(title_text))}</h2>
  {desc_html}{body_html}
</section>'''
            all_sections_html.append(section_html)

    body_content = '\n\n'.join(all_sections_html)

    # ---- Build nav ----
    nav_html = '\n    '.join(f'<a href="#{sid}">{lbl}</a>' for sid, lbl in nav_links[:15])
    nav_title = strip_md(report_title)[:16]

    # ---- Build hero ----
    version_parts = [f'v1.0 · {today}']
    if agent_count: version_parts.append(f'{agent_count} Agents')
    if search_count: version_parts.append(f'{search_count}+ Web Searches')
    version_str = ' · '.join(version_parts)

    hero_html = f'''<section class="hero">
  <div class="hero-version">{version_str}</div>
  <div class="hero-label">Deep Thinking Report · Synthesis</div>
  <h1>{hero_title_html}</h1>
  <p class="hero-sub">{hero_sub if hero_sub else ''}</p>
  <p class="hero-meta">{hero_meta if hero_meta else ''}</p>
</section>'''

    # ---- Fill template ----
    with open(TEMPLATE_PATH, 'r') as f:
        template = f.read()

    html = template.replace('{{TITLE}}', report_title)
    html = html.replace('{{NAV_TITLE}}', nav_title)
    html = html.replace('{{NAV_LINKS}}', nav_html)
    html = html.replace('{{HERO}}', hero_html)
    html = html.replace('{{FOOTER_TITLE}}', f'{report_title} · {today}')
    html = html.replace('{{FOOTER_SUB}}', f'{len(sections_raw)-1} sections · {len(nav_links)} nav anchors · deep-thinking analysis')
    html = html.replace('<!-- CONTENT -->', body_content)

    # Final cleanup
    html = re.sub(r'<p>&lt;div[^&]*&gt;</p>\s*', '', html)
    html = re.sub(r'<p>&lt;/div&gt;</p>\s*', '', html)

    # ---- Output ----
    output_path = os.path.join(report_dir, f'{topic_slug}-final-report.html')
    with open(output_path, 'w') as f:
        f.write(html)

    # ---- Quality report ----
    checks = {
        'stat-cards': body_content.count('stat-item') + body_content.count('summary-card'),
        'highlight-box': body_content.count('highlight-box'),
        'verdict': body_content.count('verdict'),
        'timeline': body_content.count('timeline'),
        'grid-2/3': body_content.count('grid-2') + body_content.count('grid-3'),
        'info/warn-box': body_content.count('info-box') + body_content.count('warn-box'),
        'badge-green (FACT)': body_content.count('badge-green'),
        'badge-yellow (JUDGMENT)': body_content.count('badge-yellow'),
        'tables': body_content.count('<table>'),
        'sections': body_content.count('<section'),
        'nav-links': len(nav_links),
    }

    print(f"HTML generated: {output_path}")
    print(f"Size: {len(html):,} chars")
    print(f"Template: Beijing white-card v3 (sticky-nav + stats + cards + grids + highlight/info/warn)")
    print(f"Components:")
    for name, count in checks.items():
        status = "✓" if count > 0 else "✗ MISSING"
        print(f"  {status} {name}: {count}")

    return output_path


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 generate_html.py <path-to-report.md>")
        sys.exit(1)
    md_path = sys.argv[1]
    DASHBOARD_OFF = '<!-- dashboard:off -->' in open(md_path, encoding='utf-8').read()
    if not os.path.exists(md_path):
        print(f"Error: file not found: {md_path}")
        sys.exit(1)
    convert(md_path)
