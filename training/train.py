"""Training script for SMS spam detection model."""

import argparse
import os
import sys

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline


def train(dataset_path: str, output_path: str) -> str:
    """Train the spam detection model and save to disk."""
    if not os.path.exists(dataset_path):
        print(f"Error: Dataset not found at {dataset_path}", file=sys.stderr)
        sys.exit(1)

    df = pd.read_csv(dataset_path)

    required_cols = {"Teks", "label"}
    if not required_cols.issubset(df.columns):
        print(f"Error: Dataset missing required columns: {required_cols}", file=sys.stderr)
        sys.exit(1)

    X = df["Teks"].astype(str)
    y = df["label"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42
    )

    pipeline = make_pipeline(
        TfidfVectorizer(
            max_features=8000,
            ngram_range=(1, 2),
            sublinear_tf=True,
        ),
        MultinomialNB(
            alpha=0.1,
        ),
    )
    pipeline.fit(X_train, y_train)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    joblib.dump(pipeline, output_path)
    print(f"Model saved to: {output_path}")
    return output_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train SMS spam detection model")
    parser.add_argument(
        "--dataset",
        default=os.path.join(os.path.dirname(__file__), "data", "dataset_sms_spam_v1.csv"),
        help="Path to dataset CSV file",
    )
    parser.add_argument(
        "--output",
        default=os.path.join(os.path.dirname(__file__), "artifacts", "model.pkl"),
        help="Path to save trained model",
    )
    args = parser.parse_args()
    train(args.dataset, args.output)
