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

## 📝 TAHAP 6: EVALUATION METRICS (LENGKAP)

### 6.1 Ground Truth & Data Preparation

#### Apa itu Ground Truth?

**Ground truth** adalah label yang benar (label diberikan oleh admin/expert), bukan prediksi sistem.

```python
# recommendation_logs table
{
    "user_id": 123,
    "recommendations": [2, 10, 7, 4],      # Output dari sistem rekomendasi
    "relevants": [2, 3, 7, 9]               # Ground truth (admin tentukan)
}
```

#### Bagaimana Ground Truth Ditentukan?

Ada beberapa cara:

**1. Manual Labeling oleh Admin**
```python
# Admin inspect setiap rekomendasi dan tandai yang relevan
recommendations = [2, 10, 7, 4]
relevant = [2, 3, 7, 9]  # Admin set manually
```

**2. User Behavior Tracking** (jika user engagement ditrack)
```python
# Jika user click/like rekomendasi → anggap relevan
if user_clicked_paper_2:
    relevant.append(2)
```

**3. Similarity dengan Paper yang User Like**
```python
# Jika user sebelumnya like papers [2, 3, 7, 9]
# Gunakan itu sebagai ground truth
user_liked = [2, 3, 7, 9]
relevant = user_liked
```

### 6.2 Metrik Evaluasi Detail

---

### ⚡ PRECISION AT K

**Definisi Formal**: Proporsi rekomendasi yang relevan dari K rekomendasi teratas.

**Pertanyaan**: "Dari K papers yang kami rekomendasikan, berapa persen yang benar-benar relevan?"

**Formula**:
```
Precision@k = (Jumlah rekomendasi relevan dalam top k) / k
            = |Recommended[:k] ∩ Relevant| / k
```

**Kode Dari Codebase**:

```python
def precision_at_k(self, recommended, relevant, k):
    # recommended = [2, 10, 7, 4]  (urutan papers dari sistem)
    # relevant = [2, 3, 7, 9]      (ground truth - papers yang relevan)
    # k = 3                         (evaluasi top 3)
    
    rec_k = recommended[:k]
    # rec_k = [2, 10, 7]  (ambil top 3 dari recommended)
    
    # Hitung berapa banyak dari rec_k yang ada di relevant
    hit = len(set(rec_k) & set(relevant))
    # set([2, 10, 7]) & set([2, 3, 7, 9])
    # = {2, 7}
    # hit = 2  (ada 2 papers yang relevan)
    
    return hit / k if k > 0 else 0
    # = 2 / 3 = 0.6667 (66.67%)
```

**Interpretasi Detail**:

```
Recommended: [2, 10, 7, 4]
Relevant:    [2, 3, 7, 9]

Precision@1 = 1 / 1 = 1.0    (paper[0]=2 ✓ relevan)
Precision@2 = 1 / 2 = 0.5    (paper[1]=10 ✗ tidak relevan)
Precision@3 = 2 / 3 = 0.667  (paper[2]=7 ✓ relevan)
Precision@4 = 2 / 4 = 0.5    (paper[3]=4 ✗ tidak relevan)
```

**Visualisasi**:

```
┌─────────────────────────────────────────┐
│ Ranking of Recommended Papers            │
├─────────────────────────────────────────┤
│ Rank 1: Paper 2 ✓ RELEVAN               │
│ Rank 2: Paper 10 ✗ NOT RELEVAN          │
│ Rank 3: Paper 7 ✓ RELEVAN               │
│ Rank 4: Paper 4 ✗ NOT RELEVAN           │
└─────────────────────────────────────────┘

Precision@1 = ✓/1 = 1.0   (100%)
Precision@2 = ✓/2 = 0.5   (50%)
Precision@3 = 2✓/3 = 0.667 (67%)
Precision@4 = 2✓/4 = 0.5  (50%)
```

**Interpretasi Bisnis**:
- **Precision tinggi (0.8+)**: User akan puas, mayoritas rekomendasi bagus
- **Precision rendah (0.3-)**: User akan kecewa, banyak rekomendasi jelek

