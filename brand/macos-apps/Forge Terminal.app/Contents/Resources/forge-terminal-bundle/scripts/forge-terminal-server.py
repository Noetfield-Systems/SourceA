#!/usr/bin/env python3
"""Forge Terminal server entry — delegates to full Connect server (Chat Unify machines + Forge IDE)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from forge_terminal_connect_server_v1 import main

if __name__ == "__main__":
    main()
