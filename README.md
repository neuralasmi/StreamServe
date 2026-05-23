# StreamServe — Production ML Serving Infrastructure

![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104%2B-red)
![Docker](https://img.shields.io/badge/Docker-Multi--stage%20Build-blue)
![Kubernetes](https://img.shields.io/badge/Kubernetes-HPA--Ready-purple)
![scikit-learn](https://img.shields.io/badge/scikit--learn-1.3%2B-orange)

Production-grade ML model serving with FastAPI, Docker, Kubernetes HPA-ready configs, model versioning, and comprehensive health checks.

## What It Does
- FastAPI REST API: `GET /health`, `GET /model/info`, `POST /predict`, `POST /batch_predict`
- Model versioning: load/swap models without downtime via `/model/switch` endpoint
- Async prediction pipeline with background tasks
- Health check endpoint for Kubernetes readiness/liveness probes
- Docker: multi-stage build, python:3.11-slim, <200MB image
- Kubernetes manifests: Deployment, Service, HorizontalPodAutoscaler
- Batch inference support for offline scoring jobs

## API Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Readiness + liveness probe |
| `/model/info` | GET | Loaded model name, version, input shape |
| `/predict` | POST | Single prediction with latency log |
| `/batch_predict` | POST | Batch predictions up to 1000 items |
| `/model/switch` | POST | Hot-swap model version |

## Quick Start
```bash
git clone https://github.com/neuralasmi/StreamServe
cd StreamServe
docker build -t streamserve:latest .
docker run -p 8000:8000 streamserve:latest
curl http://localhost:8000/health
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"features":[5.1,3.5,1.4,0.2]}'
```

## Kubernetes
```bash
kubectl apply -f k8s/
kubectl autoscale deployment streamserve --cpu-percent=70 --min=2 --max=10
```