**Kapan Precision Penting?**
- ✅ E-commerce: User tidak suka dibanjiri produk irrelevant
- ✅ Streaming: Rekomendasi harus berkualitas agar tidak mengganggu
- ❌ Search engine: Recall lebih penting (user cari informasi lengkap)

---

### 🎣 RECALL AT K

**Definisi Formal**: Proporsi relevant items yang berhasil direkomendasikan dalam top K.

**Pertanyaan**: "Dari SEMUA papers yang seharusnya direkomendasikan (relevant), berapa persen yang kami temukan di top K?"

**Formula**:
```
Recall@k = (Jumlah rekomendasi relevan dalam top k) / (Total jumlah relevant)
         = |Recommended[:k] ∩ Relevant| / |Relevant|
```

**Kode**:

```python
def recall_at_k(self, recommended, relevant, k):
    # recommended = [2, 10, 7, 4]
    # relevant = [2, 3, 7, 9]  (total 4 papers yang relevan)
    # k = 3
    
    rec_k = recommended[:k]
    # rec_k = [2, 10, 7]
    
    hit = len(set(rec_k) & set(relevant))
    # = 2  (papers 2 dan 7)
    
    return hit / len(relevant) if relevant else 0
    # = 2 / 4 = 0.5 (50%)
```

**Interpretasi Detail**:

```
Ada 4 papers yang SEHARUSNYA direkomendasikan (relevant): [2, 3, 7, 9]

Recall@1 = 1 / 4 = 0.25   (kami temukan 1 dari 4 = 25%)
Recall@2 = 1 / 4 = 0.25   (kami temukan 1 dari 4 = 25%)
Recall@3 = 2 / 4 = 0.5    (kami temukan 2 dari 4 = 50%)
Recall@4 = 2 / 4 = 0.5    (kami temukan 2 dari 4 = 50%)
           ↑ paper 3 dan 9 tidak ditemukan
```

**Visualisasi**:

```
Relevant Papers (yang seharusnya ada):
[2] [3] [7] [9]
 ✓   ✗  ✓   ✗    ← Di top 3 rekomendasi

Recall = (✓ yang ditemukan) / (✓ total) = 2 / 4 = 50%

Artinya: Kami menemukan 50% dari papers yang user seharusnya ketahui
```

**Interpretasi Bisnis**:
- **Recall tinggi (0.8+)**: User menemukan sebagian besar papers relevan
- **Recall rendah (0.3-)**: User akan ketinggalan banyak papers bagus

**Kapan Recall Penting?**
- ✅ Search engine: User perlu hasil pencarian lengkap
- ✅ Medical diagnosis: Harus menemukan semua kemungkinan penyakit
- ❌ Spam filter: Precision lebih penting (jangan filter email legitimate)

---

### ⚖️ F1 SCORE AT K

**Definisi Formal**: Harmonic mean dari Precision dan Recall. Mengukur keseimbangan antara keduanya.

**Pertanyaan**: "Bagaimana keseimbangan antara akurasi rekomendasi (precision) dan cakupan items relevan (recall)?"

**Formula**:
```
F1@k = 2 × (Precision@k × Recall@k) / (Precision@k + Recall@k)

Alternatif: F1 = 2PR / (P + R)
```

**Kode**:

```python
def f1_score(self, p, r):
    # p = precision (0.667)
    # r = recall (0.5)
    
    if (p + r) > 0:
        return 2 * p * r / (p + r)
    else:
        return 0
    
    # = 2 × (0.667 × 0.5) / (0.667 + 0.5)
    # = 2 × 0.333 / 1.167
    # = 0.667 / 1.167
    # = 0.571 (57.1%)
```

**Mengapa F1 Lebih Baik dari Rata-rata Arithmetic?**

```
Contoh: P = 0.9, R = 0.1

Arithmetic Mean = (0.9 + 0.1) / 2 = 0.5
F1 Score = 2 × (0.9 × 0.1) / (0.9 + 0.1) = 0.167

↑ F1 lebih rendah karena ada ketidakseimbangan besar
```

**Interpretasi Detail**:

