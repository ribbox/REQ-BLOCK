# Agent instructions — REQ-BLOCK

Guidance for AI agents (and humans) working on this repository.

**Keep this file current** when behaviour, UI, deploy, or layout changes. Prefer updating `AGENTS.md` in the same change as the code it describes.

## What this project is

Visual, Scratch-style **requirements builder** (Blockly blocks with typed connections). Users assemble requirements from reusable pieces, manage multiple pages, persist in the browser, and sync a full project **snapshot** to a self-hosted API.

There is **no live co-editing** of the Blockly workspace — only Load / Sync of the whole JSON snapshot.

- **UI:** single-file `requirement_scratch.html` (HTML + CSS + JS; Blockly from CDN)
- **API:** Python stdlib HTTP server (`backend/server.py`) — one JSON file, ETag / If-Match
- **License:** Apache-2.0 (aligned with Blockly)

## Repository layout

| Path | Role |
|------|------|
| `requirement_scratch.html` | Full web app (Docker mounts as nginx `index.html`) |
| `requirement_scratch_pre_multiuser_backup.html` | Snapshot from before multi-user sync |
| `docker-compose.yml` | Full stack: `api` + `web` (nginx) on host **8088** |
| `backend/server.py` | GET/PUT/POST `/`, GET `/health` |
| `backend/nginx.conf` | SPA + `/api` proxy; no absolute redirects |
| `backend/Dockerfile` | API image |
| `backend/docker-compose.yml` | API-only on host **8090** |
| `AGENTS.md` | This file |
| `README.md` | User-facing quick start + license |

Do **not** reintroduce recovery artifacts (`restore-html.sh`, `*.gz.b64`, `*.part0`, `patches/`) unless explicitly requested.

## Ports

| Mode | Host port | Notes |
|------|-----------|--------|
| Full stack | **8088** | Only published host port; API listens internally on **8090** |
| API only | **8090** | `backend/docker-compose.yml` |

Do **not** bind host **8080** (often used by other containers on this host).

Docker service name for the API: **`api`**. nginx uses Docker DNS (`127.0.0.11`) and a variable `proxy_pass` so `api` is resolved at **request** time (avoids nginx crash if `api` is not ready at startup). `web` waits for `api` **healthcheck** (`GET /health`).

## Header toolbar (icon-only)

| Icon | Action |
|------|--------|
| ℹ️ | Info panel (toolbar table + piece colour key) |
| 💾 | Save current requirement text to **this page’s list** |
| ☁️ | **Sync to server** (PUT full snapshot) — not in Settings |
| 📚 | Add selected block to reusable library (same category) |
| 🗑️ | Clear blocks on this page |
| ⚙️ | Settings (remote URL, load from remote, import/export, clear local) |

- Header title is only **🧩** (favicon matches). Tab title: “Requirement Builder”.
- There is **no** “Generate Requirement” button — the sentence updates **live** as blocks connect.
- Settings still has **Load from remote**; save/sync is the header **☁️** only.

## Confirm modals

`showConfirmModal(title, message, options)`:

- `confirmLabel` — primary button text (default `OK`)
- `danger: true` — red styling for destructive actions

| Dialog | Confirm label |
|--------|----------------|
| Remote update available | **Load remote** |
| Import | Import |
| Delete page / clear data / remove library item | destructive label + `danger: true` |

Never hardcode the confirm button as “Delete” for non-delete actions.

## Multi-user / remote sync

- Snapshot only: full `pages`, library, workspace state, metadata.
- Client `getRemoteUrl()` must **keep a trailing slash** on the API URL.
- PUT uses `If-Match` when an ETag is known; **412** → load remote, then sync again.
- Optional poll in Settings can show “Remote update available”.

### Path-prefix deploy (e.g. Caddy)

Example public base: `https://example.com/req-block/`

1. Caddy: `handle_path /req-block/*` → `host:8088` (one upstream for full stack).
2. App **Remote sync URL** must include prefix **and** trailing slash, e.g. `https://example.com/req-block/api/`.
3. nginx: `absolute_redirect off`; proxy `/api` and `/api/` with **no** `return 301` to absolute `/api/` (that drops the prefix and breaks PUT).
4. Prefer **308** over **301** if the reverse proxy normalizes trailing slashes (preserves PUT).

## Local storage

Browser `localStorage`: pages, saved requirements, workspace, piece library, settings (including remote URL). “Clear local data” should not wipe remote URL settings unless intended.

## When editing the HTML app

- Prefer small, targeted edits; file is ~63KB.
- After Docker volume deploy: hard-refresh (`Ctrl+Shift+R`).
- Network tab: successful sync is **200** on `PUT …/api/`, not **301**.
- Large single-file pushes via some agent channels are fragile — prefer the user’s local `git push` for `requirement_scratch.html` when possible.

## Backend

- PUT body: JSON object with a `pages` array.
- Health: `GET /health` → `{"status":"ok"}`.
- Optional basic auth via env vars (see `backend/README.md`).

## License

Apache-2.0 (see `README.md`). Blockly is Apache-2.0; do not add dependencies with incompatible licenses without updating the README.

## Do not

- Bind host port **8080** for this stack.
- Emit absolute nginx redirects behind a path prefix.
- Strip trailing slashes from the remote API URL in client code.
- Assume live multi-user block editing.
- Leave confirm buttons labelled “Delete” for load/import/sync flows.
- Re-add recovery/placeholder HTML or split-upload scripts without a clear need.
