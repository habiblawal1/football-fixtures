#!/bin/bash
# Absolute path to your project
PROJECT_DIR="/Users/habiblawal/GitHub/football-fixtures"

# Optional: path to your virtualenv python (uncomment if using venv)
VENV_ACTIVATE="/Users/habiblawal/GitHub/football-fixtures/.venv/bin/activate"

cd "$PROJECT_DIR" || exit 1

# If you use a venv, uncomment the next line:
source "$VENV_ACTIVATE"

# Run script with explicit python binary (use full path from `which python3` or `which python`)
/usr/bin/env python3 "$PROJECT_DIR/getFixtures.py" >> "$PROJECT_DIR/launchd.log" 2>> "$PROJECT_DIR/launchd-error.log"