```
Precision@3 = 2/3 = 0.667  (dari 3 rekomendasi, 2 relevan)
Recall@3 = 2/4 = 0.5       (dari 4 relevant, menemukan 2)

F1 = 2 × (0.667 × 0.5) / (0.667 + 0.5)
   = 2 × 0.333 / 1.167
   = 0.571

F1 Score = 57.1% (keseimbangan cukup baik, tapi tidak sempurna)
```

**Interpretasi Bisnis**:
- **F1 tinggi (0.7+)**: Sistem seimbang (precision & recall sama-sama baik)
- **F1 rendah (0.3-)**: Ada masalah pada salah satu metrik
- **F1 Medium (0.5)**: Ada trade-off antara precision dan recall

**Contoh Trade-off**:

```
Sistem A:
  Precision = 0.9 (akurat)
  Recall = 0.1 (tidak lengkap)
  F1 = 0.18 (BAD - terlalu fokus precision)

Sistem B:
  Precision = 0.5 (cukup)
  Recall = 0.5 (cukup)
  F1 = 0.5 (BETTER - seimbang)

Sistem C:
  Precision = 0.8 (bagus)
  Recall = 0.8 (bagus)
  F1 = 0.8 (EXCELLENT - seimbang sempurna)
```

---

### 🎯 AVERAGE PRECISION (MAP AT K)

**Definisi Formal**: Precision rata-rata yang dihitung hanya saat sistem menemukan item relevan. Memberikan bobot lebih ke ranking awal.

**Pertanyaan**: "Bagaimana kualitas ranking ketika sistem menemukan items relevan?"

**Formula**:
```
AP@k = (1 / |Relevant|) × Σ(Precision@i × rel_i)

Di mana:
- i = posisi (1 hingga k)
- rel_i = 1 jika item di posisi i relevan, 0 jika tidak
- Precision@i = precision hingga posisi i
```

**Kode**:

```python
def average_precision(self, recommended, relevant, k):
    # recommended = [2, 10, 7, 4]
    # relevant = [2, 3, 7, 9]
    # k = 4 (evaluasi 4)
    
    rec_k = recommended[:k]
    if not relevant:
        return 0.0
    
    score = 0.0
    hit = 0
    
    # Loop setiap posisi
    for i, item in enumerate(rec_k):
        # Apakah item di posisi i relevan?
        rel_i = 1 if item in relevant else 0
        
        if rel_i:
            # Item relevan ditemukan
            hit += 1
            # Hitung precision hingga posisi i
            precision_at_i = hit / (i + 1)
            # Tambah ke score
            score += precision_at_i
    
    # Rata-rata dari jumlah relevant items
    return score / len(relevant)
```

**Contoh Step-by-Step Detailed**:

```
Recommended: [2, 10, 7, 4]
Relevant: [2, 3, 7, 9]
Total relevant = 4

┌─────────────────────────────────────────────────────┐
│ POSITION 0: Item 2                                  │
├─────────────────────────────────────────────────────┤
│ Is 2 in [2, 3, 7, 9]? YES ✓ RELEVAN               │
│                                                     │
│ hit = 0 + 1 = 1                                    │
│ Precision@1 = 1 (# hits) / 1 (position) = 1.0     │
│ score = 0 + 1.0 = 1.0                              │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ POSITION 1: Item 10                                 │
├─────────────────────────────────────────────────────┤
│ Is 10 in [2, 3, 7, 9]? NO ✗ TIDAK RELEVAN         │
│                                                     │
│ hit = 1 (tidak berubah)                            │
│ score = 1.0 (tidak berubah)                        │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ POSITION 2: Item 7                                  │
├─────────────────────────────────────────────────────┤
│ Is 7 in [2, 3, 7, 9]? YES ✓ RELEVAN               │
│                                                     │
│ hit = 1 + 1 = 2                                    │
│ Precision@3 = 2 (# hits) / 3 (position) = 0.667   │
│ score = 1.0 + 0.667 = 1.667                        │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ POSITION 3: Item 4                                  │
├─────────────────────────────────────────────────────┤
│ Is 4 in [2, 3, 7, 9]? NO ✗ TIDAK RELEVAN          │
│                                                     │
│ hit = 2 (tidak berubah)                            │
│ score = 1.667 (tidak berubah)                      │
└─────────────────────────────────────────────────────┘

FINAL CALCULATION:
AP = score / |Relevant|
   = 1.667 / 4
   = 0.4167 (41.67%)
```

