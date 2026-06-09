# sqwash-pdf status

## Completed

- [x] Shared flatten library (`lib/flatten.py`)
- [x] CLI refactor to use shared library
- [x] FastAPI backend with `/health` and `POST /api/flatten`
- [x] Static web UI with upload, DPI/quality controls, and download
- [x] Render and Vercel deployment config
- [x] Unit tests for bytes API, CLI output, and FastAPI routes
- [x] Workspace docs (`context.md`, `.incoming/`)

## Next steps

- [ ] Deploy API to Render and note the live `onrender.com` URL
- [ ] Update `web/vercel.json` rewrite destination to the Render URL
- [ ] Deploy `web/` to Vercel with project root set to `web`
- [ ] Smoke test upload/download on production
- [ ] Optional: set `ALLOWED_ORIGINS` on Render for Vercel preview domains
