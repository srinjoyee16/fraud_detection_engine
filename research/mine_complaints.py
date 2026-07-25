"""
Complaint-mining pipeline for Week 1 discovery.

Input: a CSV you collect (Reddit posts, Play Store reviews, seller forum
threads) with at least a `text` column, plus optional `source` and `url`.
Output (research/output/):
  - labelled.csv: every post with relevance, stakeholder and issue labels
  - summary.csv: counts by stakeholder x issue
  - hand_label_sample.csv: a random sample of relevant posts for you to label
Then, after you fill the `human_issue` column in the sample:
  python research/mine_complaints.py --agreement research/output/hand_label_sample.csv
reports how often your labels agree with the rule labels (Cohen's kappa).

Run:
  python research/mine_complaints.py research/data/posts.csv
"""
import argparse
import re
from pathlib import Path

import pandas as pd

OUT = Path(__file__).parent / "output"

RELEVANT = r"refund|return|replace|damag|broken|wrong item|fake (photo|image|claim)|ai[- ]?(generated|edited)|photoshop|morph|edited (photo|image)"
STAKEHOLDER = {
    "seller": r"\bseller|my store|my shop|restaurant|merchant|our brand|vendor",
    "shopper": r"\bi ordered|my order|i received|customer care|they denied|rejected my|my refund",
}
ISSUE = {
    "fake_photo_fraud": r"fake (photo|image|claim)|ai[- ]?(generated|edited)|photoshop|morph|edited (photo|image)|same photo",
    "honest_claim_denied": r"(refund|return|claim).{0,40}(denied|rejected|declined)|not (approved|accepted)",
    "slow_refund": r"(refund).{0,40}(days|weeks|still|waiting|pending)",
    "pickup_inspection": r"pickup|pick up|delivery (boy|agent|executive).{0,40}(check|inspect|refus)",
    "proof_friction": r"(video|unboxing|another photo|more photos|proof).{0,40}(asked|required|need|demand)",
}


def label(text: str) -> dict:
    t = str(text).lower()
    rel = bool(re.search(RELEVANT, t))
    stake = next((k for k, p in STAKEHOLDER.items() if re.search(p, t)), "unclear")
    issues = [k for k, p in ISSUE.items() if re.search(p, t)]
    return {"relevant": rel, "stakeholder": stake, "issue": issues[0] if issues else "other", "all_issues": ";".join(issues)}


def mine(path: str, sample_n: int = 60, seed: int = 1):
    OUT.mkdir(exist_ok=True)
    df = pd.read_csv(path)
    if "text" not in df.columns:
        raise SystemExit("CSV needs a `text` column")
    df = df.drop_duplicates(subset="text").reset_index(drop=True)
    labels = pd.DataFrame([label(t) for t in df.text])
    out = pd.concat([df, labels], axis=1)
    out.to_csv(OUT / "labelled.csv", index=False)
    rel = out[out.relevant]
    summary = rel.groupby(["stakeholder", "issue"]).size().rename("posts").reset_index().sort_values("posts", ascending=False)
    summary.to_csv(OUT / "summary.csv", index=False)
    sample = rel.sample(min(sample_n, len(rel)), random_state=seed).copy()
    sample["human_issue"] = ""
    sample.to_csv(OUT / "hand_label_sample.csv", index=False)
    print(f"{len(df)} posts after de-duplication, {len(rel)} relevant ({len(rel)/max(len(df),1):.0%})")
    print(summary.to_string(index=False))
    print(f"Hand-label {len(sample)} posts in {OUT/'hand_label_sample.csv'} (fill `human_issue`), then run --agreement")


def agreement(path: str):
    s = pd.read_csv(path).dropna(subset=["human_issue"])
    s = s[s.human_issue.astype(str).str.strip() != ""]
    if s.empty:
        raise SystemExit("No hand labels yet")
    po = (s.issue == s.human_issue).mean()
    cats = set(s.issue) | set(s.human_issue)
    pe = sum((s.issue == c).mean() * (s.human_issue == c).mean() for c in cats)
    kappa = (po - pe) / (1 - pe) if pe < 1 else 1.0
    print(f"{len(s)} hand-labelled posts: raw agreement {po:.0%}, Cohen's kappa {kappa:.2f}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("csv", nargs="?")
    ap.add_argument("--agreement")
    a = ap.parse_args()
    if a.agreement:
        agreement(a.agreement)
    elif a.csv:
        mine(a.csv)
    else:
        ap.print_help()
