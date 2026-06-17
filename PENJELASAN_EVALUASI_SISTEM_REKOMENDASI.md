# Penjelasan Lengkap: Sistem Rekomendasi dari Kode hingga Metrik Evaluasi

Dokumen ini menjelaskan cara kerja sistem rekomendasi Arxivinder dari tahap TF-IDF vectorization hingga menghasilkan metrik evaluasi: **Precision**, **Recall**, **F1 Score**, dan **MAP (Mean Average Precision)**.

---

## 📊 Alur Kerja Sistem

```
┌─────────────────────────────────────────────────────────┐
│ 1. PREPROCESSING                                        │
│    - Load abstract dari database                        │
│    - Lowercase, remove special chars, tokenization      │
│    - Remove stopwords, stemming                         │
└────────────┬────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────┐
│ 2. TF-IDF VECTORIZATION                                 │
│    - Hitung Term Frequency (TF)                         │
│    - Hitung Inverse Document Frequency (IDF)            │
│    - Gabungkan menjadi TF-IDF vector                    │
└────────────┬────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────┐
│ 3. SIMILARITY MATRIX                                    │
│    - Hitung cosine similarity antar dokumen             │
│    - Simpan ke matrix N×N                               │
└────────────┬────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────┐
│ 4. CONTENT-BASED FILTERING (CBF)                        │
│    - User query paper A                                 │
│    - Cari papers mirip dengan cosine similarity         │
│    - Return top N candidates                            │
└────────────┬────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────┐
│ 5. UCB RANKING (Upper Confidence Bound)                 │
│    - Re-rank candidates berdasarkan feedback history    │
│    - Balance exploitation (best performers)             │
│      & exploration (under-tested papers)                │
│    - Return top K papers                                │
└────────────┬────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────┐
│ 6. LOGGING & EVALUATION                                 │
│    - Catat recommended papers & relevant papers         │
│    - Hitung Precision, Recall, F1, MAP                 │
│    - Simpan metrics ke database                         │
└─────────────────────────────────────────────────────────┘
```

---

## 🔍 TAHAP 1-2: PREPROCESSING & TF-IDF

### Preprocessing (Kode: `recommendation_service.preprocess()`)

```python
def preprocess(self, text):
    """
    INPUT:  "Machine Learning Models for Data Analysis"
    OUTPUT: ["machin", "learn", "model", "data", "analysi"]
    """
    stemmer = PorterStemmer()
    stop_words = set(stopwords.words("english"))
    
    # 1. Lowercase
    text = text.lower()
    # "Machine Learning..." → "machine learning..."
    
    # 2. Remove special characters
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    # Keep hanya huruf & spasi
    
    # 3. Tokenize (split by space)
    tokens = text.split()
    
    # 4. Remove stopwords & stem
    tokens = [
        stemmer.stem(word)
        for word in tokens
        if word not in stop_words
    ]
    
    return tokens
```

### TF (Term Frequency) - Kode: `_compute_tf()`

**Tujuan**: Hitung seberapa sering setiap kata muncul dalam 1 dokumen.

```python
def _compute_tf(self, tokens):
    """
    tokens = ["machin", "learn", "model", "data", "analysi"]
    """
    tf = Counter(tokens)
    # Counter: {"machin": 1, "learn": 1, "model": 1, "data": 1, "analysi": 1}
    
    total = len(tokens)  # = 5
    
    tf_result = {
        word: count / total
        for word, count in tf.items()
    }
    # Hasil: setiap kata punya TF = 1/5 = 0.2
```

**Interpretasi**: Jika kata "learning" muncul 3x dari 10 token → TF["learning"] = 0.3

### IDF (Inverse Document Frequency) - Kode: `_compute_idf()`

**Tujuan**: Hitung seberapa penting suatu kata (kata umum = penting rendah).

