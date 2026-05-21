# CLI Usage Examples

Contoh-contoh praktis penggunaan vectorization CLI.

## 📌 Scenario 1: First Time Vectorization

**Situation:** Database baru punya 500 papers, belum ada cache

**Steps:**

```bash
# 1. Check database status
python -m app.cli status

# Output:
# [DB] Database:
#    - Total papers: 500
# [CACHE] Cache:
#    Status: NOT CACHED

# 2. Start vectorization
python -m app.cli vectorize-all

# Output akan show:
# [RUN] Starting vectorization with batch size: 100...
# Processing batch: 1 - 100
# Processing batch: 101 - 200
# Processing batch: 201 - 300
# Processing batch: 301 - 400
# Processing batch: 401 - 500
# Progress: 100.0%
# [DONE] Vectorization completed successfully!
# [STATS] Final Cache Status:
#    - Total papers: 500
#    - Matrix size: 500x500
#    - File size: 12.45 MB

# 3. Verify cache
python -m app.cli cache-info

# Output:
# [CACHE] Cache Information
# [OK] Cache Status: CACHED
#   - Total papers: 500
#   - Matrix size: 500x500
#   - File size: 12.45 MB
#   - Last saved: 2026-05-17T17:20:30.123456
#   - Cache location: app/cache/vectorization/precomputed_vectors.pkl
```

**Time:** ~5 minutes for 500 papers

---

## 📌 Scenario 2: Added New Papers (Re-Vectorize)

**Situation:** Database sudah punya 500 papers dengan cache, tambah 200 papers baru

**Steps:**

```bash
# 1. Check current status
python -m app.cli status

# Output:
# [DB] Database:
#    - Total papers: 700 (old 500 + new 200)
# [CACHE] Cache:
#    Status: CACHED [OK]
#    - Papers cached: 500 (outdated!)
#    - Matrix size: 500x500

# 2. Option A: Ask user confirmation (recommended)
python -m app.cli vectorize-all

# Output:
# [CACHE] Cache already exists:
#    - Papers cached: 500
#    - Cache file size: 12.45 MB
#    - Last updated: 2026-05-17T17:20:30.123456
#
# [ASK] Do you want to re-vectorize anyway? [y/N]: y
# [OK] Proceeding with re-vectorization...
# [RUN] Starting vectorization with batch size: 100...
# ... (vectorization progress)
# [DONE] Vectorization completed successfully!
# [STATS] Final Cache Status:
#    - Total papers: 700
#    - Matrix size: 700x700
#    - File size: 19.87 MB

# 3. Option B: Force re-vectorize (skip confirmation)
python -m app.cli vectorize-all --force

# Akan langsung mulai vectorization tanpa ask
```

**Time:** ~7-8 minutes for all 700 papers

---

## 📌 Scenario 3: Memory Issues (Small Batch Size)

**Situation:** Machine hanya punya 2GB RAM, vectorization crash

**Steps:**

```bash
# 1. Clear cache first
python -m app.cli clear-cache

# Confirmation:
# Are you sure you want to clear the cache? This cannot be undone. [y/N]: y
# [DONE] Cache cleared successfully!

# 2. Vectorize dengan batch size lebih kecil
python -m app.cli vectorize-all --batch-size 50

# Output:
# [RUN] Starting vectorization with batch size: 50...
# Processing batch: 1 - 50
# Processing batch: 51 - 100
# Processing batch: 101 - 150
# ... (lebih lambat tapi less memory intensive)
# [DONE] Vectorization completed successfully!

# Batch size 50 akan gunakan ~100-150MB memory
# vs batch size 100 yang gunakan ~300MB
```

**Tips:**
- Start with `--batch-size 50` untuk machines dengan memory terbatas
- Monitor memory usage selama process
- Jika masih crash, coba `--batch-size 25`

---

## 📌 Scenario 4: Quick Status Check During Work

**Situation:** Ingin cek apakah cache valid sebelum mulai development

**Steps:**

```bash
# Quick one-liner untuk check status
python -m app.cli cache-info

# Output:
# [CACHE] Cache Information
# [OK] Cache Status: CACHED
#   - Total papers: 1287
#   - Matrix size: 1287x1287
#   - File size: 17.38 MB
#   - Last saved: 2026-05-17T17:11:55.785822
#   - Cache location: app/cache/vectorization/precomputed_vectors.pkl

# If cache is not valid:
# No cache found. Run 'python -m app.cli vectorize-all' to create cache.
```

---

## 📌 Scenario 5: Using Windows Batch Script

**Situation:** Team member hanya comfortable dengan GUI clicks

**Steps:**

```bash
# 1. Double-click vectorize.bat

# Akan open terminal dengan menu:
# ============================================================
# Arxivinder Vectorization Tool
# ============================================================
#
# Select an option:
# 1. Vectorize all papers (default batch size 100)
# 2. Vectorize all papers (custom batch size)
# 3. Check cache info
# 4. Check vectorization status
# 5. Clear cache
# 6. Exit
#
# Enter your choice (1-6): 1

# 2. Input: 1
# (akan run default vectorization)

# 3. Input: 3
# (check cache info)

# 4. Input: 6
# (exit)
```

**Advantage:** No need untuk remember command syntax

---

