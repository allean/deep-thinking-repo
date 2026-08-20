#!/usr/bin/env bash
# check_env.sh — verify the runtime environment for the deep-thinking skill.
# Checks: python3 (>= 3.8), required stdlib modules, skill file integrity.
# Exit code 0 = all checks pass; 1 = one or more failures.

set -u

PASS=0; FAIL=0
ok()   { printf "  \033[32m✓\033[0m %s\n" "$1"; PASS=$((PASS+1)); }
bad()  { printf "  \033[31m✗\033[0m %s\n" "$1"; FAIL=$((FAIL+1)); }
info() { printf "  \033[90m%s\033[0m\n" "$1"; }

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "==> Python runtime"
if command -v python3 >/dev/null 2>&1; then
    PY_VER="$(python3 -c 'import sys; print("%d.%d.%d" % sys.version_info[:3])')"
    if python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)'; then
        ok "python3 $PY_VER (>= 3.8 required)"
    else
        bad "python3 $PY_VER is too old — >= 3.8 required"
    fi
else
    bad "python3 not found in PATH"
fi

echo "==> Python stdlib modules (used by assets/*.py)"
if command -v python3 >/dev/null 2>&1; then
    for mod in re html sys os datetime pathlib; do
        if python3 -c "import $mod" >/dev/null 2>&1; then
            ok "import $mod"
        else
            bad "import $mod failed"
        fi
    done
    info "No third-party packages are required — stdlib only."
fi

echo "==> Skill files (repo integrity)"
for f in SKILL.md \
         references/phase-0-and-0.5.md \
         references/phase-1-decomposition.md \
         references/phase-2-execution.md \
         references/phase-3-tracking-evolver.md \
         assets/generate_html.py \
         assets/template.html \
         assets/convert_all_md.py; do
    if [ -f "$REPO_ROOT/$f" ]; then
        ok "$f"
    else
        bad "$f missing"
    fi
done

echo "==> Skill frontmatter"
if head -5 "$REPO_ROOT/SKILL.md" 2>/dev/null | grep -q "^name: deep-thinking"; then
    ok "SKILL.md has valid 'name: deep-thinking' frontmatter"
else
    bad "SKILL.md frontmatter missing or invalid"
fi

echo "==> HTML converter smoke test"
if command -v python3 >/dev/null 2>&1 && [ -f "$REPO_ROOT/assets/generate_html.py" ]; then
    TMP_MD="$(mktemp /tmp/deep-thinking-smoke-XXXXXX.md)"
    printf '# Smoke Test\n\n## Dashboard\n\n### Dashboard\n\n| Metric | Value |\n|---|---|\n| a | 1 |\n\n[FACT] test [JUDGMENT] test\n' > "$TMP_MD"
    if python3 "$REPO_ROOT/assets/generate_html.py" "$TMP_MD" >/dev/null 2>&1; then
        ok "generate_html.py converted a sample markdown file"
    else
        bad "generate_html.py failed on a sample markdown file"
    fi
    rm -f "$TMP_MD" "${TMP_MD%.md}"-final-report.html
else
    bad "skipped (python3 or generate_html.py unavailable)"
fi

echo
if [ "$FAIL" -eq 0 ]; then
    printf "\033[32mAll checks passed (%d).\033[0m\n" "$PASS"
    exit 0
else
    printf "\033[31m%d check(s) failed, %d passed.\033[0m\n" "$FAIL" "$PASS"
    exit 1
fi