```python
def _compute_idf(self, docs_tokens):
    """
    Misal ada 100 dokumen:
    - "learning" ada di 90 dokumen (umum) → IDF rendah
    - "perturbation" ada di 3 dokumen (spesifik) → IDF tinggi
    """
    N = len(docs_tokens)  # Total dokumen
    df = defaultdict(int)
    
    # Hitung berapa dokumen setiap kata muncul
    for tokens in docs_tokens:
        for word in set(tokens):
            df[word] += 1
    
    # IDF = log((N+1) / (df+1)) + 1
    idf_result = {
        word: math.log((N + 1) / (freq + 1)) + 1
        for word, freq in df.items()
    }
```

**Contoh Perhitungan IDF**:

```
N = 100 dokumen

"learning": muncul di 90 dokumen
  IDF = log(101/91) + 1 = log(1.11) + 1 ≈ 1.04

"perturbation": muncul di 3 dokumen
  IDF = log(101/4) + 1 = log(25.25) + 1 ≈ 4.23
```

### TF-IDF - Kode: `_compute_tfidf()`

**TF-IDF = TF × IDF** (Kombinasi frekuensi + pentingnya kata)

```python
def _compute_tfidf(self, docs_tokens):
    idf = self._compute_idf(docs_tokens)
    
    for tokens in docs_tokens:
        tf = self._compute_tf(tokens)
        tfidf = {
            word: tf[word] * idf[word]
            for word in tf
        }
```

**Contoh**:

```
Dokumen: "Machine learning neural networks"
Setelah preprocessing: ["machin", "learn", "neural", "network"]

TF (dalam dokumen ini):
  TF["machin"] = 0.25
  TF["learn"] = 0.25
  TF["neural"] = 0.25
  TF["network"] = 0.25

IDF (dari 100 dokumen):
  IDF["machin"] = 3.5
  IDF["learn"] = 1.1
  IDF["neural"] = 2.8
  IDF["network"] = 2.5

TF-IDF:
  TF-IDF["machin"] = 0.25 × 3.5 = 0.875
  TF-IDF["learn"] = 0.25 × 1.1 = 0.275
  TF-IDF["neural"] = 0.25 × 2.8 = 0.70
  TF-IDF["network"] = 0.25 × 2.5 = 0.625

TF-IDF Vector = {
  "machin": 0.875,
  "learn": 0.275,
  "neural": 0.70,
  "network": 0.625
}
```

---

## 📈 TAHAP 3: COSINE SIMILARITY

### Konsep

Mengukur kesamaan antara 2 vektor TF-IDF dengan menghitung cosine dari sudut antar vektor.

**Formula**:
```
Cosine Similarity = (A · B) / (||A|| × ||B||)

Dot Product (A · B) = Σ(A[i] × B[i])
Magnitude ||A|| = √(Σ(A[i]²))
```

### Kode: `_cosine_similarity()`

```python
def _cosine_similarity(self, vec1, vec2):
    """
    vec1 = {"machin": 0.87, "learn": 0.28, "neural": 0.70}
    vec2 = {"machin": 0.50, "learn": 0.30, "neural": 0.75, "network": 0.45}
    """
    
    # Step 1: Common words (kata yang ada di kedua vektor)
    common_words = set(vec1.keys()) & set(vec2.keys())
    # {"machin", "learn", "neural"}
    
    # Step 2: Dot product
    dot_product = sum(vec1[w] * vec2[w] for w in common_words)
    # = (0.87×0.50) + (0.28×0.30) + (0.70×0.75)
    # = 0.435 + 0.084 + 0.525
    # = 1.044
    
    # Step 3: Magnitude vec1
    norm1 = math.sqrt(sum(v ** 2 for v in vec1.values()))
    # = sqrt((0.87)² + (0.28)² + (0.70)²)
    # = sqrt(0.7569 + 0.0784 + 0.49)
    # = sqrt(1.3253)
    # ≈ 1.151
    
    # Step 4: Magnitude vec2
    norm2 = math.sqrt(sum(v ** 2 for v in vec2.values()))
    # = sqrt((0.50)² + (0.30)² + (0.75)² + (0.45)²)
    # = sqrt(0.25 + 0.09 + 0.5625 + 0.2025)
    # = sqrt(1.165)
    # ≈ 1.079
    
    # Step 5: Cosine similarity
    cosine_sim = dot_product / (norm1 * norm2)
    # = 1.044 / (1.151 × 1.079)
    # = 1.044 / 1.242
    # ≈ 0.84
    
    return cosine_sim
```

