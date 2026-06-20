#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from fbe_assembly_lib_v1 import planned_wrapper_main
raise SystemExit(planned_wrapper_main("church-demo-v1"))
