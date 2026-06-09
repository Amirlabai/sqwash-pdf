# sqwash-pdf status

## Completed

- [x] Shared flatten library (`lib/flatten.py`)
- [x] CLI refactor to use shared library
- [x] FastAPI backend with `/health` and `POST /api/flatten`
- [x] Static web UI with upload, DPI/quality controls, and download
- [x] Render and Vercel deployment config
- [x] Vercel `API_URL` env var with build-time `vercel.json` generation
- [x] Unit tests for bytes API, CLI output, and FastAPI routes
- [x] Workspace docs (`context.md`, `.incoming/`)

## Next steps

- [ ] Deploy API to Render and note the live `onrender.com` URL
- [ ] Set `API_URL` on Vercel to the Render URL
- [ ] Set `VERCEL_APP_URL` on Render to the Vercel production URL
- [ ] Deploy `web/` to Vercel (root `web`, build `npm run build`)
- [ ] Smoke test upload/download on production
