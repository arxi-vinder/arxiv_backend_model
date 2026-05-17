# Arxivinder Vectorization CLI Guide

Terminal CLI untuk melakukan vectorization semua papers dan manage cache vectorization.

## 📋 Requirements

- Python 3.8+
- Semua dependencies di `requirements.txt` sudah terinstall (terutama `click`)
- Database MySQL sudah berjalan dan terhubung dengan `.env` configuration

## 🚀 Quick Start

### 1. Setup Environment

Pastikan `.env` file sudah dikonfigurasi dengan database credentials:

```env
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DB=arxivinder
MYSQL_USER=root
MYSQL_PASSWORD=your_password
```

### 2. Navigate to Project Directory

```bash
cd d:\Projects\Arxivinder\backend_model
```

### 3. Run CLI Commands

## 📊 Available Commands

### Vectorize All Papers (Main Command)

**Full vectorization dari semua papers di database**

```bash
python -m app.cli vectorize-all
```

**Options:**
- `--batch-size` (default: 100): Jumlah papers yang diproses per batch
- `--force`: Bypass cache check dan langsung vectorize ulang

**Examples:**

```bash
# Vectorize dengan batch size 100 (default)
python -m app.cli vectorize-all

# Vectorize dengan batch size yang lebih kecil (hemat memory)
python -m app.cli vectorize-all --batch-size 50

# Force re-vectorization meskipun cache sudah ada
python -m app.cli vectorize-all --force
```

**Output:**
```
============================================================
🚀 Starting Paper Vectorization Process
============================================================

📊 Total papers in database: 1000
💾 Cache already exists:
   - Papers cached: 800
   - Cache file size: 125.45 MB
   - Last updated: 2026-05-17T10:30:45.123456

❓ Do you want to re-vectorize anyway? [y/N]: y
✓ Proceeding with re-vectorization...

⏳ Starting vectorization with batch size: 100...
============================================================
Processing batch: 1 - 100
Processing batch: 101 - 200
...
Progress: 50.0%
Progress: 100.0%

============================================================
✅ Vectorization completed successfully!

📈 Final Cache Status:
   - Total papers: 1000
   - Matrix size: 1000x1000
   - File size: 156.78 MB
   - Location: app/cache/vectorization/precomputed_vectors.pkl
```

### Check Cache Info

**Lihat informasi cache yang tersedia**

```bash
python -m app.cli cache-info
```

**Output:**
```
============================================================
💾 Cache Information
============================================================
✓ Cache Status: CACHED
  - Total papers: 1000
  - Matrix size: 1000x1000
  - File size: 156.78 MB
  - Last saved: 2026-05-17T10:35:20.654321
  - Cache location: app/cache/vectorization/precomputed_vectors.pkl
```

### Check Vectorization Status

**Lihat status keseluruhan vectorization**

```bash
python -m app.cli status
```

**Output:**
```
============================================================
📊 Vectorization Status
============================================================

📁 Database:
   - Total papers: 1000

💾 Cache:
   Status: CACHED ✓
   - Papers cached: 1000
   - Matrix size: 1000x1000
   - File size: 156.78 MB
   - Last updated: 2026-05-17T10:35:20.654321

============================================================
```

### Clear Cache

**Hapus cache vectorization (PERHATIAN: tidak bisa di-undo)**

```bash
python -m app.cli clear-cache
```

**Confirmation:**
```
Are you sure you want to clear the cache? This cannot be undone. [y/N]: y
✅ Cache cleared successfully!
```

## 📈 Performance Tips

### Batch Size Selection

- **Default (100)**: Cocok untuk database dengan 1000-2000 papers
- **Smaller (50)**: Gunakan jika memory terbatas atau untuk testing
- **Larger (200+)**: Gunakan jika memory cukup untuk accelerate processing

```bash
# Untuk database kecil (< 500 papers)
python -m app.cli vectorize-all --batch-size 50

# Untuk database medium (500-2000 papers)
python -m app.cli vectorize-all --batch-size 100

# Untuk database besar (> 2000 papers)
python -m app.cli vectorize-all --batch-size 200
```

### Expected Times

Waktu vectorization tergantung dari:
- **Jumlah papers**: Linear growth
- **Panjang abstract**: TF-IDF computation time
- **Batch size**: Smaller batches = more I/O, larger = more memory
- **CPU power**: Multi-core processing

**Estimasi:**
- 100 papers: ~30 detik
- 500 papers: ~5 menit
- 1000 papers: ~20 menit
- 2000+ papers: ~1+ jam

## 🔍 Troubleshooting

### Error: "Database connection failed"

**Cause:** .env configuration incorrect atau MySQL tidak running

**Solution:**
1. Check `.env` file sudah ada dan correct
2. Pastikan MySQL service sudah berjalan
3. Test connection:
   ```bash
   python -c "from app.db.database import SessionLocal; db = SessionLocal(); print('Connected!')"
   ```

### Error: "No papers found in database"

**Cause:** Database belum punya papers

**Solution:**
1. Seed database terlebih dahulu:
   ```bash
   python -c "from app.utils.paper_seeder import seed_papers; seed_papers()"
   ```
2. Atau import papers via API endpoint

### Memory Error During Vectorization

**Cause:** Batch size terlalu besar untuk available memory

**Solution:**
1. Stop process dan clear memory
2. Run lagi dengan batch size lebih kecil:
   ```bash
   python -m app.cli vectorize-all --batch-size 50
   ```

### Cache File Corrupted

**Cause:** Cache file (.pkl) rusak atau incomplete

**Solution:**
```bash
# Clear corrupted cache
python -m app.cli clear-cache

# Re-vectorize
python -m app.cli vectorize-all
```

## 📝 Cache Details

### Cache Location
```
app/cache/vectorization/
├── precomputed_vectors.pkl    # Binary vectors cache
└── metadata.json              # Cache metadata
```

### Cache Contents

**precomputed_vectors.pkl** berisi:
- `datas`: List of papers dengan id, title, abstract
- `tfidf_vectors`: TF-IDF vectors untuk setiap paper
- `cosine_matrix`: Precomputed cosine similarity matrix

**metadata.json**:
```json
{
  "total_papers": 1000,
  "matrix_size": 1000,
  "saved_at": "2026-05-17T10:35:20.654321",
  "cache_file": "app/cache/vectorization/precomputed_vectors.pkl"
}
```

## 🔗 Integration dengan API

Recommendation API secara otomatis akan:
1. Check apakah cache ada
2. Load vectors dari cache jika valid
3. Use untuk quick recommendation lookup

Tidak perlu manual setup - semuanya automatic!

## 📞 Support

Jika ada pertanyaan atau issues:
1. Check logs di console output
2. Enable debug logging dengan set `LOG_LEVEL=DEBUG` di .env
3. Check database connection

## 🎯 Next Steps

Setelah vectorization selesai:

1. **Test Recommendations:**
   ```bash
   # Via API (setelah server running)
   curl http://localhost:8000/api/recommendations/papers/1?top_n=5
   ```

2. **Monitor Cache Usage:**
   ```bash
   python -m app.cli cache-info
   ```

3. **Update Papers:**
   Jika ada papers baru, jalankan ulang:
   ```bash
   python -m app.cli vectorize-all --force
   ```
