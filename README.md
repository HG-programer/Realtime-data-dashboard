## 🚀 Real-Time Data Dashboard

A full-stack, containerized dashboard that simulates real-time data streaming and visualization.

Built using:
- Flask (Backend API)
- PostgreSQL (Database)
- Docker & Docker Compose (Containerization)
- Chart.js (Data Visualization)

## Architecture

```text
Browser → Flask API → PostgreSQL
	   ↑
	Docker
```

## Tech Stack

- Flask API
- PostgreSQL
- Docker
- Docker Compose
- Chart.js (frontend visualization)

## Run Demo

```bash
docker-compose up --build
```

Open the dashboard at: http://localhost:5000/dashboard

## Deploy on Render

1. Push this repo to GitHub.
2. In Render, create a new **Web Service** from the repo.
3. Use **Docker** as the environment so Render builds from the `Dockerfile`.
4. Add a **PostgreSQL** database in Render.
5. Set these environment variables on the web service:
	- `POSTGRES_HOST` = your Render Postgres hostname
	- `POSTGRES_PORT` = `5432`
	- `POSTGRES_DB` = your Render database name
	- `POSTGRES_USER` = your Render database user
	- `POSTGRES_PASSWORD` = your Render database password
6. Deploy the service and open the generated Render URL.

If you use a Render Postgres private connection string, map the values above from that connection info.

## GitHub Topics

docker flask postgresql backend dashboard realtime

## API Endpoints

- `GET /health`
- `GET /db-test`
- `GET /api/results`
- `POST /api/results`

## 📸 Preview

![Dashboard](./screenshots/dashboard.png)
![Chart](./screenshots/chart.png)
