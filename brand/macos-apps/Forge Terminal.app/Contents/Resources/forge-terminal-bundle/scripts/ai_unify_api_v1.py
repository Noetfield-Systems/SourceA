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
OPENAI_URL = "https://api.openai.com/v1/chat/completions"
ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
OPENAI_KEY_MISSING_MSG = "OpenAI Key not set in secrets.env"

DEFAULT_MODELS = {
    "gemini_flash_or": "google/gemini-2.5-flash",
    "gemini_flash_direct": "gemini-2.5-flash",
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


def _normalize_openrouter_key(val: str) -> str:
    v = (val or "").strip().strip('"').strip("'")
    # Common vault typo: ysk-or-v1 → sk-or-v1 (duplicate line overwrote good key)
    if v.startswith("ysk-or-"):
        v = v[1:]
    return v


def _parse_env_file(path: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    or_candidates: list[str] = []
    if not path.is_file():
        return out
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        name, _, val = line.partition("=")
        name = name.strip()
        val = _normalize_openrouter_key(val.strip().strip('"').strip("'"))
        if not name or not val:
            continue
        if name == "OPENROUTER_API_KEY":
            or_candidates.append(val)
            continue
        if name in ("OPENROUTER_API_KEY_FORGE", "OPENROUTER_API_KEY_EVAL"):
            out[name] = val
            continue
        out[name] = val
    if or_candidates:
        valid = [c for c in or_candidates if c.startswith("sk-or-v1-")]
        out["OPENROUTER_API_KEY"] = valid[-1] if valid else or_candidates[-1]
    forge = out.get("OPENROUTER_API_KEY_FORGE", "")
    eval_key = out.get("OPENROUTER_API_KEY_EVAL", "")
    primary = out.get("OPENROUTER_API_KEY", "")
    if forge and forge.startswith("sk-or-v1-"):
        out["OPENROUTER_API_KEY"] = forge
    elif primary and primary.startswith("sk-or-v1-"):
        out["OPENROUTER_API_KEY"] = primary
    elif eval_key and eval_key.startswith("sk-or-v1-"):
        out["OPENROUTER_API_KEY"] = eval_key
    if forge and not eval_key:
        out.setdefault("OPENROUTER_API_KEY_EVAL", "")
    if eval_key and not forge:
        out.setdefault("OPENROUTER_API_KEY_FORGE", "")
    return out


def _log_key_fingerprint(label: str, val: str) -> None:
    if val:
        print(f"LOG: Sourcing {label}: {val[:4]}...", flush=True)
    else:
        print(f"LOG: Sourcing {label}: (missing)", flush=True)


def bootstrap_secrets_env(*, force: bool = True, log: bool = False) -> dict[str, str]:
    """Force-load ~/.sina/secrets.env — vault always wins over stale process env."""
    vault = _parse_env_file(SECRETS)
    gemini = vault.get("GEMINI_API_KEY") or vault.get("GOOGLE_API_KEY", "")
    openrouter = vault.get("OPENROUTER_API_KEY", "")
    openrouter_forge = vault.get("OPENROUTER_API_KEY_FORGE", "") or openrouter
    openrouter_eval = vault.get("OPENROUTER_API_KEY_EVAL", "")
    openai = vault.get("OPENAI_API_KEY", "")
    anthropic = vault.get("ANTHROPIC_API_KEY", "")

    if force or gemini:
        if gemini:
            os.environ["GEMINI_API_KEY"] = gemini
            os.environ["GOOGLE_API_KEY"] = gemini
    if force or openrouter:
        if openrouter:
            os.environ["OPENROUTER_API_KEY"] = openrouter
        if openrouter_forge:
            os.environ["OPENROUTER_API_KEY_FORGE"] = openrouter_forge
        if openrouter_eval:
            os.environ["OPENROUTER_API_KEY_EVAL"] = openrouter_eval
    if force or openai:
        if openai:
            os.environ["OPENAI_API_KEY"] = openai
    if force or anthropic:
        if anthropic:
            os.environ["ANTHROPIC_API_KEY"] = anthropic

    for model_key in ("GEMINI_MODEL", "OPENROUTER_MODEL", "OPENAI_MODEL", "ANTHROPIC_MODEL"):
        if vault.get(model_key):
            os.environ[model_key] = vault[model_key]

    keys = {
        "OPENROUTER_API_KEY": os.environ.get("OPENROUTER_API_KEY", "").strip(),
        "OPENROUTER_API_KEY_FORGE": os.environ.get("OPENROUTER_API_KEY_FORGE", "").strip(),
        "OPENROUTER_API_KEY_EVAL": os.environ.get("OPENROUTER_API_KEY_EVAL", "").strip(),
        "OPENAI_API_KEY": os.environ.get("OPENAI_API_KEY", "").strip(),
        "ANTHROPIC_API_KEY": os.environ.get("ANTHROPIC_API_KEY", "").strip(),
        "GEMINI_API_KEY": (
            os.environ.get("GEMINI_API_KEY", "").strip()
            or os.environ.get("GOOGLE_API_KEY", "").strip()
        ),
    }
    if log:
        _log_key_fingerprint("Gemini Key", keys["GEMINI_API_KEY"])
        _log_key_fingerprint("OpenRouter Key", keys["OPENROUTER_API_KEY"])
        _log_key_fingerprint("OpenRouter Forge", keys["OPENROUTER_API_KEY_FORGE"])
        _log_key_fingerprint("OpenRouter Eval", keys["OPENROUTER_API_KEY_EVAL"])
        _log_key_fingerprint("OpenAI Key", keys["OPENAI_API_KEY"])
        _log_key_fingerprint("Anthropic Key", keys["ANTHROPIC_API_KEY"])
    return keys


def load_keys() -> dict[str, str]:
    keys = bootstrap_secrets_env(force=True, log=False)
    if keys["OPENROUTER_API_KEY"] and keys["GEMINI_API_KEY"] and keys["OPENAI_API_KEY"]:
        return keys

    fallback_vaults = [
        Path.home() / ".sourcea-secrets" / "openrouter.env",
        Path.home() / ".sourcea-secrets" / "labs-sandbox.env",
        Path.home() / "Desktop" / "SinaPromptOS" / "secrets.env",
    ]
    for vault_path in fallback_vaults:
        parsed = _parse_env_file(vault_path)
        if not keys["OPENROUTER_API_KEY"]:
            keys["OPENROUTER_API_KEY"] = parsed.get("OPENROUTER_API_KEY", "")
        if not keys["OPENROUTER_API_KEY_FORGE"]:
            keys["OPENROUTER_API_KEY_FORGE"] = parsed.get("OPENROUTER_API_KEY_FORGE", "")
        if not keys["OPENROUTER_API_KEY_EVAL"]:
            keys["OPENROUTER_API_KEY_EVAL"] = parsed.get("OPENROUTER_API_KEY_EVAL", "")
        if not keys["OPENAI_API_KEY"]:
            keys["OPENAI_API_KEY"] = parsed.get("OPENAI_API_KEY", "")
        if not keys.get("ANTHROPIC_API_KEY"):
            keys["ANTHROPIC_API_KEY"] = parsed.get("ANTHROPIC_API_KEY", "")
        if not keys["GEMINI_API_KEY"]:
            keys["GEMINI_API_KEY"] = parsed.get("GEMINI_API_KEY") or parsed.get("GOOGLE_API_KEY", "")

    if keys["GEMINI_API_KEY"]:
        os.environ["GEMINI_API_KEY"] = keys["GEMINI_API_KEY"]
        os.environ["GOOGLE_API_KEY"] = keys["GEMINI_API_KEY"]
    if keys["OPENROUTER_API_KEY"]:
        os.environ["OPENROUTER_API_KEY"] = keys["OPENROUTER_API_KEY"]
    if keys["OPENROUTER_API_KEY_FORGE"]:
        os.environ["OPENROUTER_API_KEY_FORGE"] = keys["OPENROUTER_API_KEY_FORGE"]
    if keys["OPENROUTER_API_KEY_EVAL"]:
        os.environ["OPENROUTER_API_KEY_EVAL"] = keys["OPENROUTER_API_KEY_EVAL"]
    if keys["OPENAI_API_KEY"]:
        os.environ["OPENAI_API_KEY"] = keys["OPENAI_API_KEY"]
    if keys.get("ANTHROPIC_API_KEY"):
        os.environ["ANTHROPIC_API_KEY"] = keys["ANTHROPIC_API_KEY"]
    return keys


def _pick_openrouter_key(keys: dict[str, str], slot: str = "default") -> str:
    slot = (slot or "default").strip().lower()
    forge = keys.get("OPENROUTER_API_KEY_FORGE") or keys.get("OPENROUTER_API_KEY", "")
    eval_key = keys.get("OPENROUTER_API_KEY_EVAL", "")
    if slot in ("forge", "terminal", "ide"):
        return forge
    if slot in ("eval", "quality", "critic"):
        return eval_key or forge
    return forge or eval_key


bootstrap_secrets_env(force=True, log=True)


def _ssl_ctx():
    try:
        import certifi

        return ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        return ssl.create_default_context()


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


def chat_openrouter(
    *,
    system: str,
    user: str,
    model: str | None = None,
    key_slot: str = "default",
) -> tuple[bool, str]:
    keys = load_keys()
    key = _pick_openrouter_key(keys, key_slot)
    if not key:
        return False, "OPENROUTER_API_KEY missing in ~/.sina/secrets.env"
    if not key.startswith("sk-or-v1-"):
        return False, "OPENROUTER_API_KEY invalid format — must start with sk-or-v1- (check ~/.sina/secrets.env for duplicate lines)"
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


def chat_anthropic(*, system: str, user: str, model: str | None = None) -> tuple[bool, str]:
    keys = load_keys()
    key = keys.get("ANTHROPIC_API_KEY", "").strip()
    if not key:
        return False, "ANTHROPIC_API_KEY missing in ~/.sina/secrets.env — see data/forge-secrets-env-template-v1.env"
    model_id = (model or os.environ.get("ANTHROPIC_MODEL") or "claude-sonnet-4-6").strip()
    status, data = _http_post(
        ANTHROPIC_URL,
        {
            "model": model_id,
            "max_tokens": 8192,
            "system": system,
            "messages": [{"role": "user", "content": user}],
        },
        {
            "x-api-key": key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        },
    )
    if status != 200 or not isinstance(data, dict):
        return False, f"anthropic_error:{status}:{data}"
    try:
        parts = data.get("content") or []
        text = "\n".join(p.get("text", "") for p in parts if p.get("type") == "text").strip()
        return (True, text) if text else (False, "anthropic_empty_response")
    except (KeyError, IndexError, TypeError):
        return False, f"anthropic_parse_error:{data}"


def chat_openai(*, system: str, user: str, model: str | None = None) -> tuple[bool, str]:
    keys = load_keys()
    key = keys["OPENAI_API_KEY"]
    if not key:
        return False, OPENAI_KEY_MISSING_MSG
    model_id = (model or os.environ.get("OPENAI_MODEL") or "gpt-4o").strip()
    is_reasoning = model_id.startswith("o1") or model_id.startswith("o3")
    if is_reasoning:
        messages = [{"role": "user", "content": f"{system}\n\n{user}"}]
        body: dict[str, Any] = {"model": model_id, "messages": messages}
    else:
        body = {
            "model": model_id,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": 0.4,
        }
    status, data = _http_post(
        OPENAI_URL,
        body,
        {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        },
    )
    if status != 200 or not isinstance(data, dict):
        return False, f"openai_error:{status}:{data}"
    try:
        return True, data["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError, TypeError):
        return False, f"openai_parse_error:{data}"


def chat_gemini_direct(*, system: str, user: str, model: str | None = None) -> tuple[bool, str]:
    keys = load_keys()
    key = keys["GEMINI_API_KEY"]
    if not key:
        return False, "GEMINI_API_KEY missing in ~/.sina/secrets.env"
    model_id = model or os.environ.get("GEMINI_MODEL") or DEFAULT_MODELS["gemini_flash_direct"]
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
        err = f"gemini_error:{status}:{data}"
        if status in (429, 500, 503, 504) and keys.get("OPENROUTER_API_KEY"):
            or_map = {
                "gemini-2.5-flash-lite": "google/gemini-2.5-flash-lite-preview-06-17",
                "gemini-2.5-flash": "google/gemini-2.5-flash",
                "gemini-2.5-pro": "google/gemini-2.5-pro",
            }
            or_model = or_map.get(model_id, "google/gemini-2.5-flash")
            ok_or, text_or = chat_openrouter(
                system=system,
                user=user,
                model=or_model,
                key_slot="forge",
            )
            if ok_or:
                return True, text_or
        return False, err
    try:
        parts = data["candidates"][0]["content"]["parts"]
        text = "\n".join(p.get("text", "") for p in parts if p.get("text")).strip()
        return (True, text) if text else (False, "gemini_empty_response")
    except (KeyError, IndexError, TypeError):
        return False, f"gemini_parse_error:{data}"


def pick_provider(requested: str = "auto", *, model: str | None = None) -> str:
    keys = load_keys()
    mid = (model or "").strip()
    if mid:
        try:
            import sys as _sys

            _sys.path.insert(0, str(ROOT / "scripts"))
            from model_dispatch import resolve_explicit_model  # noqa: WPS433

            resolved = resolve_explicit_model(mid)
            if resolved.get("explicit"):
                inferred = resolved["provider"]
            else:
                from model_dispatch import infer_provider_for_model  # noqa: WPS433

                inferred = infer_provider_for_model(mid)
            if inferred == "openai":
                return "openai" if keys["OPENAI_API_KEY"] else "none"
            if inferred == "anthropic_direct":
                return "anthropic" if keys.get("ANTHROPIC_API_KEY") else "none"
            if inferred == "openrouter" and keys["OPENROUTER_API_KEY"]:
                return "openrouter"
            if inferred == "gemini_direct" and keys["GEMINI_API_KEY"]:
                return "gemini_direct"
        except Exception:
            if mid.startswith("gpt-") or mid.startswith("openai-") or mid.startswith("o1"):
                return "openai" if keys["OPENAI_API_KEY"] else "none"
            if mid.startswith("claude-"):
                return "anthropic" if keys.get("ANTHROPIC_API_KEY") else "none"
            if "/" in mid and keys["OPENROUTER_API_KEY"]:
                return "openrouter"
            if keys["GEMINI_API_KEY"]:
                return "gemini_direct"
    req = (requested or "auto").strip().lower()
    if req in ("openai", "gpt"):
        return "openai" if keys["OPENAI_API_KEY"] else "none"
    if req in ("anthropic", "claude"):
        return "anthropic" if keys.get("ANTHROPIC_API_KEY") else "none"
    if req in ("openrouter", "or"):
        return "openrouter" if keys["OPENROUTER_API_KEY"] else "none"
    if req in ("gemini", "gemini_direct", "google"):
        if keys["GEMINI_API_KEY"]:
            return "gemini_direct"
        if keys["OPENROUTER_API_KEY"]:
            return "openrouter"
        return "none"
    if keys["GEMINI_API_KEY"]:
        return "gemini_direct"
    if keys["OPENROUTER_API_KEY"]:
        return "openrouter"
    if keys.get("ANTHROPIC_API_KEY"):
        return "anthropic"
    if keys["OPENAI_API_KEY"]:
        return "openai"
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
    explicit_model: bool = False,
) -> dict[str, Any]:
    bootstrap_secrets_env(force=True, log=False)

    import sys as _sys

    _sys.path.insert(0, str(ROOT / "scripts"))
    from model_dispatch import resolve_explicit_model  # noqa: WPS433

    forge_model = (model or "").strip()
    resolved = resolve_explicit_model(forge_model)
    explicit_model = explicit_model or bool(resolved.get("explicit"))
    api_model = resolved.get("api_model") if resolved.get("explicit") else forge_model
    forge_model_id = resolved.get("forge_model_id") or forge_model

    prov = pick_provider(provider, model=forge_model_id or forge_model)
    if prov == "none":
        if resolved.get("provider") == "openai" or forge_model in ("gpt-4o", "openai-o1"):
            return {"ok": False, "error": "openai_key_missing", "message": OPENAI_KEY_MISSING_MSG}
        if resolved.get("provider") == "anthropic_direct":
            return {
                "ok": False,
                "error": "anthropic_key_missing",
                "message": "ANTHROPIC_API_KEY missing in ~/.sina/secrets.env",
            }
        return {"ok": False, "error": "no_api_key", "message": "Set API keys in ~/.sina/secrets.env"}

    def _openrouter_slot() -> str:
        s = (source or "").lower()
        if "eval" in s or "quality" in s or "critic" in s:
            return "eval"
        if "forge" in s or "terminal" in s:
            return "forge"
        return "default"

    def _fn(sys_txt: str, usr_txt: str) -> tuple[bool, str]:
        if prov == "gemini_direct":
            return chat_gemini_direct(system=sys_txt, user=usr_txt, model=api_model or None)
        if prov == "anthropic":
            return chat_anthropic(system=sys_txt, user=usr_txt, model=api_model or None)
        if prov == "openai":
            return chat_openai(system=sys_txt, user=usr_txt, model=api_model or None)
        return chat_openrouter(
            system=sys_txt,
            user=usr_txt,
            model=api_model or None,
            key_slot=_openrouter_slot(),
        )

    if light_gate or explicit_model:
        ok, text = _fn(system, user)
        if not ok and text == OPENAI_KEY_MISSING_MSG:
            return {"ok": False, "error": "openai_key_missing", "message": OPENAI_KEY_MISSING_MSG}
        return {
            "ok": ok,
            "blocked": False,
            "response": text,
            "provider": prov,
            "model": forge_model_id or api_model or DEFAULT_MODELS["gemini_flash_or"],
            "api_model": api_model,
            "gate": {
                "mode": "light" if light_gate else "explicit_lock",
                "reason": "explicit_model_lock" if explicit_model else "api_operational",
                "source": source,
                "bypass_tier_routing": bool(explicit_model),
                "tier_routing": "bypassed" if explicit_model else "default",
            },
        }

    try:
        from model_dispatch import dispatch_chat  # noqa: WPS433

        return dispatch_chat(
            system=system,
            user=user,
            chat_fn=_fn,
            task_id=task_id or f"ai-unify-{uuid.uuid4().hex[:8]}",
            repo_root=str(ROOT),
            source=source,
            model_id=forge_model_id or forge_model,
            explicit_model=explicit_model,
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
        "openrouter_ready": bool(_pick_openrouter_key(keys, "default"))
        and _pick_openrouter_key(keys, "default").startswith("sk-or-v1-"),
        "openrouter_forge_ready": bool(_pick_openrouter_key(keys, "forge"))
        and _pick_openrouter_key(keys, "forge").startswith("sk-or-v1-"),
        "openrouter_eval_ready": bool(_pick_openrouter_key(keys, "eval"))
        and _pick_openrouter_key(keys, "eval").startswith("sk-or-v1-"),
        "openai_ready": bool(keys["OPENAI_API_KEY"]),
        "anthropic_ready": bool(keys.get("ANTHROPIC_API_KEY")),
        "gemini_direct_ready": bool(keys["GEMINI_API_KEY"]),
        "auto_provider": prov,
        "gate_mode": gate_mode,
        "models": DEFAULT_MODELS,
        "endpoints": {
            "openrouter": OPENROUTER_URL,
            "openai": OPENAI_URL,
            "anthropic": ANTHROPIC_URL,
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
