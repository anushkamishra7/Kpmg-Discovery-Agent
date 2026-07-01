# Deploying to Render

This app is a FastAPI backend that also serves the prebuilt React frontend
(`frontend/dist`, available at `/ui`). It uses a local CLIP model (torch +
transformers) plus Pinecone and AEM. Because of torch/CLIP it needs **~2 GB RAM**,
so the free/starter tiers will run out of memory — use the **Standard** plan.

## 1. Push the repo to GitHub

Render deploys from a Git repo. From the project folder:

```bash
git add requirements.txt Dockerfile .dockerignore render.yaml .env.example DEPLOY.md
git commit -m "Add Render deployment config"
git push
```

Make sure `.env` is NOT pushed (it's already in `.gitignore`).

## 2. Create the service on Render

Two options:

**A. Blueprint (uses render.yaml — recommended)**
1. Go to https://dashboard.render.com → New → Blueprint.
2. Connect the GitHub repo. Render reads `render.yaml` and creates the web service.
3. It will prompt for the env vars marked `sync: false` — paste the values from
   your local `.env`.

**B. Manual**
1. New → Web Service → connect the repo.
2. Runtime: **Docker** (Render auto-detects the Dockerfile).
3. Plan: **Standard**. Health check path: `/health`.
4. Add all env vars from `.env.example` under the Environment tab.

## 3. Environment variables

Set every key listed in `.env.example` with the real values from your local `.env`.
At minimum the app needs the `PINECONE_*` and `AEM_*` values for search to return
results. The server will still boot without them, but queries will fail.

## 4. First deploy

The Docker build downloads the CLIP model (~600 MB) at build time and bakes it
into the image, so the build takes several minutes but cold starts are fast.
When it's live, check:

- `https://<your-app>.onrender.com/health` → `{"status":"ok"}`
- `https://<your-app>.onrender.com/ui` → the search UI

## AEM reachability (important)

If `AEM_BASE_URL` points at a **KPMG-internal** host (not public internet),
Render's servers will not be able to reach it, and image loading / crawling
will fail even though search UI loads. Options:

- Use a publicly reachable AEM endpoint, or
- Put a proxy/tunnel between Render and AEM, or
- Host inside KPMG's own cloud/VPN instead of Render (the same Dockerfile works
  on Azure Container Apps, AWS App Runner/ECS, etc.).

## Notes

- `aem_queue.db` (SQLite) and any local Postgres are for the offline indexing
  pipeline (`scripts/`, `agents/`), not the web request path. Render's disk is
  ephemeral — don't rely on writing files at runtime. Run indexing jobs
  separately and store vectors in Pinecone.
- To run the same image locally:
  `docker build -t kpmg-agent . && docker run -p 8000:8000 --env-file .env kpmg-agent`
  then open http://localhost:8000/ui