**Hasil**: Vektor vec1 dan vec2 memiliki similarity **0.84 (84%)**

---

## 🏆 TAHAP 4: CONTENT-BASED FILTERING

### Kode: `get_recommendations_by_paper_id()`

```python
def get_recommendations_by_paper_id(self, paper_id: int, top_n: int):
    """
    User: "Beri rekomendasi papers mirip dengan paper_id=5"
    """
    
    # Step 1: Cari index paper_id=5
    index = next((i for i, d in enumerate(self.datas) 
                  if d["id"] == paper_id), None)
    # Misal index = 2
    
    # Step 2: Ambil similarity scores paper 5 vs semua papers
    similarity_scores = self.cosine_sim_matrix[index]
    # [0.42, 0.86, 1.00, 0.71, 0.55, ...]
    #  Doc1  Doc2  Doc3  Doc4  Doc5
    
    # Step 3: Sort dari tertinggi ke terendah
    indexed_scores = list(enumerate(similarity_scores))
    indexed_scores.sort(key=lambda x: x[1], reverse=True)
    # [(2, 1.00), (1, 0.86), (3, 0.71), (4, 0.55), (0, 0.42), ...]
    
    # Step 4: Ambil top_n, skip paper_id itu sendiri
    top_indices = [i for i, _ in indexed_scores if i != index][:top_n]
    # [1, 3, 4, 0, ...]
    
    # Step 5: Return hasil
    return {
        "paper_id": 5,
        "recommendations": [
            {"id": 2, "title": "Neural Networks", "similarity_score": 0.86},
            {"id": 4, "title": "Computer Vision", "similarity_score": 0.71},
            {"id": 1, "title": "Deep Learning", "similarity_score": 0.42}
        ]
    }
```

---

## 🎯 TAHAP 5: UCB RANKING

### Konsep UCB

**Upper Confidence Bound** adalah strategi untuk balance antara:
- **Exploitation**: Pilih paper dengan performa terbaik (dari feedback)
- **Exploration**: Coba paper yang belum banyak diuji

### Formula UCB

```
UCB = Mean_CTR + α × √(ln(t) / N)

Di mana:
- Mean_CTR = clicks / views (Click-Through Rate)
- α = exploration factor (default = 2.0)
- t = total feedback count
- N = views (jumlah kali paper ini dilihat)
```

### Kode: `ucb_service.calculate_ucb()`

```python
def calculate_ucb(self, reward, total_action, t):
    """
    reward = 5 clicks
    total_action = 20 views
    t = 1000 (total feedback)
    alpha = 2.0 (default)
    """
    
    # Guard condition
    if total_action == 0:
        return 0.0
    
    t = float(max(t, 2))
    
    # STEP 1: Hitung Mean_CTR
    mean = reward / total_action
    #     = 5 / 20 = 0.25 (25% CTR)
    
    # STEP 2: Hitung Exploration Bonus
    exploration = self.alpha * math.sqrt(
        (math.log10(t)) / total_action
    )
    # = 2.0 × √(log10(1000) / 20)
    # = 2.0 × √(3.0 / 20)
    # = 2.0 × √(0.15)
    # = 2.0 × 0.387
    # = 0.774
    
    # STEP 3: UCB Score
    ucb = mean + exploration
    #   = 0.25 + 0.774 = 1.024
    
    return ucb
```

### Contoh UCB Ranking

```
Candidate Papers:

Paper A: 5 clicks, 20 views
  Mean_CTR = 5/20 = 0.25
  Exploration = 2.0 × √(3.0/20) = 0.774
  UCB = 0.25 + 0.774 = 1.024 ✓ RANK #1

Paper B: 2 clicks, 15 views
  Mean_CTR = 2/15 = 0.133
  Exploration = 2.0 × √(3.0/15) = 0.894
  UCB = 0.133 + 0.894 = 1.027 ✓ RANK #2

Paper C: 0 clicks, 5 views
  Mean_CTR = 0/5 = 0.0
  Exploration = 2.0 × √(3.0/5) = 1.549
  UCB = 0.0 + 1.549 = 1.549 ✓ RANK #1 (!)
```

