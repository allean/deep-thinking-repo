#!/usr/bin/env python3
"""Batch convert all MD files in a directory to HTML with dark theme + index.
Usage: python3 convert_all_md.py <target-directory>
Output: HTML files alongside MD files + index.html in target directory.
"""
import re
import sys
from pathlib import Path

CSS = """<style>
  :root { --bg: #0d1117; --surface: #161b22; --border: #30363d; --text: #c9d1d9; --muted: #8b949e; --accent: #58a6ff; --green: #3fb950; --yellow: #d2991d; --red: #f85149; }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { background: var(--bg); color: var(--text); font-family: -apple-system, "PingFang SC", "Microsoft YaHei", sans-serif; line-height: 1.7; max-width: 920px; margin: 0 auto; padding: 40px 24px; }
  h1 { font-size: 1.8em; border-bottom: 2px solid var(--accent); padding-bottom: 12px; margin: 0 0 8px; color: #fff; }
  h2 { font-size: 1.4em; margin: 48px 0 16px; padding: 8px 0; border-bottom: 1px solid var(--border); color: #f0f6fc; }
  h3 { font-size: 1.15em; margin: 28px 0 10px; color: #e6edf3; }
  h4 { font-size: 1.05em; margin: 20px 0 8px; color: #e6edf3; }
  p { margin: 10px 0; }
  blockquote { border-left: 3px solid var(--accent); padding: 8px 16px; margin: 16px 0; background: var(--surface); border-radius: 0 6px 6px 0; color: var(--muted); }
  table { width: 100%; border-collapse: collapse; margin: 16px 0; font-size: 0.92em; }
  th { background: var(--surface); text-align: left; padding: 10px 14px; border-bottom: 2px solid var(--border); font-weight: 600; color: #e6edf3; }
  td { padding: 9px 14px; border-bottom: 1px solid var(--border); vertical-align: top; }
  tr:hover { background: rgba(88,166,255,0.04); }
  code { background: var(--surface); padding: 2px 6px; border-radius: 4px; font-size: 0.9em; }
  pre { background: var(--surface); padding: 16px 20px; border-radius: 8px; overflow-x: auto; margin: 16px 0; border: 1px solid var(--border); font-size: 0.88em; line-height: 1.6; }
  pre code { background: none; padding: 0; }
  ul, ol { margin: 8px 0 8px 24px; }
  li { margin: 4px 0; }
  a { color: var(--accent); text-decoration: none; }
  a:hover { text-decoration: underline; }
  hr { border: none; border-top: 1px solid var(--border); margin: 40px 0; }
  strong { color: #fff; }
  .nav { background: var(--surface); border: 1px solid var(--border); border-radius: 8px; padding: 20px 24px; margin: 28px 0; }
  .nav h3 { margin: 0 0 10px; }
  .highlight-box { border-left: 4px solid var(--accent); padding: 14px 18px; margin: 20px 0; background: var(--surface); border-radius: 0 8px 8px 0; }
  .highlight-box.green { border-left-color: var(--green); }
  .highlight-box.yellow { border-left-color: var(--yellow); }
  .highlight-box.red { border-left-color: var(--red); }
  .badge { display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 0.78em; font-weight: 600; }
  .badge-green { background: rgba(63,185,80,0.15); color: var(--green); }
  .badge-yellow { background: rgba(210,153,29,0.15); color: var(--yellow); }
  .badge-red { background: rgba(248,81,73,0.15); color: var(--red); }
</style>"""


