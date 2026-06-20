#!/usr/bin/env python3
"""SEMEJ — provider registry (AI chat URLs + DOM hints)."""
from __future__ import annotations

import json
from pathlib import Path

CONFIG_PATH = Path.home() / ".sina" / "semej-providers.json"
DEFAULT_CHAIN = ["gemini", "chatgpt", "perplexity", "grok", "claude"]

DEFAULT_PROVIDERS = {
    "schema": 1,
    "chrome_debug_port": 9222,
    "wait_response_sec": 90,
    "poll_interval_sec": 4,
    "chain_default": DEFAULT_CHAIN,
    "providers": [
        {
            "id": "gemini",
            "name": "Gemini",
            "url": "https://gemini.google.com/",
            "input_selectors": [
                "div[contenteditable='true']",
                "rich-textarea textarea",
                "textarea",
            ],
            "submit_keys": "Enter",
            "response_selectors": [
                "message-content",
                ".model-response-text",
                "[data-message-author='model']",
            ],
        },
        {
            "id": "chatgpt",
            "name": "ChatGPT",
            "url": "https://chatgpt.com/",
            "input_selectors": [
                "#prompt-textarea",
                "textarea[data-id='root']",
                "div[contenteditable='true']",
                "textarea",
            ],
            "submit_keys": "Enter",
            "response_selectors": [
                "[data-message-author-role='assistant']",
                ".markdown",
                "article[data-turn='assistant']",
            ],
        },
        {
            "id": "perplexity",
            "name": "Perplexity",
            "url": "https://www.perplexity.ai/",
            "input_selectors": [
                "textarea",
                "div[contenteditable='true']",
                "[placeholder*='Ask']",
            ],
            "submit_keys": "Enter",
            "response_selectors": [
                ".prose",
                "[class*='answer']",
                "main div[class*='markdown']",
            ],
        },
        {
            "id": "grok",
            "name": "Grok",
            "url": "https://grok.com/",
            "input_selectors": ["textarea", "div[contenteditable='true']"],
            "submit_keys": "Enter",
            "response_selectors": [
                "[class*='message']",
                ".markdown",
                "article",
            ],
        },
        {
            "id": "claude",
            "name": "Claude",
            "url": "https://claude.ai/new",
            "input_selectors": [
                "div[contenteditable='true']",
                "fieldset textarea",
                "textarea",
            ],
            "submit_keys": "Enter",
            "response_selectors": [
                "[data-is-streaming='false']",
                ".font-claude-message",
                "[class*='assistant']",
            ],
        },
        {
            "id": "copilot",
            "name": "Microsoft Copilot",
            "url": "https://copilot.microsoft.com/",
            "input_selectors": ["textarea", "#userInput"],
            "submit_keys": "Enter",
            "response_selectors": [".ac-textBlock", "[class*='response']"],
        },
        {
            "id": "poe",
            "name": "Poe",
            "url": "https://poe.com/",
            "input_selectors": ["textarea", "[class*='GrowingTextArea']"],
            "submit_keys": "Enter",
            "response_selectors": ["[class*='Message']", ".markdown"],
        },
    ],
}


def load_config() -> dict:
    if not CONFIG_PATH.is_file():
        save_config(DEFAULT_PROVIDERS)
        return json.loads(json.dumps(DEFAULT_PROVIDERS))
    data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    for p in DEFAULT_PROVIDERS["providers"]:
        if not any(x.get("id") == p["id"] for x in data.get("providers") or []):
            data.setdefault("providers", []).append(p)
    data.setdefault("chain_default", DEFAULT_CHAIN)
    data.setdefault("chrome_debug_port", 9222)
    return data


def save_config(data: dict) -> None:
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")


def provider_by_id(pid: str) -> dict | None:
    for p in load_config().get("providers") or []:
        if p.get("id") == pid:
            return p
    return None


def chain_ids(custom: list[str] | None = None) -> list[str]:
    cfg = load_config()
    chain = custom or cfg.get("chain_default") or DEFAULT_CHAIN
    known = {p["id"] for p in cfg.get("providers") or []}
    return [x for x in chain if x in known]


def providers_payload() -> dict:
    cfg = load_config()
    return {
        "providers": cfg.get("providers") or [],
        "chain_default": cfg.get("chain_default") or DEFAULT_CHAIN,
        "chrome_debug_port": cfg.get("chrome_debug_port", 9222),
        "config_path": str(CONFIG_PATH),
    }
