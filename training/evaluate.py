"""Evaluation script for SMS spam detection model."""

import argparse
import json
import os
import sys

import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    accuracy_score,
    classification_report,
)
from sklearn.model_selection import train_test_split

LABEL_MAP = {0: "normal", 1: "spam", 2: "promo"}


def evaluate(model_path: str, dataset_path: str, output_dir: str) -> tuple[str, str]:
    """Evaluate the trained model and save metrics + confusion matrix."""
    if not os.path.exists(model_path):
        print(f"Error: Model not found at {model_path}", file=sys.stderr)
        sys.exit(1)
    if not os.path.exists(dataset_path):
        print(f"Error: Dataset not found at {dataset_path}", file=sys.stderr)
        sys.exit(1)

    model = joblib.load(model_path)
    df = pd.read_csv(dataset_path)

    X = df["Teks"].astype(str)
    y = df["label"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42
    )

    y_pred = model.predict(X_test)

    accuracy = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred, output_dict=True, zero_division=0)

    # Extract model info
    nb_step = model.named_steps.get("multinomialnb", model[-1])
    model_type = type(nb_step).__name__
    model_params = nb_step.get_params()

    metrics = {
        "accuracy": round(accuracy, 4),
        "f1_normal": round(report.get("0", {}).get("f1-score", 0.0), 4),
        "f1_spam": round(report.get("1", {}).get("f1-score", 0.0), 4),
        "f1_promo": round(report.get("2", {}).get("f1-score", 0.0), 4),
        "model_type": model_type,
        "model_params": model_params,
    }

    os.makedirs(output_dir, exist_ok=True)

    metrics_path = os.path.join(output_dir, "metrics.json")
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=2, default=str)
    print(f"Metrics saved to: {metrics_path}")

    # Confusion matrix
    cm_path = os.path.join(output_dir, "confusion_matrix.png")
    label_names = [LABEL_MAP[i] for i in sorted(LABEL_MAP.keys())]
    disp = ConfusionMatrixDisplay.from_predictions(
        y_test, y_pred, display_labels=label_names, cmap="Blues"
    )
    disp.ax_.set_title("Confusion Matrix")
    plt.tight_layout()
    plt.savefig(cm_path, dpi=100)
    plt.close()
    print(f"Confusion matrix saved to: {cm_path}")

    # F1-score bar chart
    f1_path = os.path.join(output_dir, "f1_scores.png")
    f1_scores = [metrics["f1_normal"], metrics["f1_spam"], metrics["f1_promo"]]
    colors = ["#34a853", "#ea4335", "#fbbc04"]
    fig, ax = plt.subplots(figsize=(6, 4))
    bars = ax.bar(label_names, f1_scores, color=colors, edgecolor="white", linewidth=1.2)
    for bar, score in zip(bars, f1_scores):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.01,
                f"{score:.3f}", ha="center", va="bottom", fontsize=12, fontweight="bold")
    ax.set_ylim(0, 1.1)
    ax.set_ylabel("F1-Score")
    ax.set_title("F1-Score per Class")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    plt.tight_layout()
    plt.savefig(f1_path, dpi=100)
    plt.close()
    print(f"F1 bar chart saved to: {f1_path}")

    # Class distribution chart
    dist_path = os.path.join(output_dir, "class_distribution.png")
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    # Actual distribution
    actual_counts = y_test.value_counts().sort_index()
    actual_labels = [LABEL_MAP[i] for i in actual_counts.index]
    axes[0].pie(actual_counts, labels=actual_labels, autopct="%1.1f%%",
                colors=colors, startangle=90)
    axes[0].set_title("Actual (Test Set)")
    # Predicted distribution
    pred_series = pd.Series(y_pred)
    pred_counts = pred_series.value_counts().sort_index()
    pred_labels = [LABEL_MAP[i] for i in pred_counts.index]
    axes[1].pie(pred_counts, labels=pred_labels, autopct="%1.1f%%",
                colors=colors, startangle=90)
    axes[1].set_title("Predicted")
    plt.suptitle("Class Distribution: Actual vs Predicted", fontsize=13, fontweight="bold")
    plt.tight_layout()
    plt.savefig(dist_path, dpi=100)
    plt.close()
    print(f"Class distribution chart saved to: {dist_path}")

    return metrics_path, cm_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate SMS spam detection model")
    parser.add_argument(
        "--model",
        default=os.path.join(os.path.dirname(__file__), "artifacts", "model.pkl"),
        help="Path to trained model pickle file",
    )
    parser.add_argument(
        "--dataset",
        default=os.path.join(os.path.dirname(__file__), "data", "dataset_sms_spam_v1.csv"),
        help="Path to dataset CSV file",
    )
    parser.add_argument(
        "--output-dir",
        default=os.path.join(os.path.dirname(__file__), "artifacts"),
        help="Directory to save evaluation outputs",
    )
    args = parser.parse_args()
    evaluate(args.model, args.dataset, args.output_dir)
