#!/usr/bin/env python3
"""Current codec/version coverage supersedes the former int-only map fixture."""
from pathlib import Path
import runpy
runpy.run_path(str(Path(__file__).with_name("width-check.py")), run_name="__main__")
