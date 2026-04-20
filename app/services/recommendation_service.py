import math
from typing import Counter

from sklearn.feature_extraction.text import defaultdict

from app.repositories.paper_repository import PaperRepository


class RecommendationService:

    def __init__(self, paper_repository: PaperRepository):
        self.paper_repository = paper_repository
        self.datas = []
        self.tfidf_matrix = []
        self.cosine_sim_matrix = []
        self._build_model()

    def _tokenize(self, text: str):
        return text.lower().split()

    def _compute_tf(self, tokens):
        tf = Counter(tokens)
        total = len(tokens)
        return {word: count / total for word, count in tf.items()}

    def _compute_idf(self, docs_tokens):
        N = len(docs_tokens)
        df = defaultdict(int)

        for tokens in docs_tokens:
            unique_words = set(tokens)
            for word in unique_words:
                df[word] += 1

        idf = {}
        for word, freq in df.items():
            if freq == 0:
                continue
            idf[word] = math.log(N / freq)

        return idf
    def _compute_tfidf(self, docs_tokens):
        idf = self._compute_idf(docs_tokens)
        tfidf_vectors = []

        for tokens in docs_tokens:
            tf = self._compute_tf(tokens)
            tfidf = {}
            for word, val in tf.items():
                tfidf[word] = val * idf.get(word, 0)
            tfidf_vectors.append(tfidf)

        return tfidf_vectors

    def _cosine_similarity(self, vec1, vec2):
        # dot product
        common_words = set(vec1.keys()) & set(vec2.keys())
        dot_product = sum(vec1[w] * vec2[w] for w in common_words)

        # norm
        norm1 = math.sqrt(sum(v ** 2 for v in vec1.values()))
        norm2 = math.sqrt(sum(v ** 2 for v in vec2.values()))

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    def _build_model(self):
        papers = self.paper_repository.getPaper(100)

        if not papers:
            self.datas = []
            self.cosine_sim_matrix = []
            return

        self.datas = [
            {
                "id": p.id,
                "title": p.title,
                "abstract": p.abstract
            }
            for p in papers
        ]

        # 1. Tokenisasi
        docs_tokens = [
            self._tokenize(data["abstract"])
            for data in self.datas
        ]

        # 2. TF-IDF manual
        tfidf_vectors = self._compute_tfidf(docs_tokens)

        # 3. Cosine similarity matrix
        n = len(tfidf_vectors)
        cosine_matrix = [[0.0 for _ in range(n)] for _ in range(n)]

        for i in range(n):
            for j in range(n):
                cosine_matrix[i][j] = self._cosine_similarity(
                    tfidf_vectors[i],
                    tfidf_vectors[j]
                )

        self.cosine_sim_matrix = cosine_matrix

    def get_recommendations_by_paper_id(self, paper_id: int, top_n: int = 5):

        # karena sekarang list, bukan DataFrame
        if not self.datas:
            return []

        # cari index berdasarkan id
        index = None
        for i, data in enumerate(self.datas):
            if data["id"] == paper_id:
                index = i
                break

        if index is None:
            return []

        similarity_scores = self.cosine_sim_matrix[index]

        # ambil top N (manual sort)
        indexed_scores = list(enumerate(similarity_scores))

        # sort descending berdasarkan similarity
        indexed_scores.sort(key=lambda x: x[1], reverse=True)

        # skip index sendiri (posisi pertama biasanya dirinya sendiri)
        top_indices = [i for i, _ in indexed_scores if i != index][:top_n]

        results = []

        for i in top_indices:
            results.append({
                "id": int(self.datas[i]["id"]),
                "title": self.datas[i]["title"],
                "similarity_score": float(similarity_scores[i])
            })

        return {
            "paper_id": paper_id,
            "recommendations": results
        }
