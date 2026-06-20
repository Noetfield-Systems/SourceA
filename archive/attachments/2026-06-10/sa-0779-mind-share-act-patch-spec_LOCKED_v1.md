# sa-0779 ACT — Mind Share UI patch spec (SinaaiDataBase apply)

**Saved:** 2026-06-10T12:00:00Z · **Retrofit:** doc-datetime-law batch retrofit
**Worker:** SourceA · CHECK PASS · 4 gaps · **hub edit lock** — apply in `agent-control-panel/assets/app.js`

## Gap 1 — Show `lane` on feed cards (~7124)

In `mindFeed` map, add lane to topic line:

```javascript
<p class="sc-mind-share-topic">#${esc(m.topic || "general")} · lane: ${esc(m.lane || "—")} · stance: ${esc(m.stance_hint || "neutral")}</p>
```

## Gap 2 — Client min-20 guard (~7408 submit handler)

Before `councilRoomApi({ action: "share_mind", ...})`:

```javascript
if ((body || "").trim().length < 20) {
  toast("Write at least 20 characters", "error");
  return;
}
```

## Gap 3 — Loading/disabled on submit

In submit handler: disable submit button + `toast("Sharing…")` until response; re-enable in finally.

## Gap 4 — Private agent page mind shares (~8941 Governance card)

After governance card, if `w.mind_shares?.length`:

```javascript
${card("Your Mind Share posts", `
  <p class="sc-list-meta">Latest advisory posts from this agent · <button type="button" class="sc-btn sc-btn-sm sc-btn-gold sc-goto-tab" data-tab="council-room">Council Room →</button></p>
  <ul class="sc-list">${(w.mind_shares || []).slice(0,5).map(m => `<li><strong>${esc(m.kind)}</strong> #${esc(m.topic)} — ${esc((m.body||"").slice(0,120))}</li>`).join("")}</ul>
`)}
```

Ensure `loop_workspaces` payload includes `mind_shares` from council room API (already in `agent_council_room.py` agents_out).

## Verify after apply

Council Room feed shows lane; short body rejected client-side; submit shows loading; workspace page lists own shares.
