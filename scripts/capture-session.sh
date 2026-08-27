#!/bin/bash
set -uo pipefail

# Collects the session record at the end of the interview and pushes it to an
# artifact branch on the repo's remote. Run from anywhere inside the repo.
# Every collection step is guarded: a missing source is recorded in the
# artifact, never fatal to the run.

STAMP=$(date -u +%Y%m%d-%H%M%S)
OUT_DIR=$(mktemp -d /tmp/session-capture.XXXXXX)
TARBALL="/tmp/session-artifacts-${STAMP}.tar.gz"
BRANCH="session-artifacts/${STAMP}-${CODESPACE_NAME:-local}"

REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null) || {
    echo "ERROR: run this from inside the repository"
    exit 1
}
cd "$REPO_ROOT"

grab() {
    local label=$1 src=$2
    if [ -e "$src" ]; then
        cp -R "$src" "$OUT_DIR/$label" && echo "collected: $label"
    else
        echo "absent: $label ($src)" | tee -a "$OUT_DIR/ABSENT.txt"
    fi
}

# History is flushed to disk continuously by the image's shell config; this is
# a best-effort extra flush in case the script is sourced from a live shell.
history -a 2>/dev/null || true

grab claude-projects "$HOME/.claude/projects"
grab bash-history "$HOME/.bash_history"
grab zsh-history "$HOME/.zsh_history"
grab workspace-claude-md "$REPO_ROOT/CLAUDE.md"
grab workspace-claude-dir "$REPO_ROOT/.claude"

git log -p > "$OUT_DIR/git-log.txt" 2>&1 || true
git diff HEAD > "$OUT_DIR/git-diff.txt" 2>&1 || true
git status --porcelain > "$OUT_DIR/git-status.txt" 2>&1 || true
python -m pytest > "$OUT_DIR/final-test-output.txt" 2>&1 || true

tar -czf "$TARBALL" -C "$OUT_DIR" .
if [ ! -s "$TARBALL" ]; then
    echo "ERROR: tarball is empty: $TARBALL"
    exit 1
fi
echo "tarball written: $TARBALL ($(du -h "$TARBALL" | cut -f1))"

# Publish via git plumbing: an orphan commit holding only the tarball, pushed to
# a dedicated branch. Never touches the working tree, index, or HEAD.
blob=$(git hash-object -w "$TARBALL")
tree=$(printf '100644 blob %s\tsession-artifacts.tar.gz\n' "$blob" | git mktree)
commit=$(git -c user.name="session-capture" -c user.email="capture@localhost" \
    commit-tree "$tree" -m "session artifacts ${STAMP}")

if git push origin "${commit}:refs/heads/${BRANCH}"; then
    origin_url=$(git remote get-url origin 2>/dev/null || echo "<origin>")
    echo ""
    echo "artifact branch pushed: ${BRANCH}"
    echo "confirm before teardown: open ${origin_url%.git}/tree/${BRANCH}"
    echo "and check session-artifacts.tar.gz is present and non-empty."
else
    echo ""
    echo "ERROR: push failed. Tarball preserved at ${TARBALL}"
    echo "fallback (run on the machine connected to this codespace):"
    echo "  gh codespace cp 'remote:${TARBALL}' ."
    exit 1
fi