**Insight**: Paper C meski belum pernah di-click, tapi diberi kesempatan karena belum banyak diuji (exploration).

### Kode: `rank_from_list()`

```python
def rank_from_list(self, paper_id: int, top_k: int = 10):
    """
    Langkah lengkap UCB ranking:
    """
    
    # 1. Get candidates dari CBF
    cbf_candidates = self.cbf_service.get_recommendations_by_paper_id(
        paper_id, top_n=20
    )["recommendations"]
    
    # 2. Get feedback stats untuk setiap candidate
    feedback_stats = {
        cid: self.feedback_repo.get_paper_stats(cid)
        for cid in candidate_ids
    }
    # {"2": (5, 20), "4": (2, 15), "7": (0, 5), ...}
    
    # 3. Get total feedback count
    t = self.feedback_repo.count_total_feedback() + 1
    
    # 4. Calculate UCB & re-rank
    ranked = []
    for item in cbf_candidates:
        reward, total_action = feedback_stats.get(item["id"], (0, 0))
        ucb_score = self.calculate_ucb(reward, total_action, t)
        
        ranked.append({
            "paper_id": item["id"],
            "title": item["title"],
            "cosine_score": item["similarity_score"],
            "ucb_score": ucb_score,
            "clicks": reward,
            "views": total_action
        })
    
    # 5. Sort by UCB (tertinggi dulu)
    ranked.sort(key=lambda x: x["ucb_score"], reverse=True)
    
    return {"data": ranked[:top_k]}
```

---

## 📝 TAHAP 6: EVALUATION METRICS

### Data untuk Evaluasi

```python
recommended = [2, 10, 7, 4]     # Papers yang direkomendasikan
relevant = [2, 3, 7, 9]          # Papers yang user suka (ground truth)
k = 3                             # Evaluasi top 3
```

---

### ⚡ PRECISION AT K

**Tanya**: Dari K rekomendasi, berapa % yang relevan?

**Formula**: `Precision@k = |Rec[:k] ∩ Rel| / k`

**Kode**:

```python
def precision_at_k(self, recommended, relevant, k):
    rec_k = recommended[:k]
    # [2, 10, 7]
    
    hit = len(set(rec_k) & set(relevant))
    # set([2, 10, 7]) & set([2, 3, 7, 9])
    # = {2, 7}
    # hit = 2
    
    return hit / k if k > 0 else 0
    # = 2 / 3 = 0.667 (66.7%)
```

**Interpretasi**: Dari 3 rekomendasi teratas, 2 relevan → Precision bagus (66.7%).

---

### 🎣 RECALL AT K

**Tanya**: Dari semua yang relevan, berapa % yang kami rekomendasikan (top K)?

**Formula**: `Recall@k = |Rec[:k] ∩ Rel| / |Rel|`

**Kode**:

```python
def recall_at_k(self, recommended, relevant, k):
    rec_k = recommended[:k]
    # [2, 10, 7]
    
    hit = len(set(rec_k) & set(relevant))
    # = 2
    
    return hit / len(relevant) if relevant else 0
    # = 2 / 4 = 0.5 (50%)
```

**Interpretasi**: Ada 4 papers relevan total. Dari top 3, kami menemukan 2 (50%).

---

### ⚖️ F1 SCORE

**Tanya**: Keseimbangan antara Precision dan Recall?

**Formula**: `F1 = 2 × (P × R) / (P + R)`

**Kode**:

```python
def f1_score(self, p, r):
    if (p + r) > 0:
        return 2 * p * r / (p + r)
    else:
        return 0
```

**Contoh**:

```
Precision@3 = 0.667
Recall@3 = 0.5

F1 = 2 × (0.667 × 0.5) / (0.667 + 0.5)
   = 2 × 0.333 / 1.167
   = 0.571 (57.1%)
```

---

### 🎯 AVERAGE PRECISION (MAP)

**Tanya**: Precision rata-rata saat menemukan setiap item relevan?

**Formula**: `AP = (1 / |Rel|) × Σ(Precision@i × rel_i)`

**Kode**:

