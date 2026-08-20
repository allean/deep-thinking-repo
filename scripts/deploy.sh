#!/usr/bin/env bash
# deploy.sh — install the deep-thinking skill for Claude Code and/or Kimi CLI.
#
# Usage:
#   ./scripts/deploy.sh                    # deploy to all detected targets
#   ./scripts/deploy.sh --target claude    # Claude Code only  (~/.claude/skills/deep-thinking)
#   ./scripts/deploy.sh --target kimi      # Kimi CLI only    (~/.config/agents/skills/deep-thinking)
#   ./scripts/deploy.sh --target all       # both (default)
#   ./scripts/deploy.sh --dir /custom/path # deploy to a custom directory
#   ./scripts/deploy.sh --dry-run          # show what would happen, change nothing
#   ./scripts/deploy.sh --no-backup        # do not back up an existing installation
#
# An existing installation is backed up to <target>.backup-<timestamp> before
# being replaced, unless --no-backup is given.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

TARGET="all"
CUSTOM_DIR=""
DRY_RUN=0
BACKUP=1

usage() { sed -n '2,13p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'; exit "${1:-0}"; }

while [ $# -gt 0 ]; do
    case "$1" in
        --target)    TARGET="${2:?--target needs a value}"; shift 2 ;;
        --target=*)  TARGET="${1#*=}"; shift ;;
        --dir)       CUSTOM_DIR="${2:?--dir needs a value}"; shift 2 ;;
        --dir=*)     CUSTOM_DIR="${1#*=}"; shift ;;
        --dry-run)   DRY_RUN=1; shift ;;
        --no-backup) BACKUP=0; shift ;;
        -h|--help)   usage 0 ;;
        *) echo "Unknown argument: $1" >&2; usage 1 ;;
    esac
done

case "$TARGET" in
    claude|kimi|all) ;;
    *) echo "Error: --target must be claude, kimi or all (got: $TARGET)" >&2; exit 1 ;;
esac

run() {
    if [ "$DRY_RUN" -eq 1 ]; then
        echo "  [dry-run] $*"
    else
        "$@"
    fi
}

deploy_to() {
    local dest="$1"
    local label="$2"

    echo "==> Deploying to $label: $dest"

    if [ -e "$dest" ] && [ "$BACKUP" -eq 1 ]; then
        local backup="${dest}.backup-$(date +%Y%m%d-%H%M%S)"
        run cp -R "$dest" "$backup"
        echo "  backed up existing installation -> $backup"
    fi

    run mkdir -p "$dest/references" "$dest/assets"
    run cp "$REPO_ROOT/SKILL.md" "$dest/SKILL.md"
    run cp "$REPO_ROOT"/references/*.md "$dest/references/"
    run cp "$REPO_ROOT"/assets/generate_html.py "$REPO_ROOT"/assets/template.html "$REPO_ROOT"/assets/convert_all_md.py "$dest/assets/"

    echo "  installed: SKILL.md + $(ls "$REPO_ROOT"/references/*.md | wc -l | tr -d ' ') references + 3 assets"
}

# Preflight: environment must be sane before we install anything.
echo "==> Preflight environment check"
if [ "$DRY_RUN" -eq 1 ]; then
    echo "  [dry-run] would run scripts/check_env.sh"
else
    "$REPO_ROOT/scripts/check_env.sh" || {
        echo "Environment check failed — aborting deploy." >&2
        exit 1
    }
fi
echo

if [ -n "$CUSTOM_DIR" ]; then
    deploy_to "$CUSTOM_DIR" "custom directory"
else
    if [ "$TARGET" = "claude" ] || [ "$TARGET" = "all" ]; then
        deploy_to "$HOME/.claude/skills/deep-thinking" "Claude Code"
    fi
    if [ "$TARGET" = "kimi" ] || [ "$TARGET" = "all" ]; then
        deploy_to "$HOME/.config/agents/skills/deep-thinking" "Kimi CLI"
    fi
fi

echo
echo "Done. Restart your agent session (or start a new one) to pick up the skill."
echo "Trigger it with: 深度解析 <topic>  ·  deep thinking <topic>  ·  /deep <topic>"
