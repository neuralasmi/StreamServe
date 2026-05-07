from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from typing import List
import time, joblib, numpy as np
from datetime import datetime

app = FastAPI(title="StreamServe", version="1.0.0")

MODEL_PATH = "models/model.joblib"
model_data = {"model": None, "version": "v1.0", "loaded_at": None}

class PredictRequest(BaseModel):
    features: List[float]

class BatchRequest(BaseModel):
    features: List[List[float]]

class ModelSwitchRequest(BaseModel):
    version: str
    path: str = "models/"

def load_model():
    try:
        model_data["model"] = joblib.load(MODEL_PATH)
        model_data["loaded_at"] = datetime.now().isoformat()
        model_data["version"] = "v1.0"
    except FileNotFoundError:
        # Train a dummy model if none exists
        from sklearn.datasets import load_iris
        from sklearn.ensemble import RandomForestClassifier
        X, y = load_iris(return_X_y=True)
        model_data["model"] = RandomForestClassifier().fit(X, y)
        model_data["loaded_at"] = datetime.now().isoformat()
        model_data["version"] = "v1.0-init"

load_model()

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "model_version": model_data["version"],
        "loaded_at": model_data["loaded_at"]
    }

@app.get("/model/info")
async def model_info():
    return {
        "name": "StreamServe",
        "version": model_data["version"],
        "loaded_at": model_data["loaded_at"]
    }

@app.post("/predict")
async def predict(req: PredictRequest):
    start = time.time()
    features = np.array(req.features).reshape(1, -1)
    pred = model_data["model"].predict(features)
    latency_ms = (time.time() - start) * 1000
    return {"prediction": int(pred[0]), "latency_ms": round(latency_ms, 2)}

@app.post("/batch_predict")
async def batch_predict(req: BatchRequest, background: BackgroundTasks):
    background.add_task(lambda: None)  # Placeholder for async processing
    features = np.array(req.features)
    start = time.time()
    preds = model_data["model"].predict(features)
    latency_ms = (time.time() - start) * 1000
    return {
        "predictions": [int(p) for p in preds],
        "count": len(preds),
        "latency_ms": round(latency_ms, 2)
    }

@app.post("/model/switch")
async def switch_model(req: ModelSwitchRequest):
    try:
        new_model = joblib.load(f"{req.path}{req.version}.joblib")
        model_data["model"] = new_model
        model_data["version"] = req.version
        model_data["loaded_at"] = datetime.now().isoformat()
        return {"status": "switched", "version": req.version}
    except FileNotFoundError:
        return {"error": "Model file not found"}, 404