**Visualisasi Perbandingan dengan Precision**:

```
┌───────────────────────────────────────────────┐
│ Recommended: [2✓, 10✗, 7✓, 4✗]                │
│ Relevant: [2, 3, 7, 9]                        │
├───────────────────────────────────────────────┤
│                                               │
│ PRECISION:                                    │
│   P@1 = 1/1 = 1.0                             │
│   P@2 = 1/2 = 0.5                             │
│   P@3 = 2/3 = 0.667                           │
│   P@4 = 2/4 = 0.5                             │
│   Avg Precision = (1+0.5+0.667+0.5)/4 = 0.542│
│   ↑ Rata-rata semua posisi                    │
│                                               │
│ MAP (Mean Average Precision):                 │
│   Hanya saat item relevan ditemukan:          │
│   = (1.0 + 0.667) / 4 = 0.417                 │
│   ↑ Rata-rata precision saat hit ONLY         │
└───────────────────────────────────────────────┘

Kesimpulan:
- MAP lebih rendah dari Avg Precision
- MAP memberikan penalti lebih besar untuk false positives
- MAP lebih baik mengukur ranking quality
```

**Mengapa MAP Lebih Baik?**

Bandingkan 2 skenario:

```
Scenario 1 (Good Ranking):
  Recommended: [A✓, B✓, C✗, D✗]
  AP = (1/1 + 2/2) / 2 = 1.0

Scenario 2 (Bad Ranking):
  Recommended: [A✗, B✗, C✓, D✓]
  AP = (1/3 + 2/4) / 2 = 0.417

↑ MAP memberikan score lebih tinggi ketika relevant items di ranking awal
```

**Interpretasi Bisnis**:
- **MAP tinggi (0.7+)**: Relevant papers muncul di ranking awal
- **MAP rendah (0.3-)**: Relevant papers tersebar di ranking belakang

---

### 📊 Metrik per K Value - Comprehensive Example

```python
# Dari eval_result.py - POST /api/v1/evaluation/sync

K_VALUES = [1, 2, 3, 4, 5]

recommended = [2, 10, 7, 4, 6]
relevant = [2, 3, 7, 9]

# Calculate untuk setiap K
metrics = {}

for k in K_VALUES:
    p = precision_at_k(recommended, relevant, k)
    r = recall_at_k(recommended, relevant, k)
    ap = average_precision(recommended, relevant, k)
    f1 = f1_score(p, r)
    
    metrics[k] = {
        'precision': p,
        'recall': r,
        'f1': f1,
        'map': ap
    }
```

**Hasil Tabel**:

```
k | Recommended[:k] | Precision | Recall | F1    | MAP
--|-----------------|-----------|--------|-------|-------
1 | [2]             | 1.0       | 0.25   | 0.4   | 1.0
2 | [2, 10]         | 0.5       | 0.25   | 0.333 | 0.5
3 | [2, 10, 7]      | 0.667     | 0.5    | 0.571 | 0.556
4 | [2, 10, 7, 4]   | 0.5       | 0.5    | 0.5   | 0.417
5 | [2, 10, 7, 4, 6]| 0.4       | 0.5    | 0.444 | 0.333
```

**Interpretasi Trend**:
- Precision menurun seiring K naik (natural - semakin banyak rekomendasi, semakin banyak false positives)
- Recall naik sampai semua relevant items ditemukan
- MAP ideal di K=3 (balance terbaik)

---

### 6.3 Aggregation: Dari Individual ke Overall Metrics

#### Per-User Aggregation

Setiap user bisa punya multiple logs. Aggregasi dengan rata-rata:

```python
user_1_metrics = {
    'k1': {'p': 0.9, 'r': 0.3, 'f1': 0.45, 'ap': 0.9},
    'k3': {'p': 0.8, 'r': 0.6, 'f1': 0.686, 'ap': 0.667},
    'k5': {'p': 0.6, 'r': 0.8, 'f1': 0.686, 'ap': 0.533}
}

# Rata-rata untuk k=3
avg_p_k3 = (0.9 + 0.8 + ... ) / n_logs
avg_r_k3 = (0.3 + 0.6 + ... ) / n_logs
```

