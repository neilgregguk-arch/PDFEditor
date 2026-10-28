"""Phase 4C.2 handover entry point; does not touch previous phases."""
import runpy
from pathlib import Path
runpy.run_path(str(Path(__file__).with_name("write_phase4c2_handover.py")), run_name="__main__")
