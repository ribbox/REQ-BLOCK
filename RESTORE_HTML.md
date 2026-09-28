# Restore requirement_scratch.html

If `requirement_scratch.html` is missing, wrong, or only says PLACEHOLDER:

```bash
chmod +x restore-html.sh
./restore-html.sh
docker compose up -d --build
```

Latest restore includes:
- Trailing-slash fix for remote API URL (avoids 301 on PUT)
- Confirm modal labels: **Load remote**, Import, Delete page, etc. (not always "Delete")
