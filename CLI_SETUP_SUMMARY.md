# CLI Vectorization Setup - Summary

## ✅ What's Ready

CLI tool untuk vectorize semua papers di database dari terminal telah dibuat dan siap digunakan.

### Files Created:

1. **`app/cli.py`** - Main CLI application dengan semua commands
2. **`vectorize.bat`** - Windows batch script untuk menjalankan CLI dengan menu
3. **`vectorize.sh`** - Unix/Linux/Mac shell script dengan menu
4. **`VECTORIZATION_CLI.md`** - Dokumentasi lengkap dengan contoh dan tips
5. **`VECTORIZATION_QUICKSTART.md`** - Quick reference guide
6. **`CLI_SETUP_SUMMARY.md`** - File ini

### Modified Files:

1. **`app/services/vectorization_cache_service.py`** - Removed emojis for Windows compatibility
2. **`app/cli.py`** - Created with 4 main commands

---

## 🚀 Quick Start

### Option 1: Windows (Easiest)

Double-click atau run:
```bash
vectorize.bat
```

Kemudian pilih option dari menu interaktif.

### Option 2: Unix/Linux/Mac

```bash
bash vectorize.sh
```

Kemudian pilih option dari menu interaktif.

### Option 3: Direct Command (Any OS)

```bash
# Navigasi ke project directory terlebih dahulu
cd d:\Projects\Arxivinder\backend_model

# Jalankan salah satu command:
python -m app.cli vectorize-all
python -m app.cli status
python -m app.cli cache-info
python -m app.cli clear-cache
```

---

## 📋 All Available Commands

### 1. Vectorize All Papers

**Main command untuk memproses semua papers dari database**

```bash
# Basic (batch size 100)
python -m app.cli vectorize-all

# Custom batch size
python -m app.cli vectorize-all --batch-size 50

# Force re-vectorization (bypass cache check)
python -m app.cli vectorize-all --force
```

**Output:**
- Progress indicator untuk setiap batch
- Cosine similarity matrix computation progress
- Final cache info dengan file size

**Batch Size Tips:**
- **50**: Untuk memory terbatas atau testing
- **100**: Default, cocok untuk kebanyakan kasus
- **200+**: Untuk memory besar, accelerate processing

### 2. Check Cache Info

**Lihat status cache yang sudah ada**

```bash
python -m app.cli cache-info
```

**Shows:**
- Total papers cached
- Matrix size
- File size in MB
- Last update timestamp
- Cache file location

### 3. Check Vectorization Status

**Overview status database dan cache**

```bash
python -m app.cli status
```

**Shows:**
- Total papers di database
- Cache status
- Papers cached count
- Matrix dimensions
- File size
- Last updated time

### 4. Clear Cache

**Hapus cache (TIDAK BISA DI-UNDO)**

```bash
python -m app.cli clear-cache
```

Akan ask for confirmation sebelum menghapus.

---

## 📊 Current Status (Your Database)

Based on last test:

```
Database Papers: 1287
Cache Status: CACHED [OK]
Papers Cached: 1287
Matrix Size: 1287x1287
Cache File Size: 17.38 MB
Last Updated: 2026-05-17T17:11:55.785822
```

Cache sudah valid dan siap digunakan!

---

## ⚙️ Environment Setup

Pastikan `.env` file sudah configured:

```env
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DB=arxiv_db
MYSQL_USER=root
MYSQL_PASSWORD=root
```

---

## 🔧 Troubleshooting

### Problem: "Database connection failed"
- Check `.env` configuration
- Ensure MySQL is running
- Verify credentials

### Problem: "No papers found in database"
- Database belum punya data
- Gunakan API endpoint atau seeder untuk add papers

### Problem: "Memory error during vectorization"
- Use smaller batch size: `--batch-size 50`
- Or clear unnecessary processes to free memory

### Problem: "Cache corrupted"
- Run: `python -m app.cli clear-cache`
- Then: `python -m app.cli vectorize-all`

---

## 📈 Expected Performance

| Papers | Batch Size | Time | Memory |
|--------|-----------|------|--------|
| 100 | 50 | ~30s | ~100MB |
| 500 | 100 | ~5m | ~300MB |
| 1000 | 100 | ~20m | ~500MB |
| 2000 | 200 | ~1h | ~1GB |

---

## 💡 Best Practices

1. **Check status before vectorizing:**
   ```bash
   python -m app.cli status
   ```

2. **Use appropriate batch size:**
   - Limited memory? Use `--batch-size 50`
   - Powerful machine? Use `--batch-size 200`

3. **Monitor progress:**
   - Cosine similarity computation shows percentage progress
   - Takes longer for larger datasets

4. **Cache management:**
   - Cache is automatically used by API
   - Only clear if corrupted or need full re-vectorization
   - Cache file persists across restarts

5. **For new papers:**
   - Run `vectorize-all --force` to re-vectorize with new papers
   - Or `clear-cache` then `vectorize-all` for fresh start

---

## 🎯 Next Steps

### After Vectorization:

1. **Test with API:**
   ```bash
   # Start API server
   python -m app.server
   
   # In another terminal, test recommendation
   curl http://localhost:8000/api/recommendations/papers/1?top_n=5
   ```

2. **Check cache usage:**
   ```bash
   python -m app.cli cache-info
   ```

3. **Monitor performance:**
   - Check API response times for recommendations
   - Cache dramatically improves lookup speed

---

## 📞 Support

### Debug Mode

Enable debug logging:
```bash
set LOG_LEVEL=DEBUG
python -m app.cli vectorize-all
```

### Check Logs

Logs are printed to console. Important messages:
- `[START]` - Starting process
- `[OK]` - Success
- `[WARN]` - Warning
- `[ERROR]` - Error occurred

---

## 🔐 Cache Details

### Files Location:
```
app/cache/vectorization/
├── precomputed_vectors.pkl    (Binary vectors data)
└── metadata.json              (Cache metadata)
```

### Cache Contents:
- Paper IDs, titles, abstracts
- TF-IDF vectors for each paper
- Cosine similarity matrix (n x n)

### Cache is valid when:
- ✓ Both files exist
- ✓ Metadata is readable
- ✓ File sizes match expected

---

## ✨ Features

- ✓ Batch processing untuk memory efficiency
- ✓ Progress indicators
- ✓ Cache management
- ✓ Windows & Unix compatible
- ✓ Interactive menu (batch files)
- ✓ Clear error messages
- ✓ Logging support
- ✓ No emoji compatibility issues

---

## 🎊 Done!

Vectorization CLI sudah siap digunakan. Pilih salah satu cara untuk menjalankan:

**Windows:**
```bash
vectorize.bat
```

**Unix/Linux/Mac:**
```bash
bash vectorize.sh
```

**Atau direct:**
```bash
python -m app.cli vectorize-all
```

Enjoy! 🎉
