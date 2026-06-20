#!/usr/bin/env python3
"""WitnessBC film — same ElevenLabs key as SourceA (delegates to shared setup)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from sourcea_elevenlabs_vo_setup_v1 import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())
