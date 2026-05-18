# Cache & Vectorization API Endpoints

Dokumentasi lengkap untuk semua endpoint cache dan vectorization yang tersedia di API, equivalent dengan CLI commands.

## 📋 Ringkasan Endpoints

| CLI Command | Endpoint | Method | Authentication | Deskripsi |
|-----------|----------|--------|-----------------|-----------|
| `cache-info` | `/api/v1/cache/info` | GET | Tidak | Lihat informasi cache detail |
| `status` | `/api/v1/vectorization/status` | GET | Ya | Lihat status lengkap DB + Cache |
| `vectorize-all` | `/api/v1/vectorize-all-papers` | POST | Tidak | Vectorize semua papers (batch) |
| `clear_cache` | `/api/v1/cache/clear` | DELETE | Ya | Hapus cache |
| Recommendation | `/api/v1/recommend/{paper_id}` | GET | Ya | Get recommendations |
| UCB Refresh | `/api/v1/recommend/{paper_id}/refresh-ucb` | POST | Ya | Refresh UCB scores |

---

## 🔍 Endpoint Details

### 1. **GET `/api/v1/cache/info`** - Cache Information
Equivalent dengan CLI command: `python -m app.cli cache-info`

**Deskripsi:**
Menampilkan informasi detail tentang cache yang sudah dibuat, termasuk jumlah papers, ukuran matrix, dan file size.

**Parameter:** Tidak ada

**Example Request:**
```bash
curl -X GET "http://localhost:8000/api/v1/cache/info"
```

**Example Response (Cache Exists):**
```json
{
  "status": "success",
  "cache_status": "cached",
  "message": "Cache is available",
  "data": {
    "total_papers": 5000,
    "matrix_size": "5000x5000",
    "file_size_mb": 245.67,
    "last_saved": "2026-05-18T10:30:45.123456",
    "cache_location": "app/cache/vectorization/precomputed_vectors.pkl"
  }
}
```

**Example Response (No Cache):**
```json
{
  "status": "success",
  "cache_status": "no_cache",
  "message": "No cache found. Run vectorization to create cache.",
  "data": null
}
```

---

### 2. **GET `/api/v1/vectorization/status`** - Full Vectorization Status
Equivalent dengan CLI command: `python -m app.cli status`

**Deskripsi:**
Menampilkan status lengkap, termasuk total papers di database dan informasi cache.

**Parameter:**
- `current_user` (optional, auto dari header): User yang authenticated

**Example Request:**
```bash
# Dengan authentication
curl -X GET "http://localhost:8000/api/v1/vectorization/status" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Tanpa authentication (jika diizinkan)
curl -X GET "http://localhost:8000/api/v1/vectorization/status"
```

**Example Response:**
```json
{
  "status": "success",
  "database": {
    "total_papers_in_db": 5000
  },
  "cache": {
    "status": "cached",
    "message": "Cache is available",
    "data": {
      "papers_cached": 5000,
      "matrix_size": "5000x5000",
      "file_size_mb": 245.67,
      "last_updated": "2026-05-18T10:30:45.123456",
      "cache_location": "app/cache/vectorization/precomputed_vectors.pkl"
    }
  }
}
```

---

### 3. **POST `/api/v1/vectorize-all-papers`** - Vectorize All Papers
Equivalent dengan CLI command: `python -m app.cli vectorize-all`

**Deskripsi:**
Melakukan vectorization untuk semua papers dalam database dengan batch processing. Proses ini akan:
- Memproses semua papers (bukan hanya 100)
- Menggunakan batch preprocessing untuk efisiensi memory
- Pre-compute vectors dan simpan ke cache
- Proses bisa memakan waktu lama (8-10 menit untuk 5000 papers)

**Parameter:**
- `batch_size` (query, integer): Ukuran batch untuk processing (default: 100)

**Example Request:**
```bash
# Dengan batch size custom
curl -X POST "http://localhost:8000/api/v1/vectorize-all-papers?batch_size=100"

# Dengan default batch size
curl -X POST "http://localhost:8000/api/v1/vectorize-all-papers"
```

**Example Response:**
```json
{
  "status": "success",
  "message": "Full vectorization completed and cached successfully",
  "data": {
    "total_papers_processed": 5000,
    "cosine_matrix_size": "5000x5000",
    "batch_size_used": 100,
    "cached": true
  }
}
```

**Error Response:**
```json
{
  "status": "error",
  "error_type": "ValueError",
  "message": "Some papers could not be vectorized",
  "traceback": "..."
}
```

---

### 4. **DELETE `/api/v1/cache/clear`** - Clear Cache
Equivalent dengan CLI command: `python -m app.cli clear-cache`

**Deskripsi:**
Menghapus cache vectorization. Operasi ini tidak bisa dibatalkan, jadi pastikan sudah yakin sebelum menjalankan.

**Parameter:**
- `current_user` (required, auto dari header): User yang authenticated (untuk security)