def md_to_html(text: str) -> str:
    lines = text.split('\n')
    out = []
    i = 0
    in_code_block = False
    code_lang = ''
    code_lines = []
    in_table = False
    table_rows = []
    in_list = False
    list_type = None

    def flush_table():
        nonlocal in_table, table_rows
        if not table_rows:
            return
        html = '<table>\n'
        for ri, row in enumerate(table_rows):
            tag = 'th' if ri == 0 else 'td'
            html += '<tr>\n'
            for cell in row:
                cell_html = process_inline(cell.strip())
                html += f'<{tag}>{cell_html}</{tag}>\n'
            html += '</tr>\n'
        html += '</table>\n'
        out.append(html)
        table_rows = []
        in_table = False

    def flush_list():
        nonlocal in_list, list_type
        if in_list and list_type:
            out.append(f'</{list_type}>\n')
        in_list = False
        list_type = None

    def flush_code_block():
        nonlocal in_code_block, code_lines, code_lang
        lang_attr = f' class="language-{code_lang}"' if code_lang else ''
        code = '\n'.join(code_lines).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        out.append(f'<pre><code{lang_attr}>{code}</code></pre>')
        code_lines = []
        code_lang = ''
        in_code_block = False

    def process_inline(text: str) -> str:
        text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
        text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)
        text = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', r'<img src="\2" alt="\1">', text)
        text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)
        text = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', text)
        return text

    while i < len(lines):
        line = lines[i]
        if line.strip().startswith('```'):
            if in_code_block:
                flush_code_block()
            else:
                in_code_block = True
                code_lang = line.strip()[3:].strip()
            i += 1
            continue
        if in_code_block:
            code_lines.append(line)
            i += 1
            continue

        stripped = line.strip()

        if '|' in stripped and stripped.startswith('|'):
            if in_list:
                flush_list()
            if not in_table:
                in_table = True
                table_rows = []
            if re.match(r'^[\|\s\-:]+$', stripped):
                i += 1
                continue
            cells = [c for c in stripped.split('|')]
            if cells and cells[0] == '':
                cells = cells[1:]
            if cells and cells[-1] == '':
                cells = cells[:-1]
            table_rows.append(cells)
            i += 1
            continue
        elif in_table:
            flush_table()

        if not stripped:
            if in_list:
                flush_list()
            i += 1
            continue

        h = re.match(r'^(#{1,6})\s+(.+)$', stripped)
        if h:
            if in_list:
                flush_list()
            level = len(h.group(1))
            content = process_inline(h.group(2))
            out.append(f'<h{level}>{content}</h{level}>\n')
            i += 1
            continue

        if re.match(r'^[-*_]{3,}$', stripped):
            if in_list:
                flush_list()
            out.append('<hr>\n')
            i += 1
            continue

        if stripped.startswith('>'):
            if in_list:
                flush_list()
            quote_lines = []
            while i < len(lines) and lines[i].strip().startswith('>'):
                q = lines[i].strip()
                q = re.sub(r'^>\s?', '', q)
                quote_lines.append(process_inline(q))
                i += 1
            quote_html = '<br>'.join(quote_lines)
            out.append(f'<blockquote>{quote_html}</blockquote>\n')
            continue

        ul = re.match(r'^(\s*)[-*]\s+(.+)$', stripped)
        if ul:
            if in_list and list_type != 'ul':
                flush_list()
            if not in_list:
                in_list = True
                list_type = 'ul'
                out.append('<ul>\n')
            content = process_inline(ul.group(2))
            out.append(f'<li>{content}</li>\n')
            i += 1
            continue

        ol = re.match(r'^(\s*)\d+[.)]\s+(.+)$', stripped)
        if ol:
            if in_list and list_type != 'ol':
                flush_list()
            if not in_list:
                in_list = True
                list_type = 'ol'
                out.append('<ol>\n')
            content = process_inline(ol.group(2))
            out.append(f'<li>{content}</li>\n')
            i += 1
            continue

        if in_list:
            flush_list()
        content = process_inline(stripped)
        out.append(f'<p>{content}</p>\n')
        i += 1

    if in_code_block:
        flush_code_block()
    if in_table:
        flush_table()
    if in_list:
        out.append(f'</{list_type}>\n')
    return '\n'.join(out)


def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <target-directory>")
        sys.exit(1)

    root = Path(sys.argv[1]).resolve()
    if not root.is_dir():
        print(f"Error: {root} is not a directory")
        sys.exit(1)

    md_files = {}
    for md in sorted(root.rglob('*.md')):
        rel = md.relative_to(root)
        md_files[str(rel)] = md

    print(f"Found {len(md_files)} MD files in {root}")
    converted = 0

    # Detect final-report and playbook paths for navbar linking
    final_report_html = None
    playbook_html = None
    for rel_path in md_files:
        if 'final-report' in rel_path.lower():
            final_report_html = rel_path.replace('.md', '.html')
        if 'playbook' in rel_path.lower():
            playbook_html = rel_path.replace('.md', '.html')

    nav_links = []
    if final_report_html:
        nav_links.append(f'<a href="{final_report_html}">← 主报告</a>')
    if playbook_html:
        nav_links.append(f'<a href="{playbook_html}">操作手册</a>')
    nav_links.append('<a href="index.html">全部文档</a>')
    nav_bar = ' · '.join(nav_links)

    for rel_path, md_path in sorted(md_files.items()):
        html_path = md_path.with_suffix('.html')
        try:
            text = md_path.read_text(encoding='utf-8')
        except Exception as e:
            print(f"  SKIP {rel_path}: {e}")
            continue

        title = Path(rel_path).stem.replace('-', ' ').replace('_', ' ')
        body = md_to_html(text)
        body = re.sub(r'href="([^"]+)\.md"', r'href="\1.html"', body)
        body = re.sub(r'href="([^"]+)\.md#', r'href="\1.html#', body)

        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
{CSS}
</head>
<body>
<div class="nav" style="margin-bottom:24px">{nav_bar}</div>
{body}
<div class="nav" style="margin-top:40px">
  <h3>📂 快速导航</h3>
  {nav_bar}
