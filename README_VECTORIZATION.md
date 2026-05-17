# Arxivinder Vectorization CLI - Complete Guide

## 🎯 Overview

Complete command-line tool untuk vectorize semua papers di database dan manage cache. **Tidak perlu endpoint, semua berjalan dari terminal!**

---

## 🚀 Quick Start (30 Seconds)

### Windows
```bash
vectorize.bat
```
Pilih option dari menu.

### Linux/Mac
```bash
bash vectorize.sh
```
Pilih option dari menu.

### Direct (Any OS)
```bash
python -m app.cli vectorize-all
```

---

## 📚 Documentation Files

| File | Purpose |
|------|---------|
| **README_VECTORIZATION.md** | File ini - complete overview |
| **VECTORIZATION_QUICKSTART.md** | 5-minute quick reference |
| **VECTORIZATION_CLI.md** | Full documentation dengan tips |
| **CLI_EXAMPLES.md** | Practical usage scenarios |
| **CLI_SETUP_SUMMARY.md** | Setup & current status |

**Pick your doc:**
- **New user?** → Start with `VECTORIZATION_QUICKSTART.md`
- **Want all details?** → Read `VECTORIZATION_CLI.md`
- **Need examples?** → Check `CLI_EXAMPLES.md`
- **Setup help?** → See `CLI_SETUP_SUMMARY.md`

---

## 📋 Available Commands

### 1️⃣ Vectorize All Papers

```bash
python -m app.cli vectorize-all [OPTIONS]
```

**Options:**
- `--batch-size INTEGER` - Papers per batch (default: 100)
- `--force` - Skip cache check, force re-vectorize

**Examples:**

```bash
# Standard vectorization
python -m app.cli vectorize-all

# Custom batch size (smaller for limited memory)
python -m app.cli vectorize-all --batch-size 50

# Force re-vectorize (ignore existing cache)
python -m app.cli vectorize-all --force

# Both options combined
python -m app.cli vectorize-all --batch-size 50 --force
```

**What it does:**
1. Loads papers from database in batches
2. Preprocesses abstracts (stemming, stop-word removal)
3. Computes TF-IDF vectors
4. Builds cosine similarity matrix
5. Saves to cache for fast reuse
6. Shows progress indicators

**Output Example:**
```
============================================================
[START] Starting Paper Vectorization Process
============================================================

[INFO] Total papers in database: 1287

[RUN] Starting vectorization with batch size: 100...
------------------------------------------------------------
Processing batch: 1 - 100
Processing batch: 101 - 200
...
Progress: 50.0%
Progress: 100.0%
------------------------------------------------------------

[DONE] Vectorization completed successfully!

[STATS] Final Cache Status:
   - Total papers: 1287
   - Matrix size: 1287x1287
   - File size: 17.38 MB
   - Location: app/cache/vectorization/precomputed_vectors.pkl
```

---

### 2️⃣ Check Cache Info

```bash
python -m app.cli cache-info
```

**Shows:**
- Cache status (CACHED or NOT CACHED)
- Total papers cached
- Matrix dimensions
- File size in MB
- Last update timestamp
- Cache file location

**Output Example:**
```
============================================================
[CACHE] Cache Information
============================================================
[OK] Cache Status: CACHED
  - Total papers: 1287
  - Matrix size: 1287x1287
  - File size: 17.38 MB
  - Last saved: 2026-05-17T17:11:55.785822
  - Cache location: app/cache/vectorization/precomputed_vectors.pkl
```

---

### 3️⃣ Check Vectorization Status

```bash
python -m app.cli status
```

**Shows:**
- Database status
- Total papers count
- Cache status
- Cached papers count
- Complete overview

**Output Example:**
```
============================================================
[STATUS] Vectorization Status
============================================================

[DB] Database:
   - Total papers: 1287

[CACHE] Cache:
   Status: CACHED [OK]
   - Papers cached: 1287
   - Matrix size: 1287x1287
   - File size: 17.38 MB
   - Last updated: 2026-05-17T17:11:55.785822

============================================================
```

---

### 4️⃣ Clear Cache

```bash
python -m app.cli clear-cache
```

**Deletes:**
- Precomputed vectors file
- Cache metadata

**Warning:** Cannot be undone! Will ask for confirmation.

**Output:**
```
Are you sure you want to clear the cache? This cannot be undone. [y/N]: y
[DONE] Cache cleared successfully!
```

