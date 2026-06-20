#!/usr/bin/env bash
# DEPRECATED — caretaker is event-driven (post_dispatch), not timer-based.
echo "SKIP: caretaker uses post_dispatch hook in autorun_dispatcher — no timer watch"
exit 0
