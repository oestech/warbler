#!/bin/bash
set -uo pipefail

# Runs once per codespace (postCreateCommand): per-instance state scrub and a
# logging-only self-check. Must never block codespace creation - always exits 0.

LOG="$HOME/environment-selfcheck.log"
PINNED_CLAUDE_VERSION="2.1.246"

note() { echo "$1" | tee -a "$LOG"; }
: > "$LOG"
note "self-check $(date -u +%Y-%m-%dT%H:%M:%SZ)"

# Fresh state per candidate: no inherited session history or agent config.
rm -rf "$HOME/.claude" "$HOME/.claude.json" 2>/dev/null
if [ -d "$HOME/.claude/projects" ]; then
    note "FAIL: stale ~/.claude/projects still present after scrub"
else
    note "ok: no inherited agent state"
fi

v=$(claude --version 2>/dev/null | head -1) || v="MISSING"
case "$v" in
    *"$PINNED_CLAUDE_VERSION"*) note "ok: claude version $v" ;;
    *) note "FAIL: claude version '$v' does not match pinned $PINNED_CLAUDE_VERSION" ;;
esac

if [ -n "${ANTHROPIC_API_KEY:-}${CLAUDE_CODE_OAUTH_TOKEN:-}" ]; then
    note "ok: auth env var present"
else
    note "FAIL: no auth env var (ANTHROPIC_API_KEY / CLAUDE_CODE_OAUTH_TOKEN)"
fi

if [ -n "${GOOGLE_API_KEY:-}${GEMINI_API_KEY:-}" ]; then
    note "ok: GOOGLE_API_KEY present"
else
    note "FAIL: GOOGLE_API_KEY unset (the app's query parser needs it)"
fi

if jq -e . /etc/claude-code/managed-settings.json >/dev/null 2>&1; then
    note "ok: managed settings valid JSON"
else
    note "FAIL: managed settings missing or unparseable"
fi

if python -m pytest --version >/dev/null 2>&1; then
    note "ok: pytest available"
else
    note "FAIL: pytest not installed"
fi

note "self-check complete (log: $LOG)"
exit 0