---

## ⏱️ Performance & Timing

### Expected Times

Based on database size and batch size:

| Papers | Batch Size | Time | Memory |
|--------|-----------|------|--------|
| 100 | 100 | ~30s | ~100MB |
| 500 | 100 | ~5m | ~300MB |
| 1000 | 100 | ~20m | ~500MB |
| 1287 | 100 | ~30m | ~600MB |
| 2000 | 100 | ~1h+ | ~800MB |

**Batch Size Impact:**

- **Smaller (50):** Slower but less memory
- **Larger (200):** Faster but more memory

```bash
# For limited memory machines
python -m app.cli vectorize-all --batch-size 50

# For powerful machines
python -m app.cli vectorize-all --batch-size 200
```

---

## 🔌 Integration with API

Recommendation API **automatically** uses cache:

```bash
# Start API server
python -m app.server

# Test recommendation (uses cache automatically)
curl http://localhost:8000/api/recommendations/papers/1?top_n=5
```

**Benefits:**
- Instant recommendations (< 100ms)
- No re-computation on each request
- Significant performance improvement

---

## 🛠️ Setup Requirements

### Environment Variables (.env)

```env
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DB=arxiv_db
MYSQL_USER=root
MYSQL_PASSWORD=root
```

### Python Dependencies

All required packages already in `requirements.txt`:
- `click` - CLI framework
- `sqlmodel` - Database ORM
- `nltk` - Text preprocessing
- `scikit-learn` - ML utilities

### Database

MySQL server running with:
- Database created
- Tables initialized
- Papers already imported

---

## 📊 Current Database Status

Last verified: 2026-05-17

```
Total Papers: 1287
Papers with Abstracts: 1287
Cache Status: ✓ CACHED
Cache File Size: 17.38 MB
Matrix Dimensions: 1287 x 1287
```

---

## 🎯 Common Use Cases

### Case 1: First Time Setup
```bash
# Check status
python -m app.cli status

# Vectorize
python -m app.cli vectorize-all

# Verify
python -m app.cli cache-info
```

### Case 2: Added New Papers
```bash
# Re-vectorize (will ask confirmation)
python -m app.cli vectorize-all

# Or force without asking
python -m app.cli vectorize-all --force
```

### Case 3: Limited Memory
```bash
python -m app.cli vectorize-all --batch-size 50
```

### Case 4: Daily Auto-Update
Windows Task Scheduler:
```batch
python -m app.cli vectorize-all --force
```

Linux Cron (nightly at 2am):
```bash
0 2 * * * python -m app.cli vectorize-all --force
```

---

## 🚨 Troubleshooting

### Error: "Database connection failed"
**Solution:**
1. Check `.env` file is correct
2. Ensure MySQL is running
3. Test connection:
```bash
python -c "from app.db.database import SessionLocal; db = SessionLocal(); print('OK')"
```

### Error: "No papers found in database"
**Solution:**
1. Import papers via API or seeder
2. Check database has papers:
```bash
python -c "from app.repositories.paper_repository import PaperRepository; from app.db.database import SessionLocal; db = SessionLocal(); repo = PaperRepository(db); print(f'Papers: {repo.get_total_papers_count()}')"
```

### Error: "Memory error" during vectorization
**Solution:**
1. Use smaller batch size:
```bash
python -m app.cli clear-cache
python -m app.cli vectorize-all --batch-size 25
```

### Cache seems corrupted
**Solution:**
```bash
# Clear and re-vectorize
python -m app.cli clear-cache
python -m app.cli vectorize-all
```

### Vectorization very slow
**Solution:**
1. Check system resources (Task Manager / top)
2. Try larger batch size if memory allows:
```bash
python -m app.cli vectorize-all --batch-size 200 --force
```

---

## 🔐 Cache Details

### Location
```
app/cache/vectorization/
├── precomputed_vectors.pkl    (Binary vectors ~17MB)
└── metadata.json              (Cache info ~1KB)
```

### Contents
- **Paper IDs:** Unique identifiers
- **Titles:** Paper titles
- **Abstracts:** Paper abstracts
- **TF-IDF Vectors:** 1287 vectors for similarity
- **Cosine Matrix:** 1287x1287 similarity scores

### When Cache is Valid
- ✓ Both files exist
- ✓ Metadata is readable
- ✓ File size > 10MB (for large datasets)

