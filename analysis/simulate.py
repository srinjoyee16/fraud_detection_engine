"""
Proof-of-Claim - refund-claim risk model and resolution-policy simulation.

IMPORTANT: every number this script produces comes from SYNTHETIC data.
Fraud prevalence, AI-image share, detector accuracy and behavioural effects are
assumptions (set at the top of the file), loosely calibrated to public reports.
The value is in comparing policies and seeing which assumptions decide the
answer, not in predicting any real company's numbers.

Run:
    pip install numpy pandas scikit-learn matplotlib
    python analysis/simulate.py
Outputs land in analysis/output/.
"""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split

SEED = 7
N_CLAIMS = 150_000
OUT = Path(__file__).parent / "output"
OUT.mkdir(exist_ok=True)

# ---------------------------------------------------------------------------
# Assumptions (edit and re-run)
# ---------------------------------------------------------------------------
FRAUD_RATE = 0.08            # share of "damaged / wrong item" claims that are false
AI_IMAGE_SHARE = 0.35        # share of false claims that use an AI-edited or recycled photo
DETECTOR_TPR = 0.70          # AI-image detector catches 70% of AI-edited photos...
DETECTOR_FPR = 0.04          # ...but also flags 4% of real photos

COST_MANUAL_REVIEW = 60      # INR, agent time per manual review
COST_DOORSTEP_CHECK = 45     # INR, extra cost of inspecting at pickup vs normal pickup
FRICTION_COST_PER_DAY = 25   # INR-equivalent cost of each day an honest buyer waits for a refund
WRONG_DENIAL_COST = 900      # INR, refund owed + expected lost future margin when an honest claim is denied

LIVE_CAPTURE_DETER_AI = 0.65     # AI-photo fraudsters who give up when only live in-app capture is allowed
LIVE_CAPTURE_DETER_OTHER = 0.15  # other fraudsters who give up at live capture
DOORSTEP_CATCH = 0.85            # share of remaining fraud caught by inspection at pickup
REVIEW_CATCH = 0.60              # share of fraud caught by manual review
REVIEW_WRONG_DENY = 0.03         # share of honest claims wrongly denied by manual review


def generate_claims(n, rng):
    category = rng.choice(["Electronics", "Fashion", "Home", "Grocery/FMCG", "Beauty"], n,
                          p=[0.25, 0.30, 0.20, 0.15, 0.10])
    base = {"Electronics": 6000, "Fashion": 900, "Home": 1500, "Grocery/FMCG": 450, "Beauty": 600}
    value = np.array([rng.lognormal(np.log(base[c]), 0.6) for c in category])
    fraud = rng.random(n) < FRAUD_RATE
    ai_photo = fraud & (rng.random(n) < AI_IMAGE_SHARE)

    # Buyer signals (fraudsters skew toward more past claims and newer accounts)
    account_age_m = np.where(fraud, rng.gamma(2.6, 9, n), rng.gamma(3, 10, n))
    past_orders = rng.poisson(np.where(fraud, 11, 14), n)
    past_claims = rng.binomial(past_orders, np.where(fraud, 0.08, 0.04))
    hours_to_claim = np.where(fraud, rng.gamma(2, 17, n), rng.gamma(2, 14, n))
    sku_defect_rate = np.clip(rng.normal(np.where(fraud, 0.04, 0.05), 0.025), 0.001, 0.2)  # real defects make honest claims likelier
    open_box_delivery = rng.random(n) < 0.25
    # Photo signals
    exif_missing = np.where(ai_photo, rng.random(n) < 0.60, rng.random(n) < 0.25)
    detector_flag = np.where(ai_photo, rng.random(n) < DETECTOR_TPR, rng.random(n) < DETECTOR_FPR)
    near_duplicate_img = np.where(ai_photo, rng.random(n) < 0.25, rng.random(n) < 0.005)

    return pd.DataFrame({
        "category": category, "value": value.round(0), "fraud": fraud.astype(int), "ai_photo": ai_photo.astype(int),
        "account_age_m": account_age_m.round(1), "past_orders": past_orders, "past_claims": past_claims,
        "hours_to_claim": hours_to_claim.round(1), "sku_defect_rate": sku_defect_rate.round(4),
        "open_box_delivery": open_box_delivery.astype(int), "exif_missing": exif_missing.astype(int),
        "detector_flag": detector_flag.astype(int), "near_duplicate_img": near_duplicate_img.astype(int),
    })


