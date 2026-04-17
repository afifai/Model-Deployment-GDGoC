<p align="center">
  <img src="assets/logo.png" alt="NgodingAI Logo" width="400"/>
</p>

<h1 align="center">Model-Deployment-GDGoC</h1>

<p align="center">
  <strong>Demo CI/CD Pipeline untuk Machine Learning</strong><br/>
  GDGoC UIN Jakarta | TechTalk AI/ML Advanced 25.26<br/>
  <em>by Afif AI</em>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.11-blue" alt="Python"/>
  <img src="https://img.shields.io/badge/framework-FastAPI-green" alt="FastAPI"/>
  <img src="https://img.shields.io/badge/ML-scikit--learn-orange" alt="scikit-learn"/>
  <img src="https://img.shields.io/badge/deploy-Cloud%20Run-blue" alt="Cloud Run"/>
</p>

---

## Apa Ini?

Project ini adalah contoh nyata bagaimana **CI/CD (Continuous Integration / Continuous Deployment)** diterapkan pada proyek **Machine Learning**. Kita menggunakan model sederhana untuk **deteksi spam SMS** berbahasa Indonesia.

Yang keren dari project ini:
- **Push kode ke `main`** → otomatis lint, test, train model, evaluasi, dan deploy API ke Google Cloud Run
- **Buat Pull Request** → otomatis train model, evaluasi, bandingkan dengan baseline, dan posting report di PR comment

---

## Daftar Isi

