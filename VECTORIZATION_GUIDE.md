# Panduan Vectorization & Recommendation Service

## 1. Architecture Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    API Endpoints                             │
├─────────────────────────────────────────────────────────────┤
│  GET  /recommend/{paper_id}    ← Gunakan default model      │
│  POST  /vectorize-all-papers   ← Build full model (ADMIN)   │
└────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│              RecommendationService                          │
├─────────────────────────────────────────────────────────────┤
│  • _build_model()              ← 100 papers (cepat)         │
│  • build_full_model_batch()    ← ALL papers (lambat)        │
│  • get_recommendations_by_paper_id()                        │
│  • preprocess() / _compute_tfidf() / _cosine_similarity()   │
└────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│              PaperRepository                                 │
├─────────────────────────────────────────────────────────────┤
│  • get_abstracts(limit=100)                                 │
│  • get_abstracts_batch(offset, batch_size)                  │
│  • get_total_papers_count()                                 │
└────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│              Database (Papers Table)                         │
└────────────────────────────────────────────────────────────┘
```

## 2. Cara Koneksi (Dengan Benar)

### Option A: Default Model (Recommendation)
```python
# Untuk endpoint /recommend/{paper_id}
from app.repositories.paper_repository import PaperRepository
from app.services.recommendation_service import RecommendationService

repo = PaperRepository(db)
service = RecommendationService(repo)  # auto_build=True (default)
# Vectorize 100 papers otomatis, cepat

results = service.get_recommendations_by_paper_id(paper_id, top_n=5)
```

### Option B: Full Model Vectorization (ADMIN ONLY)
```python
# Untuk endpoint POST /vectorize-all-papers
from app.repositories.paper_repository import PaperRepository
from app.services.recommendation_service import RecommendationService

repo = PaperRepository(db)
service = RecommendationService(repo, auto_build=False)  # Jangan build otomatis

# Build full model dengan batch processing
service.build_full_model_batch(batch_size=100, verbose=True)

total_papers = len(service.datas)
matrix_size = len(service.cosine_sim_matrix)
```

## 3. API Usage Examples

### 3.1 Get Recommendations (Quick - 100 papers)
```bash
curl -X GET "http://localhost:8000/api/v1/recommend/123?top_n=5" \
  -H "Authorization: Bearer <token>"
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "paper_id": 123,
    "recommendations": {
      "status": "success",
      "data": [
        {
          "id": 456,
          "title": "...",
          "similarity_score": 0.85
        }
      ]
    }
  }
}
```

### 3.2 Full Vectorization (ALL papers - SLOW!)
```bash
curl -X POST "http://localhost:8000/api/v1/vectorize-all-papers?batch_size=100" \
  -H "Authorization: Bearer <token>"
```

**Response:**
```json
{
  "status": "success",
  "message": "Full vectorization completed successfully",
  "data": {
    "total_papers_processed": 5000,
    "cosine_matrix_size": "5000x5000",
    "batch_size_used": 100
  }
}
```

## 4. Performance Optimization

### Default Model (100 papers)
```
┌─────────────────────┬──────────┬───────┬─────────┐
│ Jumlah Papers       │ Memory   │ TF-IDF│ Cosine  │
├─────────────────────┼──────────┼───────┼─────────┤
│ 100 (default)       │ ~10MB    │ 0.1s  │ 0.1s    │
│ 500                 │ ~50MB    │ 0.5s  │ 1s      │
│ 1,000               │ ~100MB   │ 1s    │ 3s      │
└─────────────────────┴──────────┴───────┴─────────┘
```

### Full Model dengan Batch Processing
```
Batch Size 100 untuk 5000 papers:
┌──────────────┬──────────┬─────────────┐
│ Step         │ Time     │ Memory      │
├──────────────┼──────────┼─────────────┤
│ Batch 1-50   │ 3 min    │ ~100MB      │
│ Cosine Matrix│ 5 min    │ ~500MB      │
│ Total        │ 8 min    │ Peak 500MB  │
└──────────────┴──────────┴─────────────┘
```

## 5. Implementasi Terbaik - Singleton Pattern (Optional)

Jika ingin cache model agar tidak rebuild setiap request:

```python
# vectorization_cache.py
from app.services.recommendation_service import RecommendationService
from app.repositories.paper_repository import PaperRepository

class VectorizationCache:
    _instance = None
    _service = None
    
    @classmethod
    def get_service(cls, repo: PaperRepository):
        if cls._instance is None:
            cls._instance = cls()
            cls._service = RecommendationService(repo, auto_build=False)
        return cls._service
    
    @classmethod
    def reset(cls):
        cls._instance = None
        cls._service = None

# Penggunaan di endpoint:
from app.vectorization_cache import VectorizationCache

@router.get("/recommend/{paper_id}")
async def get_recommendation(paper_id: int, db: Session = Depends(get_db)):
    repo = PaperRepository(db)
    service = VectorizationCache.get_service(repo)
    # Service cache, tidak rebuild setiap request
    return service.get_recommendations_by_paper_id(paper_id, top_n=5)
```

## 6. Monitoring Progress

Console Output dari Full Vectorization:
```
=== FULL VECTORIZATION ===
Total papers to process: 5000

Processing batch: 1 - 100
Processing batch: 101 - 200
...
Total papers with abstracts: 5000

Computing cosine similarity matrix (5000x5000)...
Progress: 10.0%
Progress: 20.0%
...
Progress: 100.0%

=== VECTORIZATION COMPLETE ===
```

## 7. Best Practices

✅ **DO:**
- Gunakan default model (100 papers) untuk production recommendations
- Jalankan full vectorization di background (scheduled task)
- Batch size 50-100 untuk optimal performance
- Monitor progress dengan logging

❌ **DON'T:**
- Jangan build full model setiap request
- Jangan hapus auto_build dari default
- Jangan gunakan batch_size terlalu kecil (>50) atau terlalu besar (<25)

## 8. Next Steps

Untuk production-ready implementation:
1. Implement caching (Singleton pattern)
2. Setup background job untuk full vectorization
3. Schedule vectorization setiap hari/minggu
4. Monitor dengan logging dan metrics
