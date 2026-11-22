#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
# Both historical projects use top-level names such as 'observables'.
# Separate Python processes keep their import paths independent.
python -m pytest -q -p no:cacheprovider phase2/tests
python -m pytest -q -p no:cacheprovider phase3/tests
