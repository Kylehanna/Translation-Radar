# Tech Scout Frontend

This Vite app is the public-facing frontend for Translation Radar's RAG-backed tech scouting workflow. It is wired to the FastAPI endpoints exposed by the backend repo:

- `POST /rag/search`
- `GET /rag/coverage`
- `GET /rag/technologies/{technology_id}`

## Environment

Copy `.env.example` to `.env` if you need to point the frontend at a non-default API origin.

- `VITE_RAG_API_BASE_URL`

Behavior:

- Local development defaults to `http://localhost:8000` when the app runs on `localhost` and the variable is unset.
- Production defaults to same-origin requests when the variable is unset, which is appropriate when the frontend is served behind the same host as the FastAPI app or a reverse proxy.

## Local Run

1. Start the Translation Radar FastAPI backend on port `8000`.
2. Install frontend dependencies in this directory.
3. Run the Vite dev server.

Example:

```bash
npm install
npm run dev
```

## Build

```bash
npm run build
```

If you want a stricter pre-deploy check, run:

```bash
npm run lint
npx tsc --noEmit -p tsconfig.app.json --strict
```

## Deploy Notes

- If the frontend and API are deployed on different origins, set `VITE_RAG_API_BASE_URL` to the full backend origin at build time.
- If they are deployed behind the same domain, leave `VITE_RAG_API_BASE_URL` unset and route `/rag/*` to the FastAPI service.
- The current search page expects the seeded backend response shape defined in the Translation Radar API models.