#### System-Wide Aggregation

Rata-rata dari semua users:

```python
all_users_p_k3 = [user1_p_k3, user2_p_k3, ..., userN_p_k3]
system_avg_p_k3 = sum(all_users_p_k3) / len(all_users_p_k3)
```

---

## 💾 TAHAP 7: SIMPAN KE DATABASE & RETRIEVAL

### 7.1 Flow Penyimpanan Lengkap

#### Flow Diagram

```
┌──────────────────────────────────────────────────────┐
│ Step 1: GET ALL RECOMMENDATION LOGS                  │
│                                                      │
│ recommendation_logs table:                           │
│ ┌────────────────────────────────────────────────┐  │
│ │ user_id │ recommendations │ relevants          │  │
│ ├────────────────────────────────────────────────┤  │
│ │ 1       │ [2, 10, 7, 4]   │ [2, 3, 7, 9]      │  │
│ │ 2       │ [5, 6, 8]       │ [5, 8, 11]        │  │
│ │ 3       │ [1, 2, 3, 4, 5] │ [1, 3, 5]         │  │
│ └────────────────────────────────────────────────┘  │
│                                                      │
│ Total: 3 logs                                        │
└──────────────────────┬───────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────┐
│ Step 2: CALCULATE METRICS FOR EACH LOG PER K VALUE   │
│                                                      │
│ For each log:                                        │
│   For each k in [1, 2, 3, 4, 5]:                     │
│     Calculate:                                       │
│     - Precision@k                                    │
│     - Recall@k                                       │
│     - F1@k                                           │
│     - AP@k                                           │
│                                                      │
│ Total calculations: 3 logs × 5 k values = 15 rows   │
└──────────────────────┬───────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────┐
│ Step 3: AGGREGATE PER USER PER K (Optional)          │
│                                                      │
│ If same user memiliki multiple logs:                 │
│ - Average metrics untuk setiap k value               │
│                                                      │
│ evaluation_results table (sample):                   │
│ ┌──────────────────────────────────────────────────┐│
│ │ user_id│ k │ precision │ recall │ f1 │ map  │   ││
│ ├──────────────────────────────────────────────────┤│
│ │ 1      │ 1 │ 1.0       │ 0.25   │0.4 │1.0   │   ││
│ │ 1      │ 3 │ 0.667     │ 0.5    │0.57│0.556 │   ││
│ │ 1      │ 5 │ 0.4       │ 0.5    │0.44│0.333 │   ││
│ │ 2      │ 1 │ 1.0       │ 0.33   │0.5 │1.0   │   ││
│ │ 2      │ 3 │ 0.667     │ 0.67   │0.67│0.611 │   ││
│ │ 3      │ 1 │ 1.0       │ 0.33   │0.5 │1.0   │   ││
│ │ ...    │..│ ...       │ ...    │... │...  │   ││
│ └──────────────────────────────────────────────────┘│
│                                                      │
│ Total: 3 users × 5 k values (≤15 rows)              │
└──────────────────────┬───────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────┐
│ Step 4: SAVE TO DATABASE                             │
│                                                      │
│ eval_repo.save_bulk(evaluation_results)              │
│                                                      │
│ INSERT INTO evaluation_results                       │
│ VALUES (user_id, precision, recall, f1, map, k, ts) │
└──────────────────────────────────────────────────────┘
```

#### Kode Dari Codebase

