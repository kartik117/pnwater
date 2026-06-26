"""Trains the anomaly classifier and writes the artifact + metrics that
the anomaly_detector service loads at runtime.

Run with: python -m pnwater.ml.train
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

import joblib
import xgboost as xgb
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split

from pnwater.ml.dataset import generate_dataset

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parents[3]
MODEL_PATH = REPO_ROOT / "models" / "anomaly_model.joblib"
METRICS_PATH = REPO_ROOT / "models" / "metrics.json"


def main() -> None:
    X, y = generate_dataset()
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    model = xgb.XGBClassifier(
        n_estimators=100, max_depth=4, learning_rate=0.1, eval_metric="logloss", random_state=42
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]
    metrics = {
        "accuracy": round(accuracy_score(y_test, y_pred), 4),
        "precision": round(precision_score(y_test, y_pred), 4),
        "recall": round(recall_score(y_test, y_pred), 4),
        "f1": round(f1_score(y_test, y_pred), 4),
        "roc_auc": round(roc_auc_score(y_test, y_prob), 4),
        "n_train": len(X_train),
        "n_test": len(X_test),
    }

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    METRICS_PATH.write_text(json.dumps(metrics, indent=2) + "\n")

    logger.info("wrote %s", MODEL_PATH)
    logger.info("metrics: %s", json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
