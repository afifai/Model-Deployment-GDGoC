"""Generate markdown PR report for model evaluation."""

import argparse
import json
import os

import joblib
import pandas as pd
from sklearn.metrics import confusion_matrix as cm_func
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
    image_url=None,
) -> str:
    """Generate the full markdown report."""
    import sys
    sys.path.insert(0, os.path.dirname(__file__))
    from compare_metrics import compare

    comparison = compare(baseline_path, metrics_path)
    sanity_results = run_sanity_check(model_path, dataset_path)

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

    # Confusion matrix table
    lines.append("")
    lines.append("### 📈 Confusion Matrix")
    try:
        model = joblib.load(model_path)
        df = pd.read_csv(dataset_path)
        X = df["Teks"].astype(str)
        y = df["label"]
        _, X_test, _, y_test = train_test_split(X, y, test_size=0.25, random_state=42)
        y_pred = model.predict(X_test)
        cm = cm_func(y_test, y_pred)
        labels = sorted(LABEL_MAP.keys())
        label_names = [LABEL_MAP[la] for la in labels]

        lines.append("")
        header = "| Actual \\ Predicted | " + " | ".join(f"**{n}**" for n in label_names) + " |"
        lines.append(header)
        lines.append("|---|" + "---|" * len(label_names))
        for i, row in enumerate(cm):
            row_str = " | ".join(str(v) for v in row)
            lines.append(f"| **{label_names[i]}** | {row_str} |")
    except Exception:
        lines.append("> Confusion matrix tidak tersedia.")

    # Confusion matrix image
    if image_url:
        lines.append("")
        lines.append("### 📊 Confusion Matrix (Visual)")
        lines.append("")
        lines.append(f"![Confusion Matrix]({image_url})")
    elif cm_image_path and os.path.exists(cm_image_path):
        lines.append("")
        lines.append("> 📎 Confusion matrix image tersedia sebagai artifact.")

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
    parser.add_argument("--image-url", default=None, help="URL to confusion matrix image")
    args = parser.parse_args()
    report = generate_report(
        args.metrics, args.model, args.dataset, args.cm_image, args.baseline, args.image_url
    )
    print(report)