def features(df):
    X = pd.get_dummies(df[["category"]], drop_first=True).astype(float)
    X["log_value"] = np.log(df.value)
    for c in ["account_age_m", "past_orders", "hours_to_claim", "sku_defect_rate",
              "open_box_delivery", "exif_missing", "detector_flag", "near_duplicate_img"]:
        X[c] = df[c]
    X["past_claim_rate"] = df.past_claims / df.past_orders.clip(lower=1)
    return X


BANDS = (55, 85, 97)  # percentiles: low < p55 <= medium < p85 <= high < p97 <= very high


def evaluate(df, policy, score, deter_ai=LIVE_CAPTURE_DETER_AI):
    n = len(df)
    fraud = df.fraud.to_numpy().astype(bool)
    ai = df.ai_photo.to_numpy().astype(bool)
    value = df.value.to_numpy()
    honest = ~fraud

    fraud_paid = np.zeros(n)     # INR refunded on false claims
    ops = np.zeros(n)            # review / inspection cost
    wait_days = np.zeros(n)      # refund delay for honest buyers
    wrong_deny = np.zeros(n)     # probability an honest claim is denied

    def instant(m):
        fraud_paid[m] += fraud[m] * value[m]
        wait_days[m] += 0.1

    def live_capture(m):
        # returns probability a fraudulent claim continues past live capture
        return np.where(ai[m], 1 - deter_ai, 1 - LIVE_CAPTURE_DETER_OTHER)

    if policy == "Refund on photo (baseline)":
        instant(np.ones(n, bool))
    elif policy == "AI detector gate":
        flag = df.detector_flag.to_numpy().astype(bool)
        instant(~flag)
        m = flag  # flagged -> manual review
        ops[m] += COST_MANUAL_REVIEW
        fraud_paid[m] += fraud[m] * (1 - REVIEW_CATCH) * value[m]
        wait_days[m] += 2
        wrong_deny[m] += honest[m] * REVIEW_WRONG_DENY
    elif policy == "Inspect every pickup":
        m = np.ones(n, bool)
        ops[m] += COST_DOORSTEP_CHECK
        fraud_paid[m] += fraud[m] * (1 - DOORSTEP_CATCH) * value[m]
        wait_days[m] += 4
    elif policy.startswith("Proof-of-Claim"):
        cuts = np.percentile(score, BANDS)
        band = np.digitize(score, cuts)
        # Low: instant refund
        instant(band == 0)
        # Medium: live in-app capture, refund on pickup scan
        m = band == 1
        cont = live_capture(m)
        fraud_paid[m] += fraud[m] * cont * value[m]
        wait_days[m] += 1
        # High: live capture + doorstep inspection before refund
        m = band == 2
        cont = live_capture(m)
        ops[m] += COST_DOORSTEP_CHECK
        fraud_paid[m] += fraud[m] * cont * (1 - DOORSTEP_CATCH) * value[m]
        wait_days[m] += 4
        # Very high: live capture + manual review + inspection
        m = band == 3
        cont = live_capture(m)
        ops[m] += COST_MANUAL_REVIEW + COST_DOORSTEP_CHECK
        fraud_paid[m] += fraud[m] * cont * (1 - DOORSTEP_CATCH) * (1 - REVIEW_CATCH) * value[m]
        wait_days[m] += 5
        wrong_deny[m] += honest[m] * REVIEW_WRONG_DENY
    else:
        raise ValueError(policy)

    friction = honest * wait_days * FRICTION_COST_PER_DAY + wrong_deny * WRONG_DENIAL_COST
    total = fraud_paid + ops + friction
    hon = honest.sum()
    return {
        "policy": policy,
        "fraud_loss_per_claim_inr": fraud_paid.sum() / n,
        "fraud_loss_vs_exposure_%": 100 * fraud_paid.sum() / (fraud * value).sum(),
        "ops_cost_per_claim_inr": ops.sum() / n,
        "honest_avg_wait_days": (wait_days * honest).sum() / hon,
        "honest_instant_refund_%": 100 * ((wait_days <= 0.1) & honest).sum() / hon,
        "honest_wrongly_denied_per_10k": 1e4 * (wrong_deny * honest).sum() / hon,
        "total_cost_per_claim_inr": total.sum() / n,
    }


