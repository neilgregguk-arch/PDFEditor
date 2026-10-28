"""Compatibility entry point for the strict multi-line document reader suite."""
import runpy
from pathlib import Path
runpy.run_path(str(Path(__file__).with_name("verify_wrap.py")),run_name="__main__")
