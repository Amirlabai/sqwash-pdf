# sqwash-pdf status

## Completed

- [x] Shared flatten library (`lib/flatten.py`)
- [x] CLI refactor to use shared library
- [x] FastAPI backend with `/health` and `POST /api/flatten`
- [x] Static web UI with upload, DPI/quality controls, and download
- [x] Render-only hosting (UI + API on one service)
- [x] Unit tests for bytes API, CLI output, and FastAPI routes
- [x] Workspace docs (`context.md`, `.incoming/`)

## Next steps

- [ ] Deploy to Render and confirm https://sqwash-pdf.onrender.com serves UI + API
- [ ] Smoke test upload/download on production
- [ ] Delete or disable the old Vercel project if it still exists
