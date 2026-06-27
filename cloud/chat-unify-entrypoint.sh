#!/usr/bin/env sh
set -eu
export CHAT_UNIFY_CLOUD=1
export CHAT_UNIFY_STANDALONE=1
export CHAT_UNIFY_STATE_DIR="${CHAT_UNIFY_STATE_DIR:-/data/chat-unify}"
export SINA_SOURCE_A="${SINA_SOURCE_A:-/app}"
export HOME="${HOME:-/root}"
mkdir -p "${CHAT_UNIFY_STATE_DIR}/extracts" "${CHAT_UNIFY_STATE_DIR}/receipts" "${HOME}/.sina/chat-unify/extracts" "${HOME}/.sina/chat-unify/receipts"
ln -sfn "${CHAT_UNIFY_STATE_DIR}" "${HOME}/.sina/chat-unify" 2>/dev/null || true
exec python3 /app/scripts/chat-unify-server.py