def main():
    rng = np.random.default_rng(SEED)
    df = generate_claims(N_CLAIMS, rng)
    print(f"Synthetic claims: {N_CLAIMS:,}  fraud rate {df.fraud.mean():.1%}  AI-photo share of fraud {df.ai_photo.sum()/df.fraud.sum():.0%}")

    train, test = train_test_split(df, test_size=0.4, random_state=SEED, stratify=df.fraud)
    model = HistGradientBoostingClassifier(max_iter=300, learning_rate=0.08, random_state=SEED)
    model.fit(features(train), train.fraud)
    score = model.predict_proba(features(test))[:, 1]
    auc = roc_auc_score(test.fraud, score)

    order = np.argsort(-score)
    caught = np.cumsum(test.fraud.to_numpy()[order]) / test.fraud.sum()
    cap15 = caught[int(0.15 * len(order)) - 1]
    cap45 = caught[int(0.45 * len(order)) - 1]
    det_only_auc = roc_auc_score(test.fraud, test.detector_flag)
    print(f"Risk model holdout AUC {auc:.3f} (AI detector alone: {det_only_auc:.3f})")
    print(f"Riskiest 15% of claims hold {cap15:.0%} of fraud; riskiest 45% hold {cap45:.0%}")

    policies = ["Refund on photo (baseline)", "AI detector gate", "Inspect every pickup", "Proof-of-Claim (tiered)"]
    res = pd.DataFrame([evaluate(test, p, score) for p in policies]).round(2)
    print(res.to_string(index=False))
    res.to_csv(OUT / "policy_comparison.csv", index=False)

    sens = []
    for d in [0.0, 0.2, 0.4, 0.65, 0.8]:
        r = evaluate(test, "Proof-of-Claim (tiered)", score, deter_ai=d)
        sens.append({"live_capture_deters_ai_fraud": d, "fraud_loss_per_claim_inr": r["fraud_loss_per_claim_inr"],
                     "total_cost_per_claim_inr": r["total_cost_per_claim_inr"]})
    sens = pd.DataFrame(sens).round(2)
    print(sens.to_string(index=False))
    sens.to_csv(OUT / "sensitivity_live_capture.csv", index=False)

    with open(OUT / "model_summary.txt", "w") as f:
        f.write(f"Synthetic claims: {N_CLAIMS}\nFraud rate: {df.fraud.mean():.4f}\n")
        f.write(f"Holdout AUC (gradient boosting): {auc:.3f}\nAUC of AI detector flag alone: {det_only_auc:.3f}\n")
        f.write(f"Top 15% capture: {cap15:.3f}\nTop 45% capture: {cap45:.3f}\n")

    fig, ax = plt.subplots(1, 2, figsize=(14, 5))
    x = np.arange(len(order)) / len(order) * 100
    ax[0].plot(x, caught * 100, color="#2563eb", lw=2, label=f"Risk model (AUC {auc:.2f})")
    ax[0].plot([0, 100], [0, 100], color="#9ca3af", ls="--", label="Random")
    ax[0].set_xlabel("% of claims routed to extra checks (riskiest first)")
    ax[0].set_ylabel("% of false claims captured")
    ax[0].set_title("Fraud capture curve (synthetic)")
    ax[0].legend(frameon=False); ax[0].grid(alpha=0.3)
    cols = ["#9ca3af", "#f59e0b", "#ef4444", "#2563eb"]
    parts = res.set_index("policy")
    friction = parts.total_cost_per_claim_inr - parts.fraud_loss_per_claim_inr - parts.ops_cost_per_claim_inr
    ax[1].barh(parts.index, parts.fraud_loss_per_claim_inr, color="#ef4444", label="Fraud loss")
    ax[1].barh(parts.index, parts.ops_cost_per_claim_inr, left=parts.fraud_loss_per_claim_inr, color="#f59e0b", label="Ops cost")
    ax[1].barh(parts.index, friction, left=parts.fraud_loss_per_claim_inr + parts.ops_cost_per_claim_inr, color="#60a5fa", label="Honest-buyer friction")
    ax[1].invert_yaxis(); ax[1].legend(frameon=False, loc="lower right")
    ax[1].set_xlabel("Total cost per claim (INR)"); ax[1].set_title("Policy cost breakdown (synthetic)")
    ax[1].grid(axis="x", alpha=0.3)
    for i, v in enumerate(parts.total_cost_per_claim_inr):
        ax[1].text(v, i, f"  {v:.0f}", va="center")
    ax[1].set_xlim(0, parts.total_cost_per_claim_inr.max() * 1.15)
    fig.tight_layout(); fig.savefig(OUT / "results.png", dpi=150)


if __name__ == "__main__":
    main()
