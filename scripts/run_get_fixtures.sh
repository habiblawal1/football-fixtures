#!/bin/bash
# Wrapper to run getFixtures.py reliably from launchd
# - cds to project dir
# - uses .venv if present
# - logs debug info to launchd.log and launchd-error.log

PROJECT_DIR="/Users/habiblawal/GitHub/football-fixtures"
VENV_PY="$PROJECT_DIR/.venv/bin/python"
LOG_OUT="$PROJECT_DIR/launchd.log"
LOG_ERR="$PROJECT_DIR/launchd-error.log"

cd "$PROJECT_DIR" || exit 1

# Ensure logs exist and are writable
mkdir -p "$(dirname "$LOG_OUT")"
: >> "$LOG_OUT"
: >> "$LOG_ERR"

# Group multiple commands in the current shell so all standard output and errors
# from this block are redirected together (stdout → $LOG_OUT, stderr → $LOG_ERR).
# Using { ... } ensures shared environment and single redirection for the group.
{
  echo "=== wrapper start ==="
  echo "date: $(date -u '+%Y-%m-%d %H:%M:%SZ')"
  echo "cwd: $(pwd)"
  echo "which python3: $(which python3 2>/dev/null || true)"
  echo "python from env: $(/usr/bin/env python3 -c 'import sys; print(sys.executable)' 2>/dev/null || true)"
  if [ -x "$VENV_PY" ]; then
    echo "using venv python: $VENV_PY"
    "$VENV_PY" "$PROJECT_DIR/getFixtures.py"
  else
    /usr/bin/env python3 "$PROJECT_DIR/getFixtures.py"
  fi
  echo "=== wrapper end ==="
} >> "$LOG_OUT" 2>> "$LOG_ERR"