**Example Request:**
```bash
curl -X DELETE "http://localhost:8000/api/v1/cache/clear" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Example Response:**
```json
{
  "status": "success",
  "message": "Cache cleared successfully"
}
```

**Error Response:**
```json
{
  "status": "error",
  "message": "Failed to clear cache"
}
```

---

### 5. **GET `/api/v1/cache/status`** - Quick Cache Status Check
Equivalent dengan CLI: `cache_info.get("status")`

**Deskripsi:**
Pengecekan cepat status cache. Format response sama seperti `/cache/info`.

**Parameter:**
- `current_user` (required): User yang authenticated

**Example Request:**
```bash
curl -X GET "http://localhost:8000/api/v1/cache/status" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Example Response:**
```json
{
  "status": "success",
  "data": {
    "status": "cached",
    "total_papers": 5000,
    "matrix_size": 5000,
    "file_size_mb": 245.67,
    "saved_at": "2026-05-18T10:30:45.123456",
    "cache_file": "app/cache/vectorization/precomputed_vectors.pkl"
  }
}
```

---

## 🚀 Usage Examples

### Scenario 1: Check apakah cache sudah ada
```bash
# Cek status cache
curl -X GET "http://localhost:8000/api/v1/cache/info"

# Response akan menunjukkan apakah cache sudah ada atau tidak
```

### Scenario 2: Vectorize all papers jika cache belum ada
```bash
# 1. Cek status
curl -X GET "http://localhost:8000/api/v1/vectorization/status"

# 2. Jika cache tidak ada, jalankan vectorization
curl -X POST "http://localhost:8000/api/v1/vectorize-all-papers?batch_size=100"

# 3. Tunggu process selesai (bisa memakan waktu lama)
# 4. Cek status lagi untuk confirm cache sudah berhasil dibuat
curl -X GET "http://localhost:8000/api/v1/cache/info"
```

### Scenario 3: Get recommendations setelah cache siap
```bash
# 1. Pastikan cache sudah ada
curl -X GET "http://localhost:8000/api/v1/cache/info"

# 2. Get recommendations untuk paper tertentu
curl -X GET "http://localhost:8000/api/v1/recommend/123?top_n=5" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 3. Optional: Refresh UCB scores berdasarkan feedback terbaru
curl -X POST "http://localhost:8000/api/v1/recommend/123/refresh-ucb?top_n=5" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Scenario 4: Clear cache dan re-vectorize
```bash
# 1. Cek cache info
curl -X GET "http://localhost:8000/api/v1/cache/info"

# 2. Clear cache (harus authenticated)
curl -X DELETE "http://localhost:8000/api/v1/cache/clear" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 3. Re-vectorize
curl -X POST "http://localhost:8000/api/v1/vectorize-all-papers?batch_size=100"

# 4. Wait and verify
curl -X GET "http://localhost:8000/api/v1/cache/info"
```

---

## 📝 Notes

1. **Vectorization adalah process berat**: Proses vectorization untuk semua papers bisa memakan waktu 5-15 menit tergantung jumlah papers dan spesifikasi hardware.

2. **Cache File Location**: Cache disimpan di `app/cache/vectorization/` dengan dua file:
   - `precomputed_vectors.pkl`: File pickle yang berisi vectors dan cosine matrix
   - `metadata.json`: File JSON berisi metadata cache

3. **Memory Consideration**: Vectorization menggunakan batch processing untuk menghindari memory overflow. Ukuran batch default adalah 100, bisa disesuaikan sesuai kapasitas server.

4. **Authentication**: 
   - `/cache/info` dan `/vectorize-all-papers` dapat diakses tanpa authentication
   - `/vectorization/status` (opsional authentication)
   - `/cache/clear`, `/cache/status`, `/recommend/*` memerlukan authentication

5. **Error Handling**: Semua endpoint akan mengembalikan error detail jika terjadi masalah, termasuk error type dan traceback untuk debugging.

---

## 🔄 Workflow Recommendations

### First Time Setup:
```
1. GET /cache/info → check apakah cache sudah ada
2. POST /vectorize-all-papers → jika belum ada, buat cache
3. GET /cache/info → verify cache berhasil dibuat
4. GET /recommend/{paper_id} → mulai gunakan recommendations
```

### Daily Operations:
```
1. GET /vectorization/status → check system status
2. GET /recommend/{paper_id} → get recommendations
3. POST /recommend/{paper_id}/refresh-ucb → update scores jika diperlukan
```

### Maintenance:
```
1. GET /cache/info → monitor cache size
2. DELETE /cache/clear → jika cache korup atau ingin reset
3. POST /vectorize-all-papers → rebuild cache
```

---

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| "No cache found" | Jalankan `POST /vectorize-all-papers` untuk membuat cache |
| Cache cleared tapi error | Cek permissions pada folder `app/cache/` |
| Vectorization timeout | Kurangi batch size atau check server resources |
| Recommendation lambat | Cek ukuran cache, mungkin perlu re-vectorize |

---

**Last Updated:** 2026-05-18  
**Author:** Arxivinder Backend Team
