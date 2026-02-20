import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

class ContentBasedFiltering:
    
    def __init__(self, datas, tfidf_vectorizer, tfidf_matrix):
        """
        datas: dataframe berisi title dan abstract
        tfidf_vectorizer: model TF-IDF yang sudah di-fit
        tfidf_matrix: hasil transform seluruh dokumen
        """
        self.datas = datas
        self.vectorizer = tfidf_vectorizer
        self.tfidf_matrix = tfidf_matrix
    
        
    def get_recommendations_by_abstract(self, input_abstract, top_n=5):
        """
        Mengembalikan Top-N rekomendasi berdasarkan abstrak input
        """

        input_vector = self.vectorizer.transform([input_abstract])
        cosine_scores = cosine_similarity(input_vector, self.tfidf_matrix)
        
        cosine_scores = cosine_scores.flatten()
        
        top_indices = np.argsort(cosine_scores)[::-1][:top_n]
        
        results = pd.DataFrame({
            "Title": self.datas.iloc[top_indices]["title"].values,
            "Similarity Score": cosine_scores[top_indices]
        })
        
        return results