- [Prasyarat](#prasyarat)
- [Setup Lokal](#setup-lokal)
- [Menjalankan Training](#menjalankan-training)
- [Menjalankan Evaluasi](#menjalankan-evaluasi)
- [Menjalankan API Server](#menjalankan-api-server)
- [Menjalankan Tests](#menjalankan-tests)
- [Setup Google Cloud (untuk Deployment)](#setup-google-cloud-untuk-deployment)
- [Setup GitHub Secrets](#setup-github-secrets)
- [Cara Kerja CI/CD](#cara-kerja-cicd)
- [Struktur Folder](#struktur-folder)
- [API Endpoints](#api-endpoints)

---

## Prasyarat

Sebelum mulai, pastikan kamu sudah punya:

- **Python 3.11+** — [Download di sini](https://www.python.org/downloads/)
- **Git** — [Download di sini](https://git-scm.com/downloads)
- **Akun GitHub** — [Daftar di sini](https://github.com/signup)
- **Akun Google Cloud** (untuk deployment) — [Daftar di sini](https://cloud.google.com/free)

Cek apakah sudah terinstall:

```bash
python3 --version   # Harus 3.11 atau lebih baru
git --version        # Harus terinstall
```

---

## Setup Lokal

### 1. Clone Repository

```bash
git clone git@github.com:afifai/Model-Deployment-GDGoC.git
cd Model-Deployment-GDGoC
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

> 💡 **Tips:** Disarankan pakai virtual environment:
> ```bash
> python3 -m venv venv
> source venv/bin/activate   # macOS/Linux
> venv\Scripts\activate      # Windows
> pip install -r requirements.txt
> ```

---

## Menjalankan Training

Training akan membuat model deteksi spam dan menyimpannya sebagai file `.pkl`.

```bash
python training/train.py
```

Output:
```
Model saved to: training/artifacts/model.pkl
```

**Custom paths** (opsional):
```bash
python training/train.py --dataset path/ke/data.csv --output path/ke/model.pkl
```

---

## Menjalankan Evaluasi

Evaluasi menghasilkan metrik performa dan confusion matrix.

```bash
python training/evaluate.py
```

Output:
```
Metrics saved to: training/artifacts/metrics.json
Chart saved to: training/artifacts/confusion_matrix.png
```

**Custom paths** (opsional):
```bash
python training/evaluate.py --model path/ke/model.pkl --dataset path/ke/data.csv --output-dir path/ke/output
```

---

## Menjalankan API Server

Pastikan model sudah di-train dulu (lihat langkah di atas).

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8080
```

Buka browser ke `http://localhost:8080/docs` untuk melihat dokumentasi API interaktif (Swagger UI).

**Test prediksi:**
```bash
curl -X POST http://localhost:8080/predict \
  -H "Content-Type: application/json" \
  -d '{"text": "GRATIS! Dapatkan hadiah 1 juta rupiah, klik link ini sekarang!"}'
```

---

## Menjalankan Tests

```bash
# Pastikan model sudah di-train dulu!
python training/train.py

# Jalankan tests
pytest tests/ -v
```

---

## Setup Google Cloud (untuk Deployment)

> ⚠️ **Bagian ini hanya diperlukan jika kamu ingin deploy API ke Google Cloud Run.** Kalau cuma mau jalankan lokal, skip bagian ini.

### Step 1: Install Google Cloud CLI

**macOS:**
```bash
curl -sSL https://sdk.cloud.google.com | bash
```

**Windows:**
Download installer dari: https://cloud.google.com/sdk/docs/install

**Linux:**
```bash
curl -sSL https://sdk.cloud.google.com | bash
```

Setelah install, restart terminal lalu verifikasi:
```bash
gcloud --version
```

### Step 2: Login ke Google Cloud

```bash
gcloud auth login
```

Ini akan membuka browser untuk login ke akun Google kamu.

### Step 3: Buat atau Pilih Project

**Buat project baru:**
```bash
gcloud projects create NAMA-PROJECT-KAMU --name="Spam Detector API"
```

**Atau pilih project yang sudah ada:**
```bash
gcloud config set project NAMA-PROJECT-KAMU
```

> 💡 Ganti `NAMA-PROJECT-KAMU` dengan ID project kamu (contoh: `spam-detector-123`).

### Step 4: Enable API yang Dibutuhkan

```bash
gcloud services enable run.googleapis.com
gcloud services enable artifactregistry.googleapis.com
gcloud services enable cloudbuild.googleapis.com
```

### Step 5: Buat Service Account untuk GitHub Actions

Service account ini yang akan dipakai GitHub Actions untuk deploy ke Cloud Run.

```bash
# Buat service account
gcloud iam service-accounts create github-actions \
  --display-name="GitHub Actions Deployer"
```

### Step 6: Berikan Permission ke Service Account

```bash
PROJECT_ID=$(gcloud config get-value project)
SA_EMAIL="github-actions@${PROJECT_ID}.iam.gserviceaccount.com"

# Permission untuk deploy ke Cloud Run
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/run.admin"

# Permission untuk push Docker image
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/artifactregistry.admin"

# Permission untuk Cloud Build
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/cloudbuild.builds.builder"

# Permission untuk storage (Cloud Build butuh ini)
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/storage.admin"

# Permission untuk act as service account
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/iam.serviceAccountUser"
```

### Step 7: Generate Key untuk GitHub Actions

```bash
gcloud iam service-accounts keys create gcp-key.json \
  --iam-account="github-actions@${PROJECT_ID}.iam.gserviceaccount.com"
```

Ini akan membuat file `gcp-key.json`. **Simpan isinya, kita butuh untuk GitHub Secrets.**

> ⚠️ **PENTING:** Jangan commit file `gcp-key.json` ke repository! Hapus setelah di-copy ke GitHub Secrets.

---

## Setup GitHub Secrets

### Step 1: Buka Settings Repository

1. Buka repository di GitHub: https://github.com/afifai/Model-Deployment-GDGoC
2. Klik **Settings** (tab paling kanan)
3. Di sidebar kiri, klik **Secrets and variables** → **Actions**
4. Klik **New repository secret**

### Step 2: Tambahkan 3 Secrets

| Nama Secret | Isi | Contoh |
|---|---|---|
| `GCP_PROJECT_ID` | ID project Google Cloud kamu | `spam-detector-123` |
| `GCP_SA_KEY` | Seluruh isi file `gcp-key.json` (copy-paste semua dari `{` sampai `}`) | `{"type": "service_account", ...}` |
| `GCP_REGION` | Region Google Cloud (pilih yang terdekat) | `asia-southeast2` (Jakarta) |

> 💡 **Cara copy isi `gcp-key.json`:**
> ```bash
> cat gcp-key.json
> ```
> Copy semua output-nya, paste ke field Value di GitHub Secrets.

### Step 3: Hapus Key dari Lokal

```bash
rm gcp-key.json
```

---

## Cara Kerja CI/CD

### Push ke `main` branch

```
Push Code → Lint (ruff) → Test (pytest) → Train Model → Evaluasi → Deploy ke Cloud Run
```

Setiap kali kode di-push atau di-merge ke `main`, GitHub Actions otomatis:
1. **Lint** — Cek kualitas kode dengan ruff
2. **Test** — Jalankan unit tests dengan pytest
3. **Train** — Latih model dari dataset
4. **Evaluate** — Evaluasi performa model
5. **Deploy** — Deploy API ke Google Cloud Run

### Pull Request ke `main`

```
PR Dibuat → Lint → Test → Train Model PR → Evaluasi → Bandingkan dengan Baseline → Post Report
```

Setiap kali PR dibuat atau di-update:
1. **Lint & Test** — Sama seperti di atas
2. **Train** — Latih model dari kode PR
3. **Evaluate** — Evaluasi model PR
4. **Compare** — Bandingkan metrik model PR vs model di `main`
5. **Report** — Posting tabel perbandingan di PR comment

Contoh report yang muncul di PR:

| Metric | Main (Baseline) | PR (Candidate) | Delta |
|---|---|---|---|
| Accuracy | 0.9370 | 0.9440 | 🟢 +0.0070 |
| F1-Score (normal) | 0.9500 | 0.9550 | 🟢 +0.0050 |

---

## Struktur Folder

```
.
├── app/                          # FastAPI application
│   ├── __init__.py
│   ├── main.py                   # API endpoints (/health, /predict)
│   └── schemas.py                # Pydantic request/response models
├── training/
│   ├── __init__.py
│   ├── train.py                  # Script training model
│   ├── evaluate.py               # Script evaluasi model
│   ├── data/
│   │   └── dataset_sms_spam_v1.csv  # Dataset SMS spam
│   └── artifacts/                # Output: model.pkl, metrics.json, dll
├── tests/
│   ├── __init__.py
│   ├── test_api.py               # Test API endpoints
│   └── test_model.py             # Test model pipeline
├── scripts/
│   ├── __init__.py
│   ├── compare_metrics.py        # Bandingkan metrik 2 model
│   └── generate_report.py        # Generate PR report markdown
├── assets/
│   └── logo.png                  # Logo NgodingAI
├── .github/workflows/
│   ├── ci-main.yml               # CI/CD untuk push ke main
│   └── ci-pr.yml                 # CI/CD untuk Pull Request
├── Dockerfile                    # Container untuk Cloud Run
├── requirements.txt              # Python dependencies
└── README.md                     # File ini!
```

---

## API Endpoints

| Method | Path | Deskripsi | Body |
|---|---|---|---|
| `GET` | `/health` | Health check | — |
| `POST` | `/predict` | Prediksi spam/bukan | `{"text": "isi SMS"}` |
| `GET` | `/docs` | Swagger UI (dokumentasi interaktif) | — |

### Contoh Response `/predict`

```json
{
  "prediction": 2,
  "label": "spam"
}
```

Label:
- `0` = **normal** (SMS biasa)
- `1` = **unknown** (tidak diketahui)
- `2` = **spam** (SMS spam/promosi)

---

<p align="center">
  Made with ❤️ by <strong>Afif AI</strong> for GDGoC UIN Jakarta
</p>