## 📌 Scenario 6: Cron Job (Automatic Re-vectorization)

**Situation:** Ingin auto re-vectorize setiap malam

**Windows Task Scheduler:**

```batch
# Create batch file: vectorize_nightly.bat
@echo off
cd d:\Projects\Arxivinder\backend_model
python -m app.cli vectorize-all --force >> logs/vectorization.log 2>&1
```

Kemudian schedule di Windows Task Scheduler untuk run setiap malam jam 2 pagi.

**Linux Crontab:**

```bash
# Add to crontab: crontab -e
0 2 * * * cd /home/user/arxivinder/backend_model && python -m app.cli vectorize-all --force >> logs/vectorization.log 2>&1
```

---

## 📌 Scenario 7: Debug Failed Vectorization

**Situation:** Vectorization error di tengah process

**Steps:**

```bash
# 1. Check database connection
python -m app.cli status

# If error:
# [ERROR] Error: 'NoneType' object has no attribute 'get_total_papers_count'
# → Database connection failed, check .env

# 2. Verify database directly
python -c "from app.db.database import SessionLocal; db = SessionLocal(); print('Connected!')"

# 3. If database OK, check cache
python -m app.cli cache-info

# 4. Clear potentially corrupted cache
python -m app.cli clear-cache

# 5. Retry vectorization
python -m app.cli vectorize-all --batch-size 50
```

---

## 📌 Scenario 8: Integration Test (API + Cache)

**Situation:** Test bahwa recommendation API properly menggunakan cache

**Steps:**

```bash
# 1. Ensure cache is valid
python -m app.cli status

# 2. Start API server
python -m app.server

# 3. In another terminal, test recommendation
curl http://localhost:8000/api/recommendations/papers/1?top_n=5

# Response should be fast (< 100ms) if using cache

# 4. Check API logs
# Should see something like:
# [CACHE] Trying to load precomputed vectors...
# [OK] Vectors loaded from cache!
# Model loaded from cache: 1287 papers
```

**If cache NOT used:**
- Might take 30+ seconds
- API logs show "No cache found, building default model (100 papers)"

---

## 📌 Scenario 9: Production Deployment Checklist

**Before Going Live:**

```bash
# 1. Test vectorization dengan expected data volume
python -m app.cli status
# Ensure total_papers matches production data

# 2. Vectorize all data
python -m app.cli vectorize-all

# 3. Verify cache integrity
python -m app.cli cache-info
# Check file size is reasonable (not too small)

# 4. Test API with recommendations
curl http://localhost:8000/api/recommendations/papers/1?top_n=5

# 5. Check response time
time curl http://localhost:8000/api/recommendations/papers/1?top_n=5

# Should be < 500ms with cache

# 6. Commit cache files to version control
git add app/cache/vectorization/
git commit -m "chore: add precomputed vectors cache"

# 7. Deploy!
```

---

## 📌 Scenario 10: Troubleshooting Slow Vectorization

**Situation:** Vectorization lebih lambat dari expected

**Steps:**

```bash
# 1. Check system resources
# Windows: Check Task Manager - Memory, CPU, Disk usage
# Linux: top, htop, df -h

# 2. Try dengan batch size lebih besar
python -m app.cli clear-cache
python -m app.cli vectorize-all --batch-size 200

# Lebih besar batch size = lebih cepat (jika memory allow)

# 3. Check database performance
# Test query speed:
python -c "
from app.db.database import SessionLocal
from app.repositories.paper_repository import PaperRepository
import time

db = SessionLocal()
repo = PaperRepository(db)
start = time.time()
papers = repo.get_abstracts_batch(0, 100)
end = time.time()
print(f'Query time: {(end-start)*1000:.2f}ms for 100 papers')
"

# If query time > 1000ms, database might be slow

# 4. Disable SQL echo for faster execution
# Edit app/db/database.py:
# engine = create_engine(DATABASE_URL, echo=False)  # was echo=True
```

---

## 📊 Typical Command Combinations

### Daily Check
```bash
python -m app.cli status
```

### After New Data Import
```bash
python -m app.cli vectorize-all
```

### Before Production Deploy
```bash
python -m app.cli status
python -m app.cli cache-info
```

### Fix Cache Corruption
```bash
python -m app.cli clear-cache
python -m app.cli vectorize-all --batch-size 50
```

### Optimize for Large Dataset
```bash
python -m app.cli vectorize-all --batch-size 200
python -m app.cli cache-info
```

---

## 🎯 Common Command Snippets

**Paste and use:**

```bash
# Full workflow
python -m app.cli status && \
python -m app.cli vectorize-all && \
python -m app.cli cache-info

# Quick re-vectorize (force)
python -m app.cli vectorize-all --force

# Conservative (small batches)
python -m app.cli clear-cache && \
python -m app.cli vectorize-all --batch-size 50

# Aggressive (large batches, faster)
python -m app.cli vectorize-all --batch-size 200 --force
```

---

## 📞 Need Help?

- **CLI Help:** `python -m app.cli --help`
- **Command Help:** `python -m app.cli vectorize-all --help`
- **See Full Docs:** Check `VECTORIZATION_CLI.md`
- **See Quick Ref:** Check `VECTORIZATION_QUICKSTART.md`
