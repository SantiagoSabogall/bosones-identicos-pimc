#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export TEXINPUTS="$(pwd)/vendor/revtex//:${TEXINPUTS:-}"
export BSTINPUTS="$(pwd)/vendor/revtex//:${BSTINPUTS:-}"
python generar_figuras.py
latexmk -pdf -interaction=nonstopmode -halt-on-error paper.tex
