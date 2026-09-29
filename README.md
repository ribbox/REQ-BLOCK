# REQ-BLOCK – Visual Requirements Builder

Scratch-style block editor for building software requirements by snapping typed pieces together.

## Features

- Block-based requirement assembly (Start → Capability → Object → Purpose/Condition)
- **Any of the following** lists with editable lead-in text
- Reusable piece library (add/remove; pieces return to their original category)
- Multiple pages (add, rename, delete with confirmation)
- Local storage persistence
- Export / Import JSON
- Multi-user **snapshot sync** (no live Blockly co-editing) via self-hosted API
- Docker backend for shared JSON storage (GET/PUT, ETag conflicts, CORS)

## Quick start (local)

Open `requirement_scratch.html` in a modern browser.

## Self-hosted (UI + API)

```bash
docker compose up -d --build
```

- App: http://localhost:8088/
- API: http://localhost:8088/api/

In **Settings**, set **Remote sync URL** to `http://localhost:8088/api/` (or your public URL).

## API only

```bash
cd backend
docker compose up -d --build
```

Remote URL: `http://YOUR_HOST:8090/`

See [backend/README.md](backend/README.md) for environment variables, auth, and production notes.

## Restore point

`requirement_scratch_pre_multiuser_backup.html` is a backup from before multi-user sync was added.

## License

This project is licensed under the **Apache License 2.0**.

[Blockly](https://developers.google.com/blockly) (loaded from CDN in the web UI) is also licensed under the Apache License 2.0. Using Apache-2.0 for this repository matches Blockly’s terms and keeps redistribution straightforward.

You may use, modify, and distribute this software under the Apache-2.0 conditions, including retaining copyright and license notices. See the [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0) for the full text.

**Third-party**

| Component | License |
|-----------|---------|
| [Blockly](https://github.com/google/blockly) | Apache-2.0 |

This project is not affiliated with Google or the Raspberry Pi Foundation.
