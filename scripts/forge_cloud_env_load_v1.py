#!/usr/bin/env python3
"""Load Forge cloud worker URL + secret from disk config and ~/.sourcea-secrets."""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from forge_mvp_lib_v1 import CLOUD_ENV_RECEIPT, now_utc  # noqa: E402

CONFIG = ROOT / "data" / "fbe_cloud_worker_config_v1.json"
SECRETS_DIR = Path.home() / ".sourcea-secrets"


def _load_dotenv(path: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    if not path.is_file():
        return out
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        out[k.strip()] = v.strip().strip('"').strip("'")
    return out


def load_cloud_env(*, apply: bool = False) -> dict:
    cfg: dict = {}
    if CONFIG.is_file():
        cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
    url_env = str(cfg.get("worker_url_env") or "FBE_CLOUD_WORKER_URL")
    secret_env = str(cfg.get("secret_env") or "FBE_INTERNAL_SECRET")
    merged: dict[str, str] = {}
    for env_file in sorted(SECRETS_DIR.glob("*.env")):
        merged.update(_load_dotenv(env_file))
    worker_url = os.environ.get(url_env, "").strip() or merged.get(url_env, "") or str(cfg.get("worker_url") or "").strip()
    secret = os.environ.get(secret_env, "").strip() or merged.get(secret_env, "")
    if apply and worker_url:
        os.environ[url_env] = worker_url.rstrip("/")
    if apply and secret:
        os.environ[secret_env] = secret
    cloud_ready = bool(worker_url)
    receipt = {
        "schema": "forge-cloud-env-receipt-v1",
        "saved_at": now_utc(),
        "cloud_ready": cloud_ready,
        "worker_url_env": url_env,
        "worker_url_set": bool(worker_url),
        "worker_url_host": worker_url.split("//")[-1].split("/")[0] if worker_url else None,
        "secret_set": bool(secret),
        "execution_mode": "CLOUD_ONLY",
        "mac_build_forbidden": True,
        "config_path": str(CONFIG),
    }
    CLOUD_ENV_RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    CLOUD_ENV_RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return receipt


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="Export FBE_CLOUD_WORKER_URL into process env")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = load_cloud_env(apply=args.apply)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(f"cloud_ready={row['cloud_ready']} host={row.get('worker_url_host')}")
    return 0 if row.get("cloud_ready") else 1


if __name__ == "__main__":
    raise SystemExit(main())
