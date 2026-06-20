#!/usr/bin/env python3
"""Unified AI API — OpenRouter + Gemini + Chat Unify bridge.

Single choke point for live model calls. Routes through model_dispatch gate.
Receipt: ~/.sina/ai-unify-api-v1.json
"""
from __future__ import annotations

import argparse
import json
import os
import ssl
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib import error as urlerror
from urllib import request as urlrequest

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
RECEIPT_PATH = SINA / "ai-unify-api-v1.json"
SECRETS = SINA / "secrets.env"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

DEFAULT_MODELS = {
    "gemini_flash_or": "google/gemini-2.5-flash",
    "gemini_flash_direct": "gemini-2.0-flash",
    "gemini_pro_or": "google/gemini-2.5-pro",
}

POLISH_SYSTEM = """You polish unified chat briefs for a founder OS team.
Output: clean markdown brief with Summary, Decisions, Open threads, Contradictions to resolve.
Be concise. No filler. Preserve factual claims from the input."""


CRITIQUE_SYSTEM = """You are a governance critic for SourceA disk law.
Review the brief for: stale SSOT claims, fake-green (PASS without receipt), authority drift, contradictions.
Output: verdict PASS/ESCALATE/BLOCK + bullet findings + one founder line."""


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_keys() -> dict[str, str]:
    keys = {"OPENROUTER_API_KEY": "", "GEMINI_API_KEY": ""}
    vault_paths = [
        SINA / "secrets.env",
        Path.home() / ".sourcea-secrets" / "openrouter.env",
        Path.home() / ".sourcea-secrets" / "labs-sandbox.env",
        Path.home() / "Desktop" / "SinaPromptOS" / "secrets.env",
    ]
    for vault in vault_paths:
        if not vault.is_file():
            continue
        for line in vault.read_text(encoding="utf-8", errors="replace").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            name, _, val = line.partition("=")
            name = name.strip()
            val = val.strip().strip('"').strip("'")
            if name in keys and val and not keys[name]:
                keys[name] = val
    return keys


def _ssl_ctx():
    import certifi

    return ssl.create_default_context(cafile=certifi.where())


def _http_post(url: str, body: dict, headers: dict, *, timeout: int = 120) -> tuple[int, dict | str]:
    data = json.dumps(body).encode("utf-8")
    req = urlrequest.Request(url, data=data, headers=headers, method="POST")
    try:
        with urlrequest.urlopen(req, timeout=timeout, context=_ssl_ctx()) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urlerror.HTTPError as exc:
        try:
            payload = json.loads(exc.read().decode("utf-8"))
        except (OSError, json.JSONDecodeError):
            payload = exc.read().decode("utf-8", errors="replace")
        return exc.code, payload
    except (urlerror.URLError, TimeoutError, OSError) as exc:
        return 0, str(exc)


