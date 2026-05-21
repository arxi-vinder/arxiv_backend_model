# Vectorization CLI - Quick Start Guide

## 🎯 5 Second Start

**Windows:**
```bash
vectorize.bat
```

**Linux/Mac:**
```bash
bash vectorize.sh
```

**Direct (Any OS):**
```bash
python -m app.cli vectorize-all
```

---

## 📋 All Commands

### Vectorize All Papers

```bash
# Basic (batch size 100)
python -m app.cli vectorize-all

# Custom batch size
python -m app.cli vectorize-all --batch-size 50

# Force re-vectorize
python -m app.cli vectorize-all --force
```

### Check Status

```bash
# Cache information
python -m app.cli cache-info

# Full status
python -m app.cli status
```

### Clear Cache

```bash
python -m app.cli clear-cache
```

---

## ⏱️ Expected Times

| Papers | Time | Batch Size |
|--------|------|-----------|
| 100 | ~30s | 50-100 |
| 500 | ~5m | 100 |
| 1000 | ~20m | 100 |
| 2000+ | ~1h+ | 200 |

---

## 🚨 Common Issues

### "Database connection failed"
→ Check `.env` file and MySQL is running

### "No papers found"
→ Need to seed database first with papers

### "Memory error"
→ Use smaller batch size: `--batch-size 50`

### "Cache corrupted"
→ Run: `python -m app.cli clear-cache` then vectorize again

---

## 💡 Tips

- Use smaller batch size if you have limited memory
- Run `cache-info` to check vectorization progress
- Always commit cache files to prevent re-computation
- Cache is automatically used by recommendation API

---

## 📖 Full Documentation

See `VECTORIZATION_CLI.md` for complete guide with all options and examples.
