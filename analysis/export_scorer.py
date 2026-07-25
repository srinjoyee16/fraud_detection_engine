"""
Trains a lightweight logistic-regression claim scorer on the synthetic claims
and exports it to app/model.js so the working web app can score claims in the
browser. Uses the same data generator as simulate.py.

Run:  python analysis/export_scorer.py
"""
import json
from pathlib import Path

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split

from simulate import BANDS, N_CLAIMS, SEED, features, generate_claims

APP = Path(__file__).resolve().parent.parent / "app"


def main():
    rng = np.random.default_rng(SEED)
    df = generate_claims(N_CLAIMS, rng)
    train, test = train_test_split(df, test_size=0.4, random_state=SEED, stratify=df.fraud)
    Xtr, Xte = features(train), features(test)
    mu, sd = Xtr.mean(), Xtr.std().replace(0, 1)
    model = LogisticRegression(max_iter=3000).fit((Xtr - mu) / sd, train.fraud)
    p = model.predict_proba((Xte - mu) / sd)[:, 1]
    auc = roc_auc_score(test.fraud, p)
    cuts = np.percentile(p, BANDS).tolist()
    out = {
        "features": list(Xtr.columns),
        "mean": mu.round(6).tolist(),
        "std": sd.round(6).tolist(),
        "coef": model.coef_[0].round(6).tolist(),
        "intercept": float(model.intercept_[0]),
        "band_cuts": [round(c, 6) for c in cuts],
        "holdout_auc": round(auc, 3),
        "note": "Trained on synthetic data from analysis/simulate.py. Replace with real outcomes before any real use.",
    }
    APP.mkdir(exist_ok=True)
    (APP / "model.js").write_text("window.CLAIM_MODEL = " + json.dumps(out, indent=2) + ";\n")
    print(f"Exported scorer: logistic AUC {auc:.3f}, band cuts {[round(c, 3) for c in cuts]}")


if __name__ == "__main__":
    main()