```python
# Dari app/api/routes/eval_result.py → POST /api/v1/evaluation/sync

@router.post("/sync")
def sync_evaluation(db: Session = Depends(get_db)):
    try:
        # STEP 1: Get all recommendation logs
        log_repo = RecommendationLogRepository(db)
        logs = log_repo.get_all()
        
        if not logs:
            raise HTTPException(status_code=400, detail="No logs found")
        
        # STEP 2: Prepare service & repository
        repo = EvaluationRepository(db)
        service = EvaluationService(repo)
        
        K_VALUES = [1, 2, 3, 4, 5]
        user_k_metrics = {}
        
        # STEP 3: Calculate metrics untuk setiap log
        for log in logs:
            user_id = log.user_id
            recs = log.recommendations or []
            rels = log.relevants or []
            
            # Initialize dict untuk user jika belum ada
            if user_id not in user_k_metrics:
                user_k_metrics[user_id] = {
                    k: {"p": [], "r": [], "ap": []} for k in K_VALUES
                }
            
            # Calculate untuk setiap k
            for k in K_VALUES:
                if len(recs) < k:  # Skip jika recommendations < k
                    continue
                
                # Calculate individual metrics
                p = service.precision_at_k(recs, rels, k)
                r = service.recall_at_k(recs, rels, k)
                ap = service.average_precision(recs, rels, k)
                
                # Append ke list (untuk aggregation nanti)
                user_k_metrics[user_id][k]["p"].append(p)
                user_k_metrics[user_id][k]["r"].append(r)
                user_k_metrics[user_id][k]["ap"].append(ap)
        
        # STEP 4: Aggregate per user per k
        evaluation_results = []
        
        for user_id, k_data in user_k_metrics.items():
            for k, metrics in k_data.items():
                
                if not metrics["p"]:  # Skip jika tidak ada data
                    continue
                
                n = len(metrics["p"])
                
                # Average metrics untuk user ini di k ini
                avg_p = sum(metrics["p"]) / n
                avg_r = sum(metrics["r"]) / n
                avg_ap = sum(metrics["ap"]) / n
                
                # Calculate F1
                if avg_p + avg_r > 0:
                    f1 = 2 * (avg_p * avg_r) / (avg_p + avg_r)
                else:
                    f1 = 0
                
                # Append to results
                evaluation_results.append({
                    "user_id": user_id,
                    "precision": avg_p,
                    "recall": avg_r,
                    "f1_score": f1,
                    "map_score": avg_ap,
                    "k": k
                })
        
        # STEP 5: Save to database
        repo.delete_all()  # Clear old results
        repo.save_bulk(evaluation_results)
        
        # STEP 6: Calculate & return summary
        summary = service.calculate_mean_metrics(evaluation_results)
        all_ap = [r["map_score"] for r in evaluation_results 
                  if r["map_score"] is not None]
        mean_ap = sum(all_ap) / len(all_ap) if all_ap else 0
        
        return {
            "message": "Evaluation synced successfully",
            "summary": summary,
            "mean_average_precision": mean_ap,
            "total_rows": len(evaluation_results)
        }
        
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Internal server error")
```

**Contoh Response**:

```json
{
  "message": "Evaluation synced successfully",
  "summary": {
    "precision": 0.7234,
    "recall": 0.5678,
    "f1_score": 0.6345,
    "map": 0.6123
  },
  "mean_average_precision": 0.6123,
  "total_rows": 15
}
```

---

### 7.2 Database Structure

#### evaluation_results Table

```sql
CREATE TABLE evaluation_results (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    
    -- Metrics
    precision FLOAT NOT NULL,      -- Precision@k (0.0 - 1.0)
    recall FLOAT NOT NULL,         -- Recall@k (0.0 - 1.0)
    f1_score FLOAT,                -- F1@k (0.0 - 1.0)
    mean_average_precision FLOAT,  -- MAP@k (0.0 - 1.0)
    
    -- Metadata
    k INT NOT NULL,                -- k value (1, 2, 3, 4, 5)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Indexes untuk fast query
    FOREIGN KEY (user_id) REFERENCES users(id),
    INDEX idx_user_k (user_id, k),
    INDEX idx_created (created_at)
);
```

#### Sample Data

```
id | user_id | precision | recall | f1_score | map_score | k | created_at
---|---------|-----------|--------|----------|-----------|---|--------------------
1  | 1       | 1.0       | 0.25   | 0.4      | 1.0       | 1 | 2024-01-10 10:00:00
2  | 1       | 0.5       | 0.25   | 0.333    | 0.5       | 2 | 2024-01-10 10:00:00
3  | 1       | 0.667     | 0.5    | 0.571    | 0.556     | 3 | 2024-01-10 10:00:00
4  | 1       | 0.5       | 0.5    | 0.5      | 0.417     | 4 | 2024-01-10 10:00:00
5  | 1       | 0.4       | 0.5    | 0.444    | 0.333     | 5 | 2024-01-10 10:00:00
6  | 2       | 1.0       | 0.33   | 0.5      | 1.0       | 1 | 2024-01-10 10:05:00
7  | 2       | 0.5       | 0.33   | 0.4      | 0.5       | 2 | 2024-01-10 10:05:00
...
```