</div>
</body>
</html>"""
        html_path.write_text(html, encoding='utf-8')
        converted += 1
        print(f"  ✓ {rel_path} → {html_path.name}")

    # Build index.html with automatic grouping
    groups = {}
    for rel_path in sorted(md_files.keys()):
        parts = rel_path.split('/')
        group_key = '/'.join(parts[:-1]) if len(parts) > 1 else '(root)'
        if group_key not in groups:
            groups[group_key] = []
        groups[group_key].append(rel_path)

    index_body = f"""<h1>📚 深度分析 — 全部文档</h1>
<div class="nav">{nav_bar}</div>"""

    for group_key in sorted(groups.keys()):
        display_name = group_key
        if group_key == '(root)':
            display_name = '根目录'
        index_body += f'<h2>{display_name}</h2>\n<ul>\n'
        for rel_path in groups[group_key]:
            html_name = rel_path.replace('.md', '.html')
            display = Path(rel_path).stem
            index_body += f'  <li><a href="{html_name}">{display}</a></li>\n'
        index_body += '</ul>\n'

    index_html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>深度分析 — 全部文档索引</title>
{CSS}
</head>
<body>
{index_body}
</body>
</html>"""

    index_path = root / 'index.html'
    index_path.write_text(index_html, encoding='utf-8')
    print(f"  ✓ index.html ({len(md_files)} documents in {len(groups)} groups)")

    # Build all-in-one HTML
    all_in_one_path = build_all_in_one(root, md_files, groups, final_report_html)
    if all_in_one_path:
        print(f"  ✓ {all_in_one_path.name} (merged {len(md_files)} docs)")

    print(f"\nDone: {converted} MD → HTML + index + all-in-one")


