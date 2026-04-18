"""Generate markdown PR report for model evaluation."""

import argparse
import base64
import json
import os

import joblib
import pandas as pd
from sklearn.model_selection import train_test_split

LABEL_MAP = {0: "normal", 1: "spam", 2: "promo"}


def run_sanity_check(model_path: str, dataset_path: str, n_samples: int = 5):
    """Run sanity check predictions on sample data."""
    model = joblib.load(model_path)
    df = pd.read_csv(dataset_path)
    X = df["Teks"].astype(str)
    y = df["label"]

    _, X_test, _, y_test = train_test_split(X, y, test_size=0.25, random_state=42)

    samples = list(zip(X_test.values[:n_samples], y_test.values[:n_samples]))
    results = []
    for text, expected_label in samples:
        pred = int(model.predict([text])[0])
        expected_name = LABEL_MAP.get(expected_label, str(expected_label))
        predicted_name = LABEL_MAP.get(pred, str(pred))
        match = expected_name == predicted_name
        truncated = text[:80] + ".." if len(text) > 80 else text
        results.append({
            "expected": expected_name,
            "predicted": predicted_name,
            "match": match,
            "text": truncated,
        })
    return results


def generate_report(
    metrics_path: str,
    model_path: str,
    dataset_path: str,
    cm_image_path: str,
    baseline_path=None,
) -> str:
    """Generate the full markdown report."""
    # Load comparison data
    import sys
    sys.path.insert(0, os.path.dirname(__file__))
    from compare_metrics import compare

    comparison = compare(baseline_path, metrics_path)

    # Sanity check
    sanity_results = run_sanity_check(model_path, dataset_path)

    # Build report
    lines = []
    lines.append("## 🤖 Model Evaluation Report")
    lines.append("")
    lines.append("### ⚙️ Configuration")
    lines.append(f"**Current Model:** `{comparison['model_type']}`")
    lines.append(f"**Params:** `{json.dumps(comparison['model_params'], default=str)}`")
    lines.append("")
    lines.append("### 📊 Metrics Comparison")
    lines.append("| Metric | Main (Baseline) | PR (Candidate) | Delta |")
    lines.append("|---|---|---|---|")

    for m in comparison["metrics"]:
        base_str = f"{m['baseline']:.4f}" if m["baseline"] is not None else "N/A"
        cand_str = f"{m['candidate']:.4f}"
        if m["delta"] is not None:
            delta_str = f"{m['indicator']} {m['delta']:+.4f}"
        else:
            delta_str = "N/A"
        lines.append(f"| {m['name']} | {base_str} | {cand_str} | {delta_str} |")

    lines.append("")
    lines.append("### 🕵️ Inference Sanity Check (5 Samples)")
    lines.append("| Expected | Predicted (PR) | Match? | Text |")
    lines.append("|---|---|---|---|")

    for s in sanity_results:
        match_icon = "✅" if s["match"] else "❌"
        lines.append(
            f"| **{s['expected']}** | {s['predicted']} | {match_icon} | {s['text']} |"
        )

    # Embed confusion matrix image
    if cm_image_path and os.path.exists(cm_image_path):
        lines.append("")
        lines.append("### 📈 Confusion Matrix")
        with open(cm_image_path, "rb") as img_file:
            b64 = base64.b64encode(img_file.read()).decode("utf-8")
        lines.append(f"![Confusion Matrix](data:image/png;base64,{b64})")

    lines.append("")
    lines.append("<!-- Sticky Pull Request Comment -->")

    return "\n".join(lines)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate model evaluation report")
    parser.add_argument("--metrics", required=True, help="Path to candidate metrics JSON")
    parser.add_argument("--model", required=True, help="Path to trained model")
    parser.add_argument("--dataset", required=True, help="Path to dataset CSV")
    parser.add_argument("--cm-image", required=True, help="Path to confusion matrix PNG")
    parser.add_argument("--baseline", default=None, help="Path to baseline metrics JSON")
    args = parser.parse_args()
    report = generate_report(
        args.metrics, args.model, args.dataset, args.cm_image, args.baseline
    )
    print(report)