---

## 📈 Monitoring & Metrics

### Check cache effectiveness
```bash
# See cache info
python -m app.cli cache-info

# Monitor API response time
time curl http://localhost:8000/api/recommendations/papers/1
```

### Expected response times
- **With cache:** 10-100ms
- **Without cache:** 30-60 seconds (rebuilds model)

---

## 💡 Best Practices

1. **Always check status before development:**
```bash
python -m app.cli status
```

2. **Verify cache after vectorization:**
```bash
python -m app.cli cache-info
```

3. **For new papers, force re-vectorize:**
```bash
python -m app.cli vectorize-all --force
```

4. **Commit cache to version control:**
```bash
git add app/cache/vectorization/
git commit -m "chore: update precomputed vectors"
```

5. **Monitor file size (sanity check):**
- Small dataset (< 500 papers): 2-5 MB
- Medium dataset (500-2000): 5-50 MB
- Large dataset (2000+): 50+ MB

If size is too small or too large, cache might be corrupted.

---

## 🔄 Workflow Example

### Development Workflow
```bash
# 1. Start day
python -m app.cli status

# 2. If cache not valid, vectorize
python -m app.cli vectorize-all

# 3. Start development
python -m app.server

# 4. Test recommendations
curl http://localhost:8000/api/recommendations/papers/1?top_n=5

# 5. End of day
git add app/cache/vectorization/
git commit -m "chore: update cache"
```

### Production Deployment
```bash
# 1. Verify data
python -m app.cli status

# 2. Vectorize all
python -m app.cli vectorize-all

# 3. Check cache integrity
python -m app.cli cache-info

# 4. Test API
curl http://localhost:8000/api/recommendations/papers/1

# 5. Commit & deploy
git add app/cache/vectorization/
git push
```

---

## 🎓 Understanding the Process

### What Happens During Vectorization

1. **Data Loading**
   - Fetches papers from database in batches
   - Extracts abstracts

2. **Text Preprocessing**
   - Converts to lowercase
   - Removes special characters
   - Applies stemming (PorterStemmer)
   - Removes stop words

3. **TF-IDF Computation**
   - Calculates term frequency (TF)
   - Calculates inverse document frequency (IDF)
   - Combines into TF-IDF vectors

4. **Similarity Matrix**
   - Computes cosine similarity between all pairs
   - Creates n × n matrix where n = number of papers

5. **Cache Storage**
   - Saves vectors to pickle file (binary, fast)
   - Saves metadata to JSON file
   - Creates backup for quick loading

### Why Cache Matters

**Without Cache (rebuilds each time):**
- 1287 papers = ~30 minutes
- Each request waits 30 minutes
- Poor user experience

**With Cache (precomputed):**
- Load time = ~100ms
- Instant recommendations
- Great user experience

---

## 📞 Support & Help

### Get CLI Help
```bash
python -m app.cli --help
python -m app.cli vectorize-all --help
```

### Check Logs
CLI outputs:
- `[START]` - Process starting
- `[OK]` - Success
- `[WARN]` - Warning
- `[ERROR]` - Error

### Report Issues
Check:
1. `.env` configuration
2. MySQL connection
3. Database has papers
4. Sufficient disk space

---

## ✨ Features

- ✅ **Batch Processing** - Efficient memory usage
- ✅ **Progress Indicators** - See real-time progress
- ✅ **Cache Management** - Fast reuse of vectors
- ✅ **Cross-Platform** - Windows, Linux, Mac
- ✅ **Interactive Menu** - batch script with menus
- ✅ **Error Handling** - Clear error messages
- ✅ **Logging Support** - Debug logging available
- ✅ **Fast Performance** - Optimized algorithms

---

## 🎉 You're Ready!

**Next Steps:**

1. **Run vectorization:**
```bash
python -m app.cli vectorize-all
```

2. **Check status:**
```bash
python -m app.cli status
```

3. **Start using it:**
```bash
python -m app.server
curl http://localhost:8000/api/recommendations/papers/1
```

---

## 📖 More Documentation

- **Quick Start** → `VECTORIZATION_QUICKSTART.md`
- **Full Guide** → `VECTORIZATION_CLI.md`
- **Practical Examples** → `CLI_EXAMPLES.md`
- **Setup Info** → `CLI_SETUP_SUMMARY.md`

Enjoy using the Vectorization CLI! 🚀
