# Model-Deployment-GDGoC

REST API backend untuk deteksi spam SMS berbahasa Indonesia menggunakan scikit-learn (CountVectorizer + MultinomialNB) dan FastAPI. Project ini merupakan demo CI/CD pipeline untuk ML sebagai bagian dari materi GDGoC UIN Jakarta TechTalk AI/ML Advanced.

## Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

## Training

```bash
python training/train.py
# Custom paths:
python training/train.py --dataset path/to/data.csv --output path/to/model.pkl
```

## Evaluation

```bash
python training/evaluate.py
# Custom paths:
python training/evaluate.py --model path/to/model.pkl --dataset path/to/data.csv --output-dir path/to/output
```

Output: `training/artifacts/metrics.json` dan `training/artifacts/confusion_matrix.png`

## Run API Server

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8080
# Atau dengan custom model path:
MODEL_PATH=path/to/model.pkl uvicorn app.main:app --port 8080
```

### Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| POST | `/predict` | Prediksi spam (body: `{"text": "..."}`) |

## Run Tests

```bash
pytest tests/ -v
```

## Folder Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI application
│   └── schemas.py       # Pydantic models
├── training/
│   ├── __init__.py
│   ├── train.py         # Training script
│   ├── evaluate.py      # Evaluation script
│   ├── data/            # Dataset CSV
│   └── artifacts/       # Model, metrics, charts
├── tests/
│   ├── __init__.py
│   ├── test_api.py      # API endpoint tests
│   └── test_model.py    # Model logic tests
├── scripts/
│   ├── __init__.py
│   ├── compare_metrics.py   # Metrics comparison
│   └── generate_report.py   # PR report generator
├── .github/workflows/
│   ├── ci-main.yml      # Main branch CI/CD
│   └── ci-pr.yml        # PR CI/CD
├── Dockerfile
├── requirements.txt
└── README.md
```

## CI/CD

### Main Branch (`ci-main.yml`)
Push ke `main` → Lint → Test → Train → Evaluate → Deploy ke Cloud Run

### Pull Request (`ci-pr.yml`)
PR ke `main` → Lint → Test → Train PR model → Evaluate → Compare dengan baseline → Post report ke PR comment