---

### 7.3 Retrieval & Aggregation Queries

#### Query 1: Get Overall Average Metrics

```python
# Dari evaluation_service.py → calculate_mean_metrics()

def calculate_mean_metrics(self, evaluation_data: list[dict]):
    if not evaluation_data:
        return {
            "precision": 0,
            "recall": 0,
            "f1_score": 0,
            "map": 0
        }
    
    n = len(evaluation_data)
    
    # Calculate average across all records
    mean_precision = sum(d["precision"] for d in evaluation_data) / n
    mean_recall = sum(d["recall"] for d in evaluation_data) / n
    mean_f1 = sum(d["f1_score"] or 0 for d in evaluation_data) / n
    mean_map = sum(d["map_score"] or 0 for d in evaluation_data) / n
    
    return {
        "precision": mean_precision,
        "recall": mean_recall,
        "f1_score": mean_f1,
        "map": mean_map
    }
```

**Contoh Query ke Database**:

```sql
SELECT 
    AVG(precision) as average_precision,
    AVG(recall) as average_recall,
    AVG(f1_score) as average_f1_score,
    AVG(mean_average_precision) as average_map
FROM evaluation_results;
```

**Sample Result**:

```
average_precision | average_recall | average_f1_score | average_map
------------------|----------------|------------------|-------------
0.7234             | 0.5678         | 0.6345           | 0.6123
```

---

#### Query 2: Get Metrics Grouped by K Value

```python
# Dari evaluation_service.py → calculate_average_metrics_by_k()

def calculate_average_metrics_by_k(self):
    """
    Calculate average evaluation metrics for each k value
    """
    
    # Get unique user count
    unique_user_count = self.rec_log_repo.get_unique_user_count()
    
    # Get aggregated metrics per k
    metrics_by_k_data = self.eval_repo.get_metrics_by_k()
    
    metrics_by_k = []
    
    for row in metrics_by_k_data:
        k = row.k
        count = row.count  # Number of records for this k
        
        # Calculate averages
        avg_precision = row.sum_precision / count if count > 0 else 0
        avg_recall = row.sum_recall / count if count > 0 else 0
        avg_f1_score = row.sum_f1_score / count if count > 0 else 0
        avg_map = row.sum_map / count if count > 0 else 0
        
        # Ensure values in range [0, 1]
        avg_precision = max(0.0, min(1.0, avg_precision))
        avg_recall = max(0.0, min(1.0, avg_recall))
        avg_f1_score = max(0.0, min(1.0, avg_f1_score))
        avg_map = max(0.0, min(1.0, avg_map))
        
        metrics_by_k.append({
            "k": k,
            "average_precision": round(avg_precision, 4),
            "average_recall": round(avg_recall, 4),
            "average_f1_score": round(avg_f1_score, 4),
            "average_map": round(avg_map, 4),
            "count": count
        })
    
    metrics_by_k.sort(key=lambda x: x["k"])
    
    return {
        "total_users": unique_user_count,
        "metrics_by_k": metrics_by_k
    }
```

**SQL Query**:

```sql
SELECT 
    k,
    COUNT(*) as count,
    SUM(precision) as sum_precision,
    SUM(recall) as sum_recall,
    SUM(f1_score) as sum_f1_score,
    SUM(mean_average_precision) as sum_map
FROM evaluation_results
GROUP BY k
ORDER BY k;
```

**Sample Result**:

```
k | count | sum_precision | sum_recall | sum_f1_score | sum_map
--|-------|---------------|------------|--------------|----------
1 | 3     | 3.0           | 0.92       | 1.4          | 3.0
2 | 3     | 1.5           | 0.92       | 1.233        | 1.5
3 | 3     | 2.0           | 1.5        | 1.8          | 1.667
4 | 3     | 1.5           | 1.5        | 1.5          | 1.25
5 | 3     | 1.2           | 1.5        | 1.333        | 1.0
```