def build_all_in_one(root, md_files, groups, final_report_html=None):
    """Merge all generated HTML files into a single self-contained HTML with sidebar navigation."""
    import re as RE

    # Re-read all generated HTML files and extract body content
    sections = []
    nav_items = []
    link_map = {}  # original .html filename -> section anchor id

    ALL_IN_ONE_CSS = """    :root { --bg: #0d1117; --surface: #161b22; --border: #30363d; --text: #c9d1d9; --muted: #8b949e; --accent: #58a6ff; --green: #3fb950; --yellow: #d2991d; --red: #f85149; --sidebar-w: 280px; }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { background: var(--bg); color: var(--text); font-family: -apple-system, "PingFang SC", "Microsoft YaHei", sans-serif; line-height: 1.7; display: flex; }
    #sidebar { position: fixed; left: 0; top: 0; bottom: 0; width: var(--sidebar-w); background: var(--surface); border-right: 1px solid var(--border); overflow-y: auto; padding: 20px 16px; z-index: 10; }
    #sidebar h2 { font-size: 1.1em; color: #fff; margin-bottom: 16px; padding-bottom: 10px; border-bottom: 2px solid var(--accent); }
    #sidebar .nav-cat { font-size: 0.78em; text-transform: uppercase; color: var(--muted); margin: 20px 0 6px; letter-spacing: 0.5px; }
    #sidebar ul { list-style: none; margin: 0; padding: 0; }
    #sidebar li { margin: 2px 0; }
    #sidebar a { display: block; color: var(--text); text-decoration: none; font-size: 0.88em; padding: 4px 10px; border-radius: 4px; transition: all 0.15s; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    #sidebar a:hover { background: rgba(88,166,255,0.08); color: #fff; }
    #sidebar a.active { background: rgba(88,166,255,0.15); color: var(--accent); font-weight: 600; }
    #sidebar-toggle { display: none; position: fixed; top: 12px; left: 12px; z-index: 20; background: var(--surface); border: 1px solid var(--border); color: var(--text); padding: 8px 12px; border-radius: 6px; cursor: pointer; font-size: 1.1em; }
    #main { margin-left: var(--sidebar-w); flex: 1; max-width: 960px; padding: 40px 32px; min-height: 100vh; }
    section { display: none; }
    section.active { display: block; }
    h1 { font-size: 1.8em; border-bottom: 2px solid var(--accent); padding-bottom: 12px; margin: 0 0 8px; color: #fff; }
    h2 { font-size: 1.4em; margin: 48px 0 16px; padding: 8px 0; border-bottom: 1px solid var(--border); color: #f0f6fc; }
    h3 { font-size: 1.15em; margin: 28px 0 10px; color: #e6edf3; }
    h4 { font-size: 1.05em; margin: 20px 0 8px; color: #e6edf3; }
    p { margin: 10px 0; }
    blockquote { border-left: 3px solid var(--accent); padding: 8px 16px; margin: 16px 0; background: var(--surface); border-radius: 0 6px 6px 0; color: var(--muted); }
    table { width: 100%; border-collapse: collapse; margin: 16px 0; font-size: 0.92em; }
    th { background: var(--surface); text-align: left; padding: 10px 14px; border-bottom: 2px solid var(--border); font-weight: 600; color: #e6edf3; }
    td { padding: 9px 14px; border-bottom: 1px solid var(--border); vertical-align: top; }
    tr:hover { background: rgba(88,166,255,0.04); }
    code { background: var(--surface); padding: 2px 6px; border-radius: 4px; font-size: 0.9em; }
    pre { background: var(--surface); padding: 16px 20px; border-radius: 8px; overflow-x: auto; margin: 16px 0; border: 1px solid var(--border); font-size: 0.88em; line-height: 1.6; }
    pre code { background: none; padding: 0; }
    ul, ol { margin: 8px 0 8px 24px; }
    li { margin: 4px 0; }
    a { color: var(--accent); text-decoration: none; }
    a:hover { text-decoration: underline; }
    hr { border: none; border-top: 1px solid var(--border); margin: 40px 0; }
    strong { color: #fff; }
    .nav { background: var(--surface); border: 1px solid var(--border); border-radius: 8px; padding: 20px 24px; margin: 28px 0; }
    .highlight-box { border-left: 4px solid var(--accent); padding: 14px 18px; margin: 20px 0; background: var(--surface); border-radius: 0 8px 8px 0; }
    .highlight-box.green { border-left-color: var(--green); }
    .highlight-box.yellow { border-left-color: var(--yellow); }
    .highlight-box.red { border-left-color: var(--red); }
    .badge { display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 0.78em; font-weight: 600; }
    .badge-green { background: rgba(63,185,80,0.15); color: var(--green); }
    .badge-yellow { background: rgba(210,153,29,0.15); color: var(--yellow); }
    .badge-red { background: rgba(248,81,73,0.15); color: var(--red); }
    @media (max-width: 768px) {
      #sidebar { left: calc(-1 * var(--sidebar-w)); transition: left 0.25s; }
      #sidebar.open { left: 0; }
      #sidebar-toggle { display: block; }
      #main { margin-left: 0; padding: 20px 16px; }
    }"""

    ALL_IN_ONE_JS = """const sidebar = document.getElementById('sidebar');
const toggle = document.getElementById('sidebar-toggle');
toggle.addEventListener('click', () => sidebar.classList.toggle('open'));

function showSection(id) {
  document.querySelectorAll('#main > section').forEach(s => s.classList.remove('active'));
  const sec = document.getElementById(id);
  if (sec) { sec.classList.add('active'); }
  document.querySelectorAll('#sidebar a').forEach(a => a.classList.remove('active'));
  const link = document.querySelector(`#sidebar a[data-section="${id}"]`);
  if (link) { link.classList.add('active'); link.scrollIntoView({block: 'nearest'}); }
  document.getElementById('main').scrollTop = 0;
  window.scrollTo(0, 0);
  history.replaceState(null, '', '#' + id);
  sidebar.classList.remove('open');
}

document.getElementById('main').addEventListener('click', function(e) {
  const link = e.target.closest('a');
  if (!link) return;
  const href = link.getAttribute('href');
  if (!href || !href.startsWith('#')) return;
  const targetId = href.substring(1);
  const target = document.getElementById(targetId);
  if (target && target.closest('#main')) {
    e.preventDefault();
    showSection(targetId);
  }
});

document.getElementById('sidebar').addEventListener('click', function(e) {
  const link = e.target.closest('a');
  if (!link) return;
  const href = link.getAttribute('href');
  if (!href || !href.startsWith('#')) return;
  e.preventDefault();
  const targetId = href.substring(1);
  showSection(targetId);
});

const hash = window.location.hash.substring(1);
const defaultId = document.getElementById('FINAL-REPORT-SECTION') ? 'FINAL-REPORT-SECTION' : null;
showSection(hash || defaultId || document.querySelector('#main > section').id);"""

    for group_key in sorted(groups.keys()):
        display_name = group_key
        if group_key == '(root)':
            display_name = '根目录'
        elif '/' in group_key:
            display_name = group_key

        cat_items = []
        for rel_path in groups[group_key]:
            html_path = root / rel_path.replace('.md', '.html')
            if not html_path.exists():
                continue
            html_text = html_path.read_text(encoding='utf-8')

            # Extract body content between <body> and </body>
            body_match = RE.search(r'<body>(.*?)</body>', html_text, RE.DOTALL)
            if not body_match:
                continue
            body = body_match.group(1)

            # Extract title from h1
            title_match = RE.search(r'<h1>(.*?)</h1>', body)
            title = title_match.group(1) if title_match else Path(rel_path).stem

            # Generate stable section id
            sec_id = 'sec-' + RE.sub(r'[^a-zA-Z0-9-]', '-', Path(rel_path).stem).strip('-')

            # Build link map
            html_name = rel_path.replace('.md', '.html')
            link_map[html_name] = sec_id
            link_map[Path(html_name).name] = sec_id
            # Also map the md name
            md_name = Path(rel_path).name
            link_map[md_name] = sec_id

            # Strip nav bars
            body = RE.sub(r'<div class="nav".*?</div>', '', body, flags=RE.DOTALL)

            sections.append(f'<section id="{sec_id}">{body}</section>')
            cat_items.append(f'<li><a href="#{sec_id}" data-section="{sec_id}">{title}</a></li>')

        if cat_items:
            nav_items.append(f'<h3 class="nav-cat">{display_name}</h3>')
            nav_items.append('<ul>' + '\n'.join(cat_items) + '</ul>')

    # Convert cross-document links to internal anchors
    sections_merged = '\n'.join(sections)

    def replace_link(m):
        href = m.group(1)
        if href.startswith('#'):
            return m.group(0)
        # Try exact match
        if href in link_map:
            return f'href="#{link_map[href]}"'
        # Try just the basename
        base = Path(href).name
        if base in link_map:
            return f'href="#{link_map[base]}"'
        # Try with .html extension
        if not base.endswith('.html') and (base + '.html') in link_map:
            return f'href="#{link_map[base + ".html"]}"'
        return m.group(0)

    sections_merged = RE.sub(r'href="([^"]+)"', replace_link, sections_merged)

    # Determine output filename
    slug = root.name
    output_name = f"{slug}-all-in-one.html" if slug else "all-in-one.html"

    # Find the main report section for default display
    final_report_sec_id = None
    for rel_path in groups.get('(root)', []) + groups.get('', []):
        if 'final-report' in rel_path.lower():
            final_report_sec_id = 'sec-' + RE.sub(r'[^a-zA-Z0-9-]', '-', Path(rel_path).stem).strip('-')
            break

    default_js = ALL_IN_ONE_JS
    if final_report_sec_id:
        default_js = default_js.replace('FINAL-REPORT-SECTION', final_report_sec_id)

    all_in_one = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>深度分析 — 完整报告</title>
<style>
{ALL_IN_ONE_CSS}
</style>
</head>
<body>
<button id="sidebar-toggle">☰ 目录</button>
<nav id="sidebar">
<h2>📚 全部文档</h2>
{' '.join(nav_items)}
</nav>
<div id="main">
{sections_merged}
</div>
<script>
{default_js}
</script>
</body>
</html>"""

    output_path = root / output_name
    output_path.write_text(all_in_one, encoding='utf-8')
    return output_path


if __name__ == '__main__':
    main()
