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
