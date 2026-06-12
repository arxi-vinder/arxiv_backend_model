# Arxivinder - Backend Model

Arxivinder adalah sistem rekomendasi berbasis machine learning untuk paper akademik yang menggunakan Content-Based Filtering (CBF) dan Upper Confidence Bound (UCB) algorithm untuk memberikan rekomendasi paper yang personal dan relevan kepada setiap user.

## 📋 Daftar Isi

- [Fitur Utama](#-fitur-utama)
- [Tech Stack](#-tech-stack)
- [Proses Instalasi](#-proses-instalasi)
- [Struktur Folder](#-struktur-folder)
- [Database & Entitas](#-database--entitas)
- [API Documentation](#-api-documentation)
- [Cara Menggunakan](#-cara-menggunakan)
- [Troubleshooting](#-troubleshooting)

---

## ✨ Fitur Utama

- **Content-Based Filtering (CBF)**: Rekomendasi berdasarkan kesamaan konten paper
- **Upper Confidence Bound (UCB)**: Algoritma bandit untuk explore/exploit balance
- **Paper Management**: CRUD paper dengan kategori dan metadata
- **Vectorization Cache**: Caching TF-IDF vectors untuk performa optimal
- **User Feedback**: Tracking user feedback terhadap rekomendasi
- **Evaluation System**: Evaluasi kualitas rekomendasi dengan metrics (Precision, Recall, NDCG)
- **Authentication**: JWT-based authentication untuk user dan admin
- **Admin Dashboard**: Management paper dan vectorization

---

## 🛠 Tech Stack

### Backend Framework
- **FastAPI** (v0.128.0) - Web framework modern Python
- **SQLModel** (v0.0.31) - ORM berbasis SQLAlchemy + Pydantic
- **PyMySQL** (v1.1.2) - MySQL connector

### Machine Learning
- **scikit-learn** (v1.8.0) - TF-IDF Vectorizer, cosine similarity
- **numpy** (v2.4.0) - Numerical computing
- **nltk** (v3.9.2) - NLP (tokenization, stopwords removal)
- **pandas** (v2.3.3) - Data processing

### Database
- **MySQL** - Relational database
- **Alembic** (v1.18.0) - Database migration tool

### Authentication & Security
- **PyJWT** (v2.11.0) - JWT token handling
- **bcrypt** (v5.0.0) - Password hashing
- **passlib** (v1.7.4) - Password cryptography

### Server & Deployment
- **Uvicorn** (v0.40.0) - ASGI server
- **Gunicorn** (v26.0.0) - Production WSGI server

---

## 📦 Proses Instalasi

### Prerequisites
- Python 3.8 atau lebih tinggi
- MySQL Server 5.7 atau lebih tinggi
- pip (Python package manager)

### Step 1: Clone Repository

```bash
git clone https://github.com/arxi-vinder/backend_model.git
cd backend_model
```

### Step 2: Setup Python Virtual Environment

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Setup Database Configuration

Copy `.env.example` ke `.env`:

```bash
# Windows
copy .env.example .env

# macOS/Linux
cp .env.example .env
```

Edit file `.env` dengan konfigurasi MySQL Anda:

```env
MYSQL_USER=your_username
MYSQL_PASSWORD=your_password
MYSQL_HOST=your_host
MYSQL_PORT=3306
MYSQL_DB=your_database
NGROK_AUTH_TOKEN=your_token (optional)
```

### Step 5: Setup Database Schema

```bash
# Jalankan migration untuk create tables
alembic upgrade head
```

Atau jika belum ada revisi migration:

```bash
# Create migration
alembic revision --autogenerate -m "Initial schema"

# Apply migration
alembic upgrade head
```

### Step 6: Run Server

```bash
# Development (dengan auto-reload)
python app/main.py

# Atau menggunakan uvicorn langsung
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Server akan berjalan di `http://localhost:8000`

### Step 7: Verify Installation

Buka browser dan akses:
```
http://localhost:8000/
```

Anda akan mendapat response:
```json
{
  "status": "Success",
  "message": "Hello Coy"
}
```

---

## 📁 Struktur Folder

### Root Level Files

| File/Folder | Deskripsi |
|---|---|
| `app/` | Source code utama aplikasi |
| `alembic/` | Database migration files |
| `requirements.txt` | Python dependencies |
| `.env.example` | Template environment variables |
| `Procfile` | Configuration untuk production deployment |
| `README_*.md` | Documentation files tambahan |

### 📂 app/ - Source Code Utama

```
app/
├── main.py                 # Entry point aplikasi
├── server.py              # FastAPI app configuration  
├── cli.py                 # Command line interface
├── api/                   # API routes
│   └── routes/
│       ├── paper_api.py        # Paper CRUD endpoints
│       ├── recommender_api.py  # Recommendation endpoints
│       ├── auth_api.py         # Authentication endpoints
│       ├── feedback_api.py      # Feedback endpoints
│       ├── admin_api.py        # Admin endpoints
│       ├── eval_result.py      # Evaluation endpoints
│       └── evaluation.py       # Evaluation setup
├── db/                    # Database configuration
│   └── database.py        # SQLModel engine & session
├── model/                 # Database models (ORM)
│   ├── paper.py           # Paper entity
│   ├── user.py            # User entity
│   ├── feedback.py        # Feedback entity
│   ├── recommendation_log.py
│   ├── evaluation_model.py
│   ├── evaluation_res.py
│   ├── admin.py
│   └── vectorization_cache.py
├── repositories/          # Data access layer
│   ├── paper_repository.py
│   ├── feedback_repository.py
│   ├── recommendation_log_repository.py
│   ├── vectorization_cache_repository.py
│   ├── evaluation_repository.py
│   ├── auth_repository.py
│   └── admin_repository.py
├── services/              # Business logic layer
│   ├── recommendation_service.py
│   ├── paper_service.py
│   ├── feedback_service.py
│   ├── ucb_service.py
│   ├── vectorization_cache_service.py
│   ├── vectorization_async_service.py
│   ├── recommendation_log_service.py
│   └── evaluation_service.py
├── schemas/               # Request/Response models (Pydantic)
│   ├── request/
│   │   ├── paper_request.py
│   │   ├── feedback_request.py
│   │   └── user_request.py
│   └── response/
│       ├── paper_response.py
│       ├── feedback_response.py
│       └── evaluation_response.py
├── utils/                 # Utility functions
│   ├── jwt.py             # JWT token handling
│   ├── tf_calculator.py   # Term Frequency calculator
│   ├── vectorization_startup.py
│   └── ...
├── ml/                    # Machine learning models
│   └── arxiv_papers_daily_fixed.csv  # Sample data
└── cache/                 # Vectorization cache storage
    └── vectorization/
```

### Penjelasan Folder Utama

#### `app/api/routes/` - API Endpoints
**Tujuan:** Mendefinisikan REST API endpoints untuk berbagai fitur aplikasi

| File | Fungsi |
|------|--------|
| `paper_api.py` | GET/POST/PUT/DELETE papers, search, filter by date range |
| `recommender_api.py` | GET recommendations dengan CBF+UCB ranking, vectorize papers |
| `auth_api.py` | User login/registration, JWT token generation |
| `feedback_api.py` | POST/GET user feedback on recommendations |
| `admin_api.py` | Admin login, management endpoints |
| `eval_result.py` | GET evaluation metrics (Precision, Recall, NDCG, MAP) |

#### `app/db/` - Database Configuration
**Tujuan:** Mengelola koneksi ke MySQL dan session management

- **database.py** - SQLModel engine setup, SessionLocal factory, connection pooling

#### `app/model/` - Database Models (ORM)
**Tujuan:** Mendefinisikan struktur table di MySQL dengan SQLAlchemy

Models yang ada:
- `paper.py` - Table papers
- `user.py` - Table users
- `feedback.py` - Table feedbacks
- `recommendation_log.py` - Table recommendation_logs
- `evaluation_res.py` - Table evaluation_results
- `admin.py` - Table admins
- `vectorization_cache.py` - Table vectorization_cache

#### `app/repositories/` - Data Access Layer (DAO)
**Tujuan:** Abstraksi database queries, isolasi database logic dari business logic

Setiap repository handle CRUD operations spesifik:

| Repository | Query yang di-handle |
|---|---|
| `PaperRepository` | SELECT/INSERT/UPDATE/DELETE papers, batch queries |
| `FeedbackRepository` | GET/POST feedbacks, query by user/paper |
| `RecommendationLogRepository` | Log recommendations, query history |
| `VectorizationCacheRepository` | Save/load cache metadata |
| `EvaluationRepository` | Query evaluation results & metrics |
| `AuthRepository` | User authentication queries |
| `AdminRepository` | Admin authentication |

#### `app/services/` - Business Logic Layer
**Tujuan:** Implementasi algoritma dan business rules

Layanan utama:

| Service | Fungsi |
|---------|--------|
| `recommendation_service.py` | **Content-Based Filtering**: TF-IDF vectorization, cosine similarity calculation, build model |
| `ucb_service.py` | **Upper Confidence Bound**: Multi-armed bandit algorithm untuk ranking |
| `paper_service.py` | Paper processing, filtering, sorting |
| `vectorization_cache_service.py` | Save/load precomputed vectors (pickle), cache validation |
| `vectorization_async_service.py` | Async vectorization untuk large datasets |
| `evaluation_service.py` | Calculate Precision@K, Recall@K, NDCG@K, MAP@K |
| `recommendation_log_service.py` | Log & retrieve recommendation history |

#### `app/schemas/` - Validation & Serialization Models
**Tujuan:** Pydantic models untuk validasi input dan serialisasi output JSON

- **request/** - Validasi request body dari client
- **response/** - Structure response JSON dari API

#### `app/utils/` - Utility Functions
**Tujuan:** Helper functions shared across services

| File | Fungsi |
|------|--------|
| `jwt.py` | Token generation, validation, user extraction |
| `tf_calculator.py` | Term Frequency calculation dari abstracts CSV |
| `vectorization_startup.py` | Cache initialization on app startup |

#### `app/cache/vectorization/` - Cache Storage
**Tujuan:** Menyimpan precomputed TF-IDF vectors sebagai pickle files

- Format: `paper_{paper_id}.pkl`
- Digunakan untuk fast recommendation tanpa perlu compute ulang TF-IDF

#### `alembic/` - Database Migrations
**Tujuan:** Version control untuk database schema changes

- `env.py` - Migration configuration
- `script.py.mako` - Migration template
- `versions/` - Historical migration files

---

## 📊 Database & Entitas

### Entity Relationship Diagram

```
┌─────────────┐         ┌──────────────┐
│   users     │────1:N──│  feedbacks   │
└─────────────┘         └──────────────┘
       │                       │
       │                       │
       1                       N
       │                       │
       N                       1
       │                       │
   ┌───────────────────────────────────┐
   │         papers                    │
   └───────────────────────────────────┘
       │                    │
       1                    N
       │                    │
       N                    1
       │                    │
┌─────────────────┐  ┌─────────────────────┐
│recommendation   │  │ evaluation_results  │
│   _logs         │  └─────────────────────┘
└─────────────────┘
```

### 📋 Tabel Database

#### 1. **users** - Data User

| Kolom | Tipe | Keterangan |
|-------|------|-----------|
| `id` | INT | Primary Key, Auto Increment |
| `username` | VARCHAR(255) | Username unik user |
| `password` | VARCHAR(255) | Password hash (bcrypt) |
| `created_at` | DATETIME | Timestamp pembuatan user |

**Relasi:**
- 1 User : N Feedbacks
- 1 User : N RecommendationLogs
- 1 User : N EvaluationResults

**Contoh Data:**
```sql
INSERT INTO users VALUES (1, 'john_doe', '$2b$12$abcde...', '2024-01-15 10:30:00');
```

---

#### 2. **papers** - Data Paper Akademik

| Kolom | Tipe | Keterangan |
|-------|------|-----------|
| `id` | INT | Primary Key, Auto Increment |
| `title` | VARCHAR(255) | Judul paper |
| `abstract` | TEXT | Abstrak/ringkasan paper |
| `published_date` | DATETIME | Tanggal publikasi |
| `category` | VARCHAR(100) | Kategori (e.g., "cs.AI", "math.CO") |
| `url` | VARCHAR(500) | Link ke paper (arxiv, doi, dll) |
| `author` | VARCHAR(500) | Nama author(s) |
| `created_at` | DATETIME | Waktu paper ditambah ke system |

**Relasi:**
- 1 Paper : N Feedbacks
- 1 Paper : N RecommendationLogs
- 1 Paper : N EvaluationResults

**Contoh Data:**
```sql
INSERT INTO papers VALUES 
(1, 'Attention Is All You Need', 'We propose a new simple network architecture...', 
'2017-06-12', 'cs.CL', 'https://arxiv.org/abs/1706.03762', 
'Vaswani et al.', '2024-01-15 10:30:00');
```

---

#### 3. **feedbacks** - User Feedback Terhadap Rekomendasi

| Kolom | Tipe | Keterangan |
|-------|------|-----------|
| `id` | INT | Primary Key, Auto Increment |
| `user_id` | INT | Foreign Key → users.id |
| `paper_id` | INT | Foreign Key → papers.id |
| `response` | INT | Rating: 1 (like), 0 (neutral), -1 (dislike) |
| `created_at` | DATETIME | Timestamp feedback |

**Relasi:**
- N:1 ke users (many feedbacks per user)
- N:1 ke papers (many feedbacks per paper)

**Contoh Data:**
```sql
INSERT INTO feedbacks VALUES 
(1, 1, 2, 1, '2024-01-16 14:20:00'); -- user 1 likes paper 2
(2, 1, 3, -1, '2024-01-16 15:00:00'); -- user 1 dislikes paper 3
```

---

#### 4. **recommendation_logs** - History Rekomendasi Paper

| Kolom | Tipe | Keterangan |
|-------|------|-----------|
| `id` | INT | Primary Key, Auto Increment |
| `user_id` | INT | Foreign Key → users.id |
| `paper_id` | INT | Foreign Key → papers.id (paper yang di-recommend) |
| `rank` | INT | Ranking dalam top-N recommendation (1, 2, 3, ...) |
| `ucb_score` | FLOAT | UCB algorithm score (0-1) |
| `cbf_score` | FLOAT | CBF similarity score (0-1) |
| `clicked` | BOOLEAN | User klik recommendation? |
| `created_at` | DATETIME | Waktu rekomendasi dibuat |

**Relasi:**
- N:1 ke users
- N:1 ke papers

**Contoh Data:**
```sql
INSERT INTO recommendation_logs VALUES
(1, 1, 5, 1, 0.92, 0.87, TRUE, '2024-01-16 10:15:00');
(2, 1, 8, 2, 0.88, 0.82, FALSE, '2024-01-16 10:15:00');
```

---

#### 5. **evaluation_results** - Hasil Evaluasi Rekomendasi

| Kolom | Tipe | Keterangan |
|-------|------|-----------|
| `id` | INT | Primary Key, Auto Increment |
| `user_id` | INT | Foreign Key → users.id |
| `paper_id` | INT | Foreign Key → papers.id |
| `precision_at_k` | FLOAT | Precision@K metric (0-1) |
| `recall_at_k` | FLOAT | Recall@K metric (0-1) |
| `ndcg_at_k` | FLOAT | NDCG@K metric (0-1) |
| `map_at_k` | FLOAT | MAP@K metric (0-1) |
| `created_at` | DATETIME | Timestamp evaluasi |

**Relasi:**
- N:1 ke users
- N:1 ke papers

**Metrics Penjelasan:**
- **Precision@K**: Berapa % dari top-K recommendations yang relevant
- **Recall@K**: Berapa % dari semua relevant items yang ada di top-K
- **NDCG@K**: Normalized Discounted Cumulative Gain (ranking quality)
- **MAP@K**: Mean Average Precision

---

#### 6. **vectorization_cache** - Cache Metadata

| Kolom | Tipe | Keterangan |
|-------|------|-----------|
| `id` | INT | Primary Key, Auto Increment |
| `paper_id` | INT | Paper yang di-cache |
| `cache_path` | VARCHAR(500) | Path relatif ke pickle file |
| `created_at` | DATETIME | Waktu cache dibuat |
| `updated_at` | DATETIME | Terakhir diupdate |

**Tujuan:** Metadata untuk tracking cache files, validasi cache validity

---

#### 7. **admins** - Admin Users

| Kolom | Tipe | Keterangan |
|-------|------|-----------|
| `id` | INT | Primary Key, Auto Increment |
| `username` | VARCHAR(255) | Admin username |
| `password` | VARCHAR(255) | Password hash (bcrypt) |
| `created_at` | DATETIME | Waktu pembuatan |

---

## 🔌 API Documentation

### Base URL
```
http://localhost:8000/api/v1
```

### Authentication

Gunakan JWT token pada header untuk endpoints yang memerlukan authentication:

```bash
curl -H "Authorization: Bearer <access_token>" http://localhost:8000/api/v1/...
```

Token didapat setelah login, berlaku 24 jam.

---

### 📄 Paper Endpoints

#### GET /papers
Fetch semua papers dengan filter opsional

**Query Parameters:**
- `limit` (int, default: 100) - Jumlah papers per halaman
- `start_date` (datetime, optional) - Filter published_date >= start_date
- `end_date` (datetime, optional) - Filter published_date <= end_date
- `sort` (string, default: "newest") - "newest" atau "oldest"

**Example:**
```bash
curl "http://localhost:8000/api/v1/papers?limit=10&sort=newest"
```

**Response (200 OK):**
```json
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "title": "Attention Is All You Need",
      "abstract": "The dominant sequence transduction models...",
      "published_date": "2017-06-12",
      "category": "cs.CL",
      "author": "Vaswani et al.",
      "url": "https://arxiv.org/abs/1706.03762"
    }
  ]
}
```

---

#### POST /papers
Tambah paper baru

**Request Body:**
```json
{
  "title": "New Paper Title",
  "abstract": "Abstract text here...",
  "published_date": "2024-01-15T10:30:00",
  "category": "cs.AI",
  "author": "Author Name(s)",
  "url": "https://arxiv.org/abs/2401.00001"
}
```

**Response (201 Created):**
```json
{
  "status": "success",
  "data": {
    "id": 101,
    "title": "New Paper Title",
    ...
  }
}
```

---

#### POST /papers/bulk
Tambah multiple papers sekaligus

**Request Body:**
```json
{
  "papers": [
    {
      "title": "Paper 1",
      "abstract": "Abstract 1...",
      "published_date": "2024-01-15",
      "category": "cs.AI",
      "author": "Author 1",
      "url": "https://..."
    },
    {
      "title": "Paper 2",
      "abstract": "Abstract 2...",
      "published_date": "2024-01-16",
      "category": "cs.ML",
      "author": "Author 2",
      "url": "https://..."
    }
  ]
}
```

**Response (201 Created):**
```json
{
  "status": "success",
  "message": "2 papers created successfully"
}
```

---

#### PUT /papers/{paper_id}
Update paper by ID

**Request Body:**
```json
{
  "title": "Updated Title",
  "abstract": "Updated abstract...",
  "category": "cs.LG"
}
```

---

#### DELETE /papers/{paper_id}
Delete paper by ID

**Response:**
```json
{
  "status": "success",
  "message": "Paper deleted"
}
```

---

### 🤖 Recommendation Endpoints

#### GET /recommend/{paper_id}
Dapatkan rekomendasi papers berdasarkan satu paper (seeding)

**Parameters:**
- `paper_id` (path) - ID paper sebagai seed
- `top_n` (query, default: 5) - Jumlah rekomendasi yang dikembalikan

**Headers:**
- `Authorization: Bearer <token>` (required)

**Example:**
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/v1/recommend/1?top_n=5"
```

**Response (200 OK):**
```json
{
  "status": "success",
  "data": [
    {
      "rank": 1,
      "paper_id": 2,
      "title": "Recommended Paper 1",
      "cbf_score": 0.87,
      "ucb_score": 0.91
    },
    {
      "rank": 2,
      "paper_id": 5,
      "title": "Recommended Paper 2",
      "cbf_score": 0.82,
      "ucb_score": 0.88
    }
  ]
}
```

**Scores:**
- `cbf_score`: Content-Based Filtering similarity (0-1)
- `ucb_score`: Final UCB ranking score (0-1)

---

#### POST /vectorize-all-papers
Vectorize semua papers dan cache results (Admin only)

Proses ini:
1. Load semua abstracts dari database
2. Preprocess teks (lowercase, remove stopwords, tokenize)
3. Compute TF-IDF vectors untuk setiap paper
4. Save vectors ke pickle cache

**Query Parameters:**
- `batch_size` (int, default: 100) - Jumlah papers per batch

**Headers:**
- `Authorization: Bearer <admin_token>` (required)

**Example:**
```bash
curl -X POST \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  "http://localhost:8000/api/v1/vectorize-all-papers?batch_size=100"
```

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "Vectorization complete",
  "papers_processed": 500,
  "cache_size_mb": 45.2
}
```

---

#### GET /cache/status
Check vectorization cache status (public)

**Response (200 OK):**
```json
{
  "cache_valid": true,
  "cache_size_mb": 45.2,
  "total_papers": 500,
  "last_updated": "2024-06-12T10:30:00Z",
  "cache_hits": 234,
  "cache_misses": 12
}
```

---

#### DELETE /cache/clear
Clear vectorization cache (Admin only)

**Headers:**
- `Authorization: Bearer <admin_token>`

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "Cache cleared successfully"
}
```

---

### 👤 Auth Endpoints

#### POST /login
User login, dapatkan JWT token

**Request Body:**
```json
{
  "username": "myuser",
  "password": "mypassword123"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user_id": 1,
  "username": "myuser"
}
```

---

#### POST /register
User registration

**Request Body:**
```json
{
  "username": "newuser",
  "password": "securepass123"
}
```

**Response (201 Created):**
```json
{
  "status": "success",
  "message": "User registered successfully",
  "user_id": 5
}
```

---

### 💬 Feedback Endpoints

#### POST /feedbacks
Submit feedback untuk rekomendasi

**Request Body:**
```json
{
  "paper_id": 2,
  "response": 1
}
```

Dimana `response` values:
- `1` = Like / Relevant
- `0` = Neutral
- `-1` = Dislike / Not Relevant

**Headers:**
- `Authorization: Bearer <token>` (required)

**Response (201 Created):**
```json
{
  "status": "success",
  "feedback_id": 10
}
```

---

#### GET /feedbacks
Get user feedbacks

**Headers:**
- `Authorization: Bearer <token>`

**Response (200 OK):**
```json
{
  "status": "success",
  "data": [
    {
      "id": 10,
      "paper_id": 2,
      "response": 1,
      "created_at": "2024-06-12T10:30:00"
    }
  ]
}
```

---

### 📊 Evaluation Endpoints

#### GET /eval-results
Get evaluation results untuk recommendations

**Query Parameters:**
- `user_id` (int, optional) - Filter by specific user
- `limit` (int, default: 100)

**Response (200 OK):**
```json
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "user_id": 1,
      "paper_id": 2,
      "precision_at_k": 0.80,
      "recall_at_k": 0.75,
      "ndcg_at_k": 0.82,
      "map_at_k": 0.78,
      "created_at": "2024-06-12T10:30:00"
    }
  ]
}
```

---

### 🔐 Admin Endpoints

#### POST /admin/login
Admin login

**Request Body:**
```json
{
  "username": "admin",
  "password": "adminpass123"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "admin_id": 1
}
```

---

## 🚀 Cara Menggunakan

### Workflow Lengkap

#### 1️⃣ Register User Baru

```bash
curl -X POST "http://localhost:8000/api/v1/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "myuser",
    "password": "securepass123"
  }'
```

**Response:**
```json
{
  "status": "success",
  "message": "User registered successfully",
  "user_id": 5
}
```

---

#### 2️⃣ Login & Dapatkan Token

```bash
curl -X POST "http://localhost:8000/api/v1/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "myuser",
    "password": "securepass123"
  }'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1IiwiaWF0IjoxNzE4MTcwNjAwfQ.abcdef...",
  "token_type": "bearer",
  "user_id": 5
}
```

Simpan nilai `access_token` untuk request berikutnya.

---

#### 3️⃣ Get Papers

```bash
curl -X GET "http://localhost:8000/api/v1/papers?limit=5&sort=newest"
```

**Response:**
```json
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "title": "Attention Is All You Need",
      "abstract": "The dominant sequence transduction models...",
      "published_date": "2017-06-12",
      "category": "cs.CL",
      "author": "Vaswani et al.",
      "url": "https://arxiv.org/abs/1706.03762"
    },
    // ... more papers
  ]
}
```

Pilih satu paper untuk dijadikan seed recommendation.

---

#### 4️⃣ Get Recommendations

```bash
TOKEN="YOUR_ACCESS_TOKEN_HERE"

curl -X GET "http://localhost:8000/api/v1/recommend/1?top_n=5" \
  -H "Authorization: Bearer $TOKEN"
```

**Response:**
```json
{
  "status": "success",
  "data": [
    {
      "rank": 1,
      "paper_id": 2,
      "title": "Transformer Models for NLP",
      "cbf_score": 0.87,
      "ucb_score": 0.91
    },
    {
      "rank": 2,
      "paper_id": 5,
      "title": "Deep Learning Optimization",
      "cbf_score": 0.82,
      "ucb_score": 0.88
    },
    // ... more recommendations
  ]
}
```

**Interpretasi:**
- Rank 1 = Top recommendation (highest UCB score)
- UCB score = Combined score dari CBF + feedback from other users
- CBF score = Content similarity dengan seed paper

---

#### 5️⃣ Submit Feedback

```bash
TOKEN="YOUR_ACCESS_TOKEN_HERE"

curl -X POST "http://localhost:8000/api/v1/feedbacks" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "paper_id": 2,
    "response": 1
  }'
```

Kirim feedback untuk setiap recommended paper yang Anda lihat:
- `1` = Relevant/Like
- `0` = Neutral
- `-1` = Not Relevant/Dislike

Feedback ini akan:
1. Digunakan untuk UCB ranking pada future recommendations
2. Berkontribusi pada evaluation metrics (Precision, Recall, NDCG)

---

#### 6️⃣ Check Evaluation Metrics

```bash
TOKEN="YOUR_ACCESS_TOKEN_HERE"

curl -X GET "http://localhost:8000/api/v1/eval-results?user_id=5" \
  -H "Authorization: Bearer $TOKEN"
```

**Response:**
```json
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "user_id": 5,
      "paper_id": 1,
      "precision_at_k": 0.80,
      "recall_at_k": 0.75,
      "ndcg_at_k": 0.82,
      "map_at_k": 0.78,
      "created_at": "2024-06-12T10:30:00"
    }
  ]
}
```

Metrics:
- **Precision@5** = Dari 5 recommendations, berapa % yang user like
- **Recall@5** = Dari semua papers yang user like, berapa % yang ada di top 5 recommendations
- **NDCG@5** = Ranking quality score (0-1)
- **MAP@5** = Mean average precision

---

### Admin Workflow

#### Admin Login

```bash
curl -X POST "http://localhost:8000/api/v1/admin/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "adminpass"
  }'
```

---

#### Vectorize Semua Papers (First Time Setup)

```bash
ADMIN_TOKEN="ADMIN_ACCESS_TOKEN_HERE"

curl -X POST \
  "http://localhost:8000/api/v1/vectorize-all-papers?batch_size=100" \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

Process ini:
- Load 100 papers per batch dari database
- Compute TF-IDF vectors untuk setiap abstract
- Save vectors ke pickle cache di `app/cache/vectorization/`
- Improve recommendation speed 10-100x

---

#### Check Cache Status

```bash
curl -X GET "http://localhost:8000/api/v1/cache/status"
```

**Response:**
```json
{
  "cache_valid": true,
  "cache_size_mb": 45.2,
  "total_papers": 500,
  "last_updated": "2024-06-12T10:30:00Z"
}
```

---

#### Clear Cache (jika perlu rebuild)

```bash
ADMIN_TOKEN="ADMIN_ACCESS_TOKEN_HERE"

curl -X DELETE "http://localhost:8000/api/v1/cache/clear" \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

---

### Advanced: Term Frequency Calculation

Script untuk analyze term frequency dari abstracts:

```bash
# Run TF calculator
python app/utils/tf_calculator.py
```

Output: `tf_results.csv` dengan frequency setiap term

---

## ⚙️ Configuration

### Environment Variables (.env)

```env
# MySQL Database Configuration
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DB=arxivinder

# Optional: Ngrok Tunneling
NGROK_AUTH_TOKEN=your_ngrok_token_here
```

### CORS Configuration

Edit `app/main.py` untuk allow additional origins:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",      # React frontend (dev)
        "http://127.0.0.1:5173",
        "https://yourdomain.com",     # Production domain
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 🐛 Troubleshooting

### Problem: Database Connection Failed

**Error:**
```
pymysql.err.OperationalError: (2003, "Can't connect to MySQL server")
```

**Solution:**
1. Pastikan MySQL server running
   ```bash
   # Windows (check services)
   # macOS
   brew services list | grep mysql
   # Linux
   systemctl status mysql
   ```

2. Verify konfigurasi `.env`
   ```bash
   # Test connection
   mysql -u root -p -h localhost -P 3306
   ```

3. Check firewall & network settings

---

### Problem: JWT Token Invalid/Expired

**Error:**
```
HTTPException 403: Could not validate credentials
```

**Solution:**
1. Pastikan token di header: `Authorization: Bearer <token>`
2. Token expired (24 hours)? Login ulang untuk token baru
3. Check user exist: `SELECT * FROM users WHERE id = <user_id>;`

---

### Problem: Papers Not Found

**Error:**
```
404 Paper not found
```

**Solution:**
1. Insert papers dulu:
   ```bash
   curl -X POST "http://localhost:8000/api/v1/papers" \
     -H "Content-Type: application/json" \
     -d '{...}'
   ```

2. Check table exists:
   ```bash
   mysql -u root -p arxivinder
   SHOW TABLES;
   ```

3. Run migrations:
   ```bash
   alembic upgrade head
   ```

---

### Problem: Cache Not Found

**Error:**
```
FileNotFoundError: [Errno 2] No such file or directory: 'app/cache/vectorization/...'
```

**Solution:**
1. Trigger vectorization:
   ```bash
   curl -X POST "http://localhost:8000/api/v1/vectorize-all-papers" \
     -H "Authorization: Bearer $ADMIN_TOKEN"
   ```

2. Check folder permissions:
   ```bash
   # Linux/macOS
   chmod -R 755 app/cache/
   ```

3. Clear & rebuild cache:
   ```bash
   # DELETE /api/v1/cache/clear
   # Then POST /api/v1/vectorize-all-papers
   ```

---

### Problem: Module Not Found

**Error:**
```
ModuleNotFoundError: No module named 'app'
```

**Solution:**
1. Pastikan di root directory:
   ```bash
   cd /path/to/backend_model
   pwd  # Verify location
   ```

2. Activate virtual environment:
   ```bash
   # Windows
   .venv\Scripts\activate
   
   # macOS/Linux
   source .venv/bin/activate
   ```

3. Reinstall dependencies:
   ```bash
   pip install --upgrade -r requirements.txt
   ```

4. Check Python path:
   ```bash
   python -c "import sys; print(sys.path)"
   ```

---

### Problem: Port Already in Use

**Error:**
```
OSError: [Errno 48] Address already in use
```

**Solution:**
1. Change port:
   ```bash
   uvicorn app.main:app --port 8001
   ```

2. Kill existing process:
   ```bash
   # Windows
   netstat -ano | findstr :8000
   taskkill /PID <PID> /F
   
   # macOS/Linux
   lsof -i :8000
   kill -9 <PID>
   ```

---

## 📞 Support & Resources

### Documentation Files
- `README_ASYNC_VECTORIZATION.txt` - Async vectorization guide
- `QUICK_START.md` - Quick start guide
- `CURL_EXAMPLES.sh` - API call examples
- `CLI_EXAMPLES.md` - CLI usage examples

### Database Migrations
View migration history:
```bash
alembic history
```

### Testing
```bash
# Test cache endpoints
python test_cache_endpoints.py
```

---

## 📝 License

MIT License - Free to use and modify

---

## 👨‍💼 Authors

- **Arxivinder Team**
- **Contact:** mrlaksana99@gmail.com
- **Repository:** https://github.com/arxi-vinder/backend_model

---

**Last Updated:** June 12, 2026 
**Version:** 1.0.0  
**Status:** Production Ready
