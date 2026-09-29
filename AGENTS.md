# Agent instructions — REQ-BLOCK

Guidance for AI agents (and humans) working on this repository.

## What this project is

Visual, Scratch-style **requirements builder** (Blockly blocks with typed connections). Users assemble requirements from reusable pieces, manage multiple pages, persist locally, and sync a full project snapshot to a self-hosted API (no live co-editing of the Blockly workspace).

Primary UI: single-file `requirement_scratch.html` (HTML + CSS + JS, Blockly from CDN).

Backend: small Python stdlib HTTP server (`backend/server.py`) storing one JSON snapshot with ETag / If-Match conflict detection.

## Layout

| Path | Role |
|------|------|
| `requirement_scratch.html` | Full web app (mount as nginx `index.html` in full stack) |
| `docker-compose.yml` | Full stack: API + nginx UI on host **8088** |
| `backend/` | API image, API-only compose (host **8090**), nginx conf |
| `backend/server.py` | GET/PUT/POST `/`, GET `/health` |
| `patches/` | Small documented fixes (e.g. confirm modal labels) |
| `restore-html.sh` | Rebuild HTML from compressed payload if needed |

Do **not** bind host port **8080** (often taken by other stacks on this user’s hosts).

## Ports (intentional)

| Mode | Host port | Notes |
|------|-----------|--------|
| Full stack UI + API | **8088** | Only published host port; API internal on **8090** |
| API only | **8090** | `backend/docker-compose.yml` |

Inside Docker network: service name `api`, listen **8090**. nginx proxies `/api/` → `http://api:8090/`.

## Path-prefix deploy (Caddy)

Typical public URL: `https://example.com/req-block/`

Caddy should use **`handle_path /req-block/*`** → `host:8088` so the container still sees `/` and `/api/`.

**Critical:**

1. **Remote sync URL** in the app must be the public path including prefix and trailing slash, e.g.  
   `https://example.com/req-block/api/`
2. Client code must **keep a trailing slash** on the remote URL. Stripping `/api/` → `/api` causes **301** redirects; browsers fail **PUT** with “Failed to fetch”.
3. nginx must **not** emit absolute redirects to `/api/` (drops the `/req-block` prefix). Use `absolute_redirect off` and proxy both `/api` and `/api/` without `return 301`.
4. Prefer Caddy **308** (not 301) if normalizing trailing slashes so PUT is preserved.
5. Full stack needs **one** Caddy upstream (**8088**). Do not map the API container separately when using root `docker-compose.yml`.

## Multi-user model

- **Snapshot sync only** (Load / Save full JSON). No live Blockly collaboration.
- Conflict: client sends `If-Match: <etag>`; server returns **412** if stale → user loads remote, then saves again.
- Optional poll interval in Settings can prompt “Remote update available” → confirm button must be **Load remote**, not Delete.

## Confirm modals

`showConfirmModal(title, message, options)`:

- `options.confirmLabel` — button text (default `OK`)
- `options.danger` — red styling for destructive actions

Remote update → `{ confirmLabel: 'Load remote' }`.  
Deletes/clears → `{ confirmLabel: '…', danger: true }`.

## Local storage keys

Browser localStorage holds pages, library, workspace state, and settings (including remote URL). Clearing local data should not wipe remote URL unless intended.

## When editing the HTML app

- Prefer small, targeted edits; the file is large (~60KB).
- After deploy behind Docker volume mount, hard-refresh browsers (`Ctrl+Shift+R`).
- Verify remote save in DevTools Network: expect **200** on `PUT …/api/`, not **301**.

## Backend validation

PUT body must be JSON object with a `pages` array. Health: `GET /health` → `{"status":"ok"}`.

## Do not

- Publish host **8080** for this stack.
- Rely on absolute nginx redirects behind a path prefix.
- Strip trailing slashes from the remote API URL in client code.
- Assume simultaneous live block editing; design is snapshot-based.
