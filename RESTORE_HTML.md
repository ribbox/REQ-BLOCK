# Restore requirement_scratch.html

If `requirement_scratch.html` is missing or wrong (e.g. only says PLACEHOLDER):

```bash
chmod +x restore-html.sh
./restore-html.sh
```

Then restart the web container:

```bash
docker compose up -d --build
```

This build includes the fix: remote API URL always keeps a trailing slash so browsers do not get a 301 on PUT (which caused Failed to fetch).
