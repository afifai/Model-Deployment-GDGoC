"""Compare baseline and candidate model metrics."""

import argparse
import json
import os

METRIC_KEYS = [
    ("accuracy", "Accuracy"),
    ("f1_normal", "F1-Score (normal)"),
    ("f1_unknown", "F1-Score (unknown)"),
    ("f1_spam", "F1-Score (spam)"),
]


def compute_delta(baseline_val, candidate_val):
    """Compute delta and indicator between two metric values."""
    if baseline_val is None:
        return {"delta": None, "indicator": "N/A"}
    delta = round(candidate_val - baseline_val, 4)
    indicator = "🟢" if delta >= 0 else "🔴"
    return {"delta": delta, "indicator": indicator}


def compare(baseline_path, candidate_path: str) -> dict:
    """Compare baseline and candidate metrics, output comparison dict."""
    with open(candidate_path) as f:
        candidate = json.load(f)

    baseline = None
    if baseline_path and os.path.exists(baseline_path):
        with open(baseline_path) as f:
            baseline = json.load(f)

    metrics = []
    for key, name in METRIC_KEYS:
        cand_val = candidate.get(key, 0.0)
        base_val = baseline.get(key) if baseline else None
        delta_info = compute_delta(base_val, cand_val)
        metrics.append({
            "name": name,
            "baseline": base_val,
            "candidate": round(cand_val, 4),
            **delta_info,
        })

    return {
        "metrics": metrics,
        "model_type": candidate.get("model_type", "Unknown"),
        "model_params": candidate.get("model_params", {}),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compare model metrics")
    parser.add_argument("--baseline", default=None, help="Path to baseline metrics JSON")
    parser.add_argument("--candidate", required=True, help="Path to candidate metrics JSON")
    args = parser.parse_args()
    result = compare(args.baseline, args.candidate)
    print(json.dumps(result, indent=2, ensure_ascii=False))
