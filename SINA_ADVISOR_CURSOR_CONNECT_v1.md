# Connect Cursor as Advisor in Sina Command

Three ways — pick one in **Agent loop → Advisor provider**.

---

## 1) OpenRouter API (default)

- Add to `~/.sina/secrets.env`:
  ```
  OPENROUTER_API_KEY=sk-or-...
  ```
- Advisor runs in the app only (Gemini/etc.) — **not** a Cursor window.

---

## 2) Cursor Cloud Agent (best “real Cursor” in app)

Uses **Cursor’s API** + Python SDK — a cloud/local Cursor agent, separate from your coding chat.

1. [Cursor Dashboard → Integrations → User API Keys](https://cursor.com/dashboard/integrations)
2. Add to `~/.sina/secrets.env`:
   ```
   CURSOR_API_KEY=cursor_...
   ```
3. Install SDK (once):
   ```bash
   pip3 install cursor-sdk
   ```
4. Restart Sina Command server (reopen Desktop app).
5. In app: **Agent loop** → provider chip **Cursor Cloud**.

---

## 3) Cursor IDE bridge (Advisor chat in Cursor)

Uses **this IDE** as Advisor — message injects into Cursor; Advisor replies via script.

1. In app: select provider **Cursor IDE**.
2. Create a **new Cursor chat** named “Sina Advisor”.
3. Attach rule: `@sina-advisor` (file: `SourceA/.cursor/rules/sina-advisor.mdc`).
4. Send from app → message appears in Cursor → Advisor answers → runs:
   ```bash
   ~/Desktop/SourceA/scripts/advisor-cursor-reply.sh "advisor answer"
   ```
5. App shows the reply in Advisor chat.

---

## Roles reminder

| Role | Where |
|------|--------|
| **Executor** | Main coding chat — builds |
| **Advisor** | OpenRouter / Cursor Cloud / Cursor IDE Advisor chat |
| **Planner** | OpenRouter after each executor answer (loop) |

---

*API: `POST /api/advisor/chat` with `{"action":"set_provider","provider":"cursor_cloud"}` etc.*
