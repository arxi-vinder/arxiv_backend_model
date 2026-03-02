from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
import pandas as pd

from app.repositories.paper_repository import PaperRepository


class RecommendationService:

    def __init__(self, paper_repository:PaperRepository):
        self.paper_repository = paper_repository
        self.datas = pd.DataFrame()
        self.tfidf_matrix = None
        self.cosine_sim_matrix = np.array([])

        self._build_model()

    def _build_model(self):
        """
        Ambil data dari repository lalu build TF-IDF + cosine
        """

        papers = self.paper_repository.getPaper(100)

        if not papers:
            self.datas = pd.DataFrame()
            self.cosine_sim_matrix = np.array([])
            return

        self.datas = pd.DataFrame([
            {
                "id": p.id,
                "title": p.title,
                "abstract": p.abstract
            }
            for p in papers
        ])

        vectorizer = TfidfVectorizer(stop_words="english")
        self.tfidf_matrix = vectorizer.fit_transform(self.datas["abstract"])

        self.cosine_sim_matrix = cosine_similarity(self.tfidf_matrix)

    def get_recommendations_by_paper_id(self, paper_id: int, top_n: int = 5):

        if self.datas.empty:
            return []

        index_list = self.datas.index[self.datas["id"] == paper_id].tolist()

        if not index_list:
            return []

        index = index_list[0]

        similarity_scores = self.cosine_sim_matrix[index]
        top_indices = np.argsort(similarity_scores)[::-1][1:top_n+1]

        results = []

        for i in top_indices:
            results.append({
                "id": int(self.datas.iloc[i]["id"]),
                "title": self.datas.iloc[i]["title"],
                "similarity_score": float(similarity_scores[i])
            })

        return {
            "paper_id": paper_id,
            "recommendations": results
        }