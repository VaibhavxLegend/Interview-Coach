# Project separation: frontend, backend, and ML

This repository is separated into three clear areas:

- Frontend (Next.js): `interview-coach/src` and config at project root
- Backend (FastAPI API): `interview-coach/server/app`
- ML module (model + service): `interview-coach/server/app/ml`

## Frontend

- Client API helpers live in `src/lib/api.ts`.
- A new helper `mlPredict({ text?: string; answer?: string })` calls the backend ML endpoint at `/api/ml/predict`.

## Backend

- FastAPI app defined in `server/app/main.py`.
- Routers in `server/app/routers/*`.
- New ML router `server/app/routers/ml.py` exposes `/api/ml/predict` that calls the ML service.

## ML module

- `server/app/ml/model.py` defines a minimal `SupportsPredict` protocol and a `MockInterviewModel` placeholder.
- `server/app/ml/service.py` provides a thin `MLService` wrapper with lazy model loading and a `predict()` method.

## Local development

- Use Docker Compose to bring up Postgres, Redis, and API:
  - API available at `http://127.0.0.1:8000`.
- Frontend runs via `next dev` (see `interview-coach/README.md`). Set `NEXT_PUBLIC_API_BASE` to the API base URL.

## Example

- Backend: POST `http://127.0.0.1:8000/api/ml/predict` with JSON `{ "text": "Your answer..." }`.
- Frontend: `const { result } = await mlPredict({ text: "Your answer..." });`

Replace the mock model with your actual model by implementing the `SupportsPredict` contract and updating `MLService._load_model()`.
