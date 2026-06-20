#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from fbe_assembly_lib_v1 import wrapper_main
raise SystemExit(wrapper_main("church-orient-v1"))