def chat_openrouter(*, system: str, user: str, model: str | None = None) -> tuple[bool, str]:
    keys = load_keys()
    key = keys["OPENROUTER_API_KEY"]
    if not key:
        return False, "OPENROUTER_API_KEY missing in ~/.sina/secrets.env"
    model_id = model or os.environ.get("OPENROUTER_MODEL", DEFAULT_MODELS["gemini_flash_or"])
    status, data = _http_post(
        OPENROUTER_URL,
        {
            "model": model_id,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": 0.4,
        },
        {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://local.chat-unify",
            "X-Title": "AiUnifyApi",
        },
    )
    if status != 200 or not isinstance(data, dict):
        return False, f"openrouter_error:{status}:{data}"
    try:
        return True, data["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError, TypeError):
        return False, f"openrouter_parse_error:{data}"


def chat_gemini_direct(*, system: str, user: str, model: str | None = None) -> tuple[bool, str]:
    keys = load_keys()
    key = keys["GEMINI_API_KEY"]
    if not key:
        return False, "GEMINI_API_KEY missing in ~/.sina/secrets.env"
    model_id = model or DEFAULT_MODELS["gemini_flash_direct"]
    url = GEMINI_URL.format(model=model_id) + f"?key={key}"
    status, data = _http_post(
        url,
        {
            "systemInstruction": {"parts": [{"text": system}]},
            "contents": [{"role": "user", "parts": [{"text": user}]}],
            "generationConfig": {"temperature": 0.4},
        },
        {"Content-Type": "application/json"},
    )
    if status != 200 or not isinstance(data, dict):
        return False, f"gemini_error:{status}:{data}"
    try:
        parts = data["candidates"][0]["content"]["parts"]
        text = "\n".join(p.get("text", "") for p in parts if p.get("text")).strip()
        return (True, text) if text else (False, "gemini_empty_response")
    except (KeyError, IndexError, TypeError):
        return False, f"gemini_parse_error:{data}"


def pick_provider(requested: str = "auto") -> str:
    keys = load_keys()
    req = (requested or "auto").strip().lower()
    if req in ("openrouter", "or"):
        return "openrouter" if keys["OPENROUTER_API_KEY"] else "none"
    if req in ("gemini", "gemini_direct", "google"):
        if keys["GEMINI_API_KEY"]:
            return "gemini_direct"
        if keys["OPENROUTER_API_KEY"]:
            return "openrouter"
        return "none"
    if keys["OPENROUTER_API_KEY"]:
        return "openrouter"
    if keys["GEMINI_API_KEY"]:
        return "gemini_direct"
    return "none"


def dispatch_raw(
    *,
    system: str,
    user: str,
    provider: str = "auto",
    model: str | None = None,
    task_id: str = "",
    source: str = "ai-unify-api",
    light_gate: bool = False,
) -> dict[str, Any]:
    prov = pick_provider(provider)
    if prov == "none":
        return {"ok": False, "error": "no_api_key", "message": "Set OPENROUTER_API_KEY or GEMINI_API_KEY in ~/.sina/secrets.env"}

    def _fn(sys_txt: str, usr_txt: str) -> tuple[bool, str]:
        if prov == "gemini_direct":
            return chat_gemini_direct(system=sys_txt, user=usr_txt, model=model)
        return chat_openrouter(system=sys_txt, user=usr_txt, model=model)

    if light_gate:
        ok, text = _fn(system, user)
        return {
            "ok": ok,
            "blocked": False,
            "response": text,
            "provider": prov,
            "model": model or DEFAULT_MODELS["gemini_flash_or"],
            "gate": {"mode": "light", "reason": "api_operational", "source": source},
        }

    try:
        import sys as _sys

        _sys.path.insert(0, str(ROOT / "scripts"))
        from model_dispatch import dispatch_chat  # noqa: WPS433

        return dispatch_chat(
            system=system,
            user=user,
            chat_fn=_fn,
            task_id=task_id or f"ai-unify-{uuid.uuid4().hex[:8]}",
            repo_root=str(ROOT),
            source=source,
        )
    except Exception:
        ok, text = _fn(system, user)
        return {"ok": ok, "blocked": False, "response": text, "provider": prov, "gate": {"mode": "bypass"}}


def status_payload() -> dict[str, Any]:
    keys = load_keys()
    prov = pick_provider("auto")
    gate_mode = "shadow"
    try:
        import sys as _sys

        _sys.path.insert(0, str(ROOT / "scripts"))
        from model_dispatch import current_gate_mode  # noqa: WPS433

        gate_mode = current_gate_mode()
    except Exception:
        pass
    return {
        "schema": "ai-unify-api-v1",
        "at": _now(),
        "openrouter_ready": bool(keys["OPENROUTER_API_KEY"]),
        "gemini_direct_ready": bool(keys["GEMINI_API_KEY"]),
        "auto_provider": prov,
        "gate_mode": gate_mode,
        "models": DEFAULT_MODELS,
        "endpoints": {
            "openrouter": OPENROUTER_URL,
            "gemini": "generativelanguage.googleapis.com",
            "chat_unify": f"http://127.0.0.1:{os.environ.get('CHAT_UNIFY_PORT', '13023')}/api/chat-unify",
            "n8n_integration": f"http://127.0.0.1:{os.environ.get('N8N_INTEGRATION_PORT', '13026')}/api/n8n-integration",
        },
    }


def polish_brief(text: str, *, provider: str = "auto", model: str | None = None) -> dict[str, Any]:
    if not (text or "").strip():
        return {"ok": False, "error": "empty_brief"}
    result = dispatch_raw(
        system=POLISH_SYSTEM,
        user=text[:48000],
        provider=provider,
        model=model,
        source="chat-unify-polish",
        light_gate=True,
    )
    if not result.get("ok"):
        return result
    polished = result.get("response") or ""
    out_path = SINA / "chat-unify" / "exports" / f"polished-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.md"
    try:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(polished + "\n", encoding="utf-8")
        result["export_path"] = str(out_path)
    except OSError:
        pass
    result["action"] = "polish_brief"
    _write_receipt(result)
    return result


def critique_brief(text: str, *, provider: str = "auto", model: str | None = None) -> dict[str, Any]:
    if not (text or "").strip():
        return {"ok": False, "error": "empty_brief"}
    result = dispatch_raw(
        system=CRITIQUE_SYSTEM,
        user=text[:48000],
        provider=provider,
        model=model,
        source="chat-unify-critique",
        light_gate=True,
    )
    result["action"] = "critique_brief"
    _write_receipt(result)
    return result


def _write_receipt(row: dict[str, Any]) -> None:
    receipt = {
        "schema": "ai-unify-api-v1",
        "at": _now(),
        "ok": bool(row.get("ok")),
        "action": row.get("action"),
        "provider": row.get("provider") or pick_provider("auto"),
        "blocked": bool(row.get("blocked")),
        "gate_mode": (row.get("gate") or {}).get("mode"),
        "export_path": row.get("export_path"),
        "chars_out": len(row.get("response") or ""),
    }
    try:
        RECEIPT_PATH.parent.mkdir(parents=True, exist_ok=True)
        RECEIPT_PATH.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    except OSError:
        pass


def handle_action(body: dict | None = None) -> dict[str, Any]:
    body = body or {}
    action = (body.get("action") or "status").strip().lower()
    if action in ("status", "report"):
        row = status_payload()
        row["ok"] = True
        return row
    if action == "chat":
        user = body.get("user") or body.get("text") or body.get("prompt") or ""
        if not user.strip():
            return {"ok": False, "error": "empty_prompt"}
        system = body.get("system") or "You are a helpful assistant for SourceA founder operations."
        result = dispatch_raw(
            system=system,
            user=user,
            provider=body.get("provider") or "auto",
            model=body.get("model"),
            task_id=body.get("task_id") or "",
            source=body.get("source") or "ai-unify-chat",
            light_gate=bool(body.get("light_gate", True)),
        )
        result["action"] = "chat"
        _write_receipt(result)
        return result
    if action == "polish_brief":
        return polish_brief(body.get("text") or body.get("brief") or "", provider=body.get("provider") or "auto", model=body.get("model"))
    if action == "critique_brief":
        return critique_brief(body.get("text") or body.get("brief") or "", provider=body.get("provider") or "auto", model=body.get("model"))
    return {"ok": False, "error": f"unknown_action:{action}"}


def main() -> int:
    ap = argparse.ArgumentParser(description="AI Unify API — OpenRouter + Gemini")
    ap.add_argument("--action", default="status", choices=["status", "chat", "polish_brief", "critique_brief"])
    ap.add_argument("--text", default="")
    ap.add_argument("--provider", default="auto")
    ap.add_argument("--model", default="")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    if args.action == "status":
        row = status_payload()
        row["ok"] = True
    elif args.action == "chat":
        row = handle_action({"action": "chat", "user": args.text, "provider": args.provider, "model": args.model or None})
    elif args.action == "polish_brief":
        row = polish_brief(args.text, provider=args.provider, model=args.model or None)
    else:
        row = critique_brief(args.text, provider=args.provider, model=args.model or None)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(f"AI_UNIFY ok={row.get('ok')} action={args.action}")
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
