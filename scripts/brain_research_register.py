#!/usr/bin/env python3
"""Shim → brain-os/scripts/brain_research_register.py"""
import runpy
from pathlib import Path
runpy.run_path(str(Path(__file__).resolve().parents[1] / "brain-os/scripts/brain_research_register.py"), run_name="__main__")
