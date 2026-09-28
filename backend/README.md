# Requirement Scratch – self-hosted backend

Small containerized API that stores one shared **JSON snapshot** for multi-user use.

- **No live Blockly sync** – users Load / Save the full project (pages, requirements, library, workspace snapshot).
- **GET / PUT / POST** on `/`
- **ETag / If-Match** for conflict detection
- **CORS** configurable
- Optional **HTTP Basic Auth**
- Data on a Docker volume

## Quick start (API only)

```bash
cd backend
docker compose up -d --build
```

| Endpoint | Description |
|----------|-------------|
| `GET  http://localhost:8090/` | Load project JSON |
| `PUT  http://localhost:8090/` | Save project JSON |
| `POST http://localhost:8090/` | Same as PUT (fallback) |
| `GET  http://localhost:8090/health` | Health check |

In the web app: **Settings → Remote sync URL** = `http://YOUR_HOST:8090/`

## Full stack (UI + API behind nginx)

From the parent folder (where `requirement_scratch.html` lives):

```bash
docker compose up -d --build
```

- UI:  http://localhost:8088/
- API: http://localhost:8088/api/

Set **Remote sync URL** to `http://localhost:8088/api/` (or your public HTTPS URL + `/api/`).

## Environment variables

| Variable | Default | Meaning |
|----------|---------|--------|
| `PORT` | `8090` | Listen port inside container |
| `DATA_FILE` | `/data/project.json` | Snapshot path inside container |
| `CORS_ORIGIN` | `*` | Allowed browser origin (set to your UI URL in production) |
| `BASIC_AUTH_USER` | _(empty)_ | Enable basic auth if set |
| `BASIC_AUTH_PASSWORD` | _(empty)_ | Password for basic auth |

Example with auth:

```bash
BASIC_AUTH_USER=team BASIC_AUTH_PASSWORD=secret docker compose up -d
```

If you enable basic auth, the browser `fetch` from the HTML app does **not** send credentials yet—use auth at the reverse-proxy (e.g. nginx) or extend the client later.

## Production tips

1. Put **HTTPS** in front (Caddy, Traefik, nginx).
2. Set `CORS_ORIGIN` to the exact UI origin.
3. Back up the Docker volume `requirements_data` (or bind-mount a host path).
4. For SVN/Git history, still use **Export JSON** from the app on a schedule if you want file-based versioning.

## Conflict behaviour

1. Client saves with `If-Match: <etag>` when it has one.
2. If the file changed on the server → **HTTP 412**.
3. User should **Load from remote**, merge manually if needed, then **Save to remote** again.

## Local run without Docker

```bash
mkdir -p /tmp/rs-data
DATA_FILE=/tmp/rs-data/project.json PORT=8090 python3 server.py
```
