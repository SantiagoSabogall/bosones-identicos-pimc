"""Pytest configuration: make the project's `src/` importable.

The modules under `src/` import each other by top-level name (`import analytic`,
`from params import Params`, ...). Adding `src/` to `sys.path` here lets the
suite run from the repository root without setting PYTHONPATH by hand.
"""

import os
import sys

SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src")
SRC = os.path.abspath(SRC)
if SRC not in sys.path:
    sys.path.insert(0, SRC)
