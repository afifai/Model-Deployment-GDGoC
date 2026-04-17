"""Tests for the ML model pipeline."""

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline


def test_pipeline_fit_without_error():
    """Test that Pipeline can fit on sample data without error."""
    pipeline = make_pipeline(CountVectorizer(), MultinomialNB())
    texts = ["halo apa kabar", "promo diskon besar", "info penting segera"]
    labels = [0, 2, 1]
    pipeline.fit(texts, labels)


def test_pipeline_predict_after_fit():
    """Test that Pipeline can predict after fitting."""
    pipeline = make_pipeline(CountVectorizer(), MultinomialNB())
    texts = ["halo apa kabar", "promo diskon besar", "info penting segera"]
    labels = [0, 2, 1]
    pipeline.fit(texts, labels)
    predictions = pipeline.predict(["test message"])
    assert len(predictions) == 1


def test_prediction_output_validity():
    """Test that prediction output is a valid integer (0, 1, or 2)."""
    pipeline = make_pipeline(CountVectorizer(), MultinomialNB())
    texts = ["halo apa kabar", "promo diskon besar", "info penting segera"]
    labels = [0, 2, 1]
    pipeline.fit(texts, labels)
    predictions = pipeline.predict(["pesan baru untuk kamu"])
    for pred in predictions:
        assert int(pred) in (0, 1, 2)
