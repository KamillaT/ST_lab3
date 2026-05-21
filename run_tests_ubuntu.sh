#!/usr/bin/env bash
set -e

if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi

source .venv/bin/activate

python -m pip install --upgrade pip
pip install -r requirements.txt

echo ""
if command -v firefox >/dev/null 2>&1; then
  echo "Firefox: found"
else
  echo "Firefox: NOT FOUND"
  echo "Install it with: sudo apt install firefox"
fi

if command -v google-chrome >/dev/null 2>&1; then
  echo "Google Chrome: found"
elif command -v chromium >/dev/null 2>&1; then
  echo "Chromium: found"
else
  echo "Chrome/Chromium: NOT FOUND"
  echo "Install Google Chrome or Chromium before running Chrome tests."
fi

echo ""
pytest -v -n 2 --browser chrome --browser firefox