```python
def average_precision(self, recommended, relevant, k):
    rec_k = recommended[:k]
    # [2, 10, 7, 4]
    
    if not relevant:
        return 0.0
    
    score = 0.0
    hit = 0
    
    for i, item in enumerate(rec_k):
        rel_i = 1 if item in relevant else 0
        
        if rel_i:
            hit += 1
            precision_at_i = hit / (i + 1)
            score += precision_at_i
    
    return score / len(relevant)
```

**Contoh Step-by-Step**:

```
Recommended: [2, 10, 7, 4]
Relevant: [2, 3, 7, 9]

Pos 0: Item 2 ✓ RELEVAN
  hit = 1, Precision@1 = 1/1 = 1.0
  score = 1.0

Pos 1: Item 10 ✗ TIDAK RELEVAN
  score = 1.0 (tidak berubah)

Pos 2: Item 7 ✓ RELEVAN
  hit = 2, Precision@3 = 2/3 = 0.667
  score = 1.0 + 0.667 = 1.667

Pos 3: Item 4 ✗ TIDAK RELEVAN
  score = 1.667 (tidak berubah)

AP = 1.667 / 4 = 0.417 (41.7%)
```

---

## 💾 TAHAP 7: SIMPAN KE DATABASE

### Flow Penyimpanan

```python
# Dari eval_result.py → POST /api/v1/evaluation/sync

# 1. Get semua logs
logs = log_repo.get_all()

# 2. Calculate metrics untuk setiap log per k value
K_VALUES = [1, 2, 3, 4, 5]

for log in logs:
    for k in K_VALUES:
        p = service.precision_at_k(log.recommendations, log.relevants, k)
        r = service.recall_at_k(log.recommendations, log.relevants, k)
        ap = service.average_precision(log.recommendations, log.relevants, k)
        
        f1 = 2 * (p * r) / (p + r) if (p + r) > 0 else 0

# 3. Save to database
eval_repo.save_bulk(evaluation_results)
```

### Database Structure

```sql
CREATE TABLE evaluation_results (
    id INT PRIMARY KEY,
    user_id INT,
    precision FLOAT,      -- Precision@k
    recall FLOAT,         -- Recall@k
    f1_score FLOAT,       -- F1@k
    mean_average_precision FLOAT,  -- MAP@k
    k INT,                -- k value
    created_at TIMESTAMP
);
```

---

## 📊 RINGKASAN METRIK

| Metrik | Formula | Makna | Target |
|--------|---------|-------|--------|
| **Precision@k** | \|Rec ∩ Rel\| / k | Dari k rekomendasi, berapa % relevan? | > 0.8 |
| **Recall@k** | \|Rec ∩ Rel\| / \|Rel\| | Dari semua relevan, berapa % ditemukan? | > 0.7 |
| **F1@k** | 2(PR)/(P+R) | Keseimbangan P dan R | > 0.7 |
| **MAP@k** | Avg(P saat hit) | Precision rata-rata saat item relevan | > 0.7 |
| **UCB** | Mean_CTR + α√(ln(t)/N) | Score untuk ranking dengan exploration | - |

---

## 🔗 ENDPOINT EVALUASI

```
POST /api/v1/evaluation/sync
  → Hitung semua metrik dari logs

GET /api/v1/evaluation/average-metrics
  → {average_precision, average_recall, average_f1_score, average_map}

GET /api/v1/evaluation/average-metrics-by-k
  → Metrics untuk setiap k value
```

---

## 📚 Kesimpulan Alur Lengkap

```
User Query
    ↓
TF-IDF Vectorization & Cosine Similarity (CBF)
    ↓
Get CBF Candidates [2, 4, 7, 10]
    ↓
UCB Re-ranking dengan feedback history
    ↓
Return ranked papers [2, 7, 4, 10]
    ↓
Log: recommended=[2,7,4,10], relevant=[2,3,7,9]
    ↓
Evaluate:
  - Precision@3 = 2/3 = 0.667
  - Recall@3 = 2/4 = 0.5
  - F1@3 = 0.571
  - AP@3 = 0.417
    ↓
Save to database
    ↓
Analyze performance → Improve model
```