**After Calculation**:

```
k | avg_precision | avg_recall | avg_f1_score | avg_map | count
--|---------------|------------|--------------|---------|-------
1 | 1.0           | 0.3067     | 0.4667       | 1.0     | 3
2 | 0.5           | 0.3067     | 0.4110       | 0.5     | 3
3 | 0.667         | 0.5        | 0.6          | 0.5557  | 3
4 | 0.5           | 0.5        | 0.5          | 0.4167  | 3
5 | 0.4           | 0.5        | 0.4443       | 0.3333  | 3
```

---

### 7.4 API Endpoints untuk Metrics Retrieval

#### Endpoint 1: Get Average Metrics

```
GET /api/v1/evaluation/average-metrics

Response:
{
  "total_users": 5,
  "average_precision": 0.7234,
  "average_recall": 0.5678,
  "average_f1_score": 0.6345,
  "average_map": 0.6123
}
```

#### Endpoint 2: Get Metrics by K

```
GET /api/v1/evaluation/average-metrics-by-k

Response:
{
  "total_users": 5,
  "metrics_by_k": [
    {
      "k": 1,
      "average_precision": 0.8900,
      "average_recall": 0.3450,
      "average_f1_score": 0.4987,
      "average_map": 0.8900,
      "count": 5
    },
    {
      "k": 3,
      "average_precision": 0.7234,
      "average_recall": 0.5678,
      "average_f1_score": 0.6345,
      "average_map": 0.6789,
      "count": 5
    },
    {
      "k": 5,
      "average_precision": 0.6123,
      "average_recall": 0.7234,
      "average_f1_score": 0.6645,
      "average_map": 0.5567,
      "count": 5
    }
  ]
}
```

#### Endpoint 3: Get Per-User Metrics

```
GET /api/v1/evaluation/precision

Response:
[
  {
    "user_id": 1,
    "username": "user1",
    "k1": 1.0,
    "k2": 0.5,
    "k3": 0.667,
    "k4": 0.5,
    "k5": 0.4
  },
  {
    "user_id": 2,
    "username": "user2",
    "k1": 1.0,
    "k2": 0.667,
    "k3": 0.667,
    "k4": 0.625,
    "k5": 0.6
  }
]
```

---

### 7.5 Interpretasi Hasil Aggregated Metrics

**Dari Contoh di Atas**:

```
Average Metrics:
- Precision: 0.7234 (72.34%) ✓ Bagus
- Recall: 0.5678 (56.78%) ~ Cukup
- F1: 0.6345 (63.45%) ~ Cukup
- MAP: 0.6123 (61.23%) ~ Cukup
```

**Interpretasi**:
1. **Precision tinggi (72%)**: Rekomendasi akurat, user puas dengan kualitas
2. **Recall medium (57%)**: Ada beberapa papers relevan yang terlewat
3. **F1 medium (63%)**: Ada trade-off antara precision dan recall
4. **MAP medium (61%)**: Relevant papers agak tersebar di ranking

**Insight**:
- Sistem bagus di **precision** (tidak memberikan rekomendasi jelek)
- Butuh improve di **recall** (harus menemukan lebih banyak papers relevan)
- Bisa coba: tambah `candidate_size` atau reduce `cosine_similarity_threshold`

---

### 7.6 Trend Analysis

**Jika Lihat Metrics by K**:

```
K | Precision | Recall | F1 | MAP
--|-----------|--------|-----|---------
1 | 0.89      | 0.35   | 0.50| 0.89   ← Hanya top 1 yang bagus
3 | 0.72      | 0.57   | 0.63| 0.68   ← Balanced
5 | 0.61      | 0.72   | 0.66| 0.56   ← Recall naik tapi precision turun
```

**Kesimpulan**:
- **K=1**: Rekomendasi pertama sangat akurat (89%) tapi coverage rendah (35%)
- **K=3**: Sweet spot - balance antara precision dan recall
- **K=5**: Coverage bagus (72%) tapi ada false positives (precision turun ke 61%)

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
