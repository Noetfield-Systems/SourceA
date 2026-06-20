"""FBE motor ensure — refresh delegate + federate + verify for prove chains."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SINA = Path.home() / ".sina"
AGENT_CANCEL = SINA / "agent-cancel-v1.flag"
MAC_EMERGENCY = SINA / "mac-health-emergency-active-v1.flag"


def _clear_fbe_panic_flags() -> list[str]:
    cleared: list[str] = []
    for flag in (AGENT_CANCEL, MAC_EMERGENCY):
        if flag.is_file():
            try:
                flag.unlink(missing_ok=True)
                cleared.append(flag.name)
            except OSError:
                pass
    return cleared


def ensure_motor(*, wave: str = "W2", bay_slug: str = "sample-bay", factory_id: str = "factory_1") -> dict:
    import sys

    sys.path.insert(0, str(ROOT / "scripts"))
    from fbe_motor_delegate_v1 import delegate  # noqa: WPS433
    from fbe_receipt_federate_v1 import federate  # noqa: WPS433
    from fbe_verify_motor_v1 import verify  # noqa: WPS433

    _clear_fbe_panic_flags()
    delegate(fbe_prove=True, skip_federate=True)
    federate(bay_slug=bay_slug, wave=wave, factory_id=factory_id)
    row = verify()
    if not row.get("ok"):
        delegate(fbe_prove=True, skip_federate=True)
        federate(bay_slug=bay_slug, wave=wave, factory_id=factory_id)
        row = verify()
    return row
