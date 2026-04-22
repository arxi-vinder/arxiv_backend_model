import math
from collections import Counter, defaultdict

from app.repositories.paper_repository import PaperRepository


class RecommendationService:

    def __init__(self, paper_repository: PaperRepository):
        self.paper_repository = paper_repository
        self.datas = []
        self.cosine_sim_matrix = []
        self._build_model()

    def _compute_tf(self, tokens):
        tf = Counter(tokens)
        total = len(tokens)
        return {word: count / total for word, count in tf.items()}

    def _compute_idf(self, docs_tokens):
        N = len(docs_tokens)
        df = defaultdict(int)

        for tokens in docs_tokens:
            for word in set(tokens):
                df[word] += 1

        return {
            word: math.log((N + 1) / (freq + 1)) + 1 
            for word, freq in df.items()
        }

    def _compute_tfidf(self, docs_tokens):
        idf = self._compute_idf(docs_tokens)
        tfidf_vectors = []

        for tokens in docs_tokens:
            tf = self._compute_tf(tokens)
            tfidf = {word: tf[word] * idf[word] for word in tf}
            tfidf_vectors.append(tfidf)

        return tfidf_vectors

    def _cosine_similarity(self, vec1, vec2):
        common_words = set(vec1.keys()) & set(vec2.keys())
        dot_product = sum(vec1[w] * vec2[w] for w in common_words)

        norm1 = math.sqrt(sum(v ** 2 for v in vec1.values()))
        norm2 = math.sqrt(sum(v ** 2 for v in vec2.values()))

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    def _build_model(self):
        papers = self.paper_repository.get_abstracts(100)

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
            if p.abstract
        ]


        docs_tokens = [
            p.abstract.split()
            for p in papers
            if p.abstract
        ]


        tfidf_vectors = self._compute_tfidf(docs_tokens)


        n = len(tfidf_vectors)
        cosine_matrix = [[0.0] * n for _ in range(n)]

        for i in range(n):
            for j in range(n):
                cosine_matrix[i][j] = self._cosine_similarity(
                    tfidf_vectors[i],
                    tfidf_vectors[j]
                )

        self.cosine_sim_matrix = cosine_matrix

    def get_recommendations_by_paper_id(self, paper_id: int, top_n: int):

        if not self.datas:
            return {
                "paper_id": paper_id,
                "recommendations": []
            }

        index = next((i for i, d in enumerate(self.datas) if d["id"] == paper_id), None)

        if index is None:
            return {
                "paper_id": paper_id,
                "recommendations": []
            }

        similarity_scores = self.cosine_sim_matrix[index]

        indexed_scores = list(enumerate(similarity_scores))
        indexed_scores.sort(key=lambda x: x[1], reverse=True)

        top_indices = [i for i, _ in indexed_scores if i != index][:top_n]

        results = [
            {
                "id": int(self.datas[i]["id"]),
                "title": self.datas[i]["title"],
                "similarity_score": float(similarity_scores[i])
            }
            for i in top_indices
        ]

        return {
            "paper_id": paper_id,
            "recommendations": results
        }