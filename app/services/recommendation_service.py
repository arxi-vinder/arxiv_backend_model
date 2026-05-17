import math
from collections import Counter, defaultdict
import logging

from app.repositories.paper_repository import PaperRepository
from app.services.vectorization_cache_service import VectorizationCacheService
import re
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

logger = logging.getLogger(__name__)

class RecommendationService:

    def __init__(self, paper_repository: PaperRepository, auto_build: bool = True, use_cache: bool = True):
        self.paper_repository = paper_repository
        self.datas = []
        self.cosine_sim_matrix = []
        self.cache_service = VectorizationCacheService()
        self.use_cache = use_cache

        if auto_build:
            self._build_model_with_cache()


    def preprocess(self, text):

        stemmer = PorterStemmer()
        stop_words = set(stopwords.words("english"))
        text = text.lower()
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        tokens = text.split()
        tokens = [
            stemmer.stem(word)
            for word in tokens
            if word not in stop_words
        ]

        return tokens

    def _compute_tf(self, tokens):

        print("\n=== TERM FREQUENCY (TF) ===")
        print("TOKENS:", tokens)

        tf = Counter(tokens)
        total = len(tokens)

        tf_result = {
            word: count / total
            for word, count in tf.items()
        }

        for word, value in sorted(tf_result.items()):
            print(f"TF[{word}] = {value:.6f}")

        return tf_result


    def _compute_idf(self, docs_tokens):

        print("\n=== INVERSE DOCUMENT FREQUENCY (IDF) ===")

        N = len(docs_tokens)

        print("TOTAL DOCUMENT:", N)

        df = defaultdict(int)

        for idx, tokens in enumerate(docs_tokens):

            print(f"\n[DOC {idx}]")
            print(tokens)

            for word in set(tokens):
                df[word] += 1

        print("\n=== DOCUMENT FREQUENCY ===")

        for word, freq in sorted(df.items()):
            print(f"DF[{word}] = {freq}")

        idf_result = {
            word: math.log((N + 1) / (freq + 1)) + 1
            for word, freq in df.items()
        }

        print("\n=== HASIL IDF ===")

        for word, value in sorted(idf_result.items()):
            print(f"IDF[{word}] = {value:.6f}")

        return idf_result
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

    def _build_model_with_cache(self):
        """Build model dengan strategi cache: load dari cache atau build default 100"""
        if self.use_cache and self.cache_service.is_cache_valid():
            print("\n[CACHE] Trying to load precomputed vectors...")
            cached_data = self.cache_service.load_precomputed_vectors()
            if cached_data:
                self.datas = cached_data.get("datas", [])
                self.cosine_sim_matrix = cached_data.get("cosine_matrix", [])
                logger.info(f"Model loaded from cache: {len(self.datas)} papers")
                return

        print("\n[BUILD] No cache found, building default model (100 papers)...")
        self._build_model()

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

        print("\n=== ABSTRACT YANG DIPROSES ===")

        docs_tokens = []

        for idx, p in enumerate(papers):
            if p.abstract:
                print(f"\n[DOC {idx}]")
                print("TITLE     :", p.title)
                print("ABSTRACT  :", p.abstract)

                tokens = self.preprocess(p.abstract)

                print("TOKENS    :", tokens)

                docs_tokens.append(tokens)

        print("\n=== TF-IDF VECTORIZATION ===")

        tfidf_vectors = self._compute_tfidf(docs_tokens)

        for idx, vector in enumerate(tfidf_vectors):
            print(f"\n[TF-IDF DOC {idx}]")

            for word, value in sorted(vector.items()):
                print(f"{word:<20} -> {value:.6f}")

        n = len(tfidf_vectors)
        cosine_matrix = [[0.0] * n for _ in range(n)]

        print("\n=== COSINE SIMILARITY ===")

        for i in range(n):
            for j in range(n):
                cosine_matrix[i][j] = self._cosine_similarity(
                    tfidf_vectors[i],
                    tfidf_vectors[j]
                )

                print(
                    f"Similarity Doc-{i} vs Doc-{j} "
                    f"= {cosine_matrix[i][j]:.6f}"
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

    def build_full_model_batch(self, batch_size: int = 100, verbose: bool = True):
        """Process all papers dengan batch processing untuk optimasi memori"""
        total_count = self.paper_repository.get_total_papers_count()

        if verbose:
            logger.info(f"Starting full vectorization for {total_count} papers")
            print(f"\n=== FULL VECTORIZATION ===")
            print(f"Total papers to process: {total_count}")

        all_datas = []
        all_tfidf_vectors = []
        offset = 0

        while offset < total_count:
            if verbose:
                print(f"\nProcessing batch: {offset + 1} - {min(offset + batch_size, total_count)}")
                logger.info(f"Processing batch from {offset} to {offset + batch_size}")

            papers_batch = self.paper_repository.get_abstracts_batch(offset, batch_size)

            if not papers_batch:
                break

            docs_tokens = []

            for p in papers_batch:
                if p.abstract:
                    all_datas.append({
                        "id": p.id,
                        "title": p.title,
                        "abstract": p.abstract
                    })

                    tokens = self.preprocess(p.abstract)
                    docs_tokens.append(tokens)

            if docs_tokens:
                tfidf_vectors = self._compute_tfidf(docs_tokens)
                all_tfidf_vectors.extend(tfidf_vectors)

            offset += batch_size

        self.datas = all_datas

        if verbose:
            print(f"\nTotal papers with abstracts: {len(all_datas)}")
            logger.info(f"Total papers processed: {len(all_datas)}")

        if not all_tfidf_vectors:
            self.cosine_sim_matrix = []
            if verbose:
                print("No abstracts found to vectorize")
            return

        n = len(all_tfidf_vectors)
        cosine_matrix = [[0.0] * n for _ in range(n)]

        if verbose:
            print(f"\nComputing cosine similarity matrix ({n}x{n})...")
            logger.info(f"Computing cosine similarity for {n} documents")

        for i in range(n):
            if verbose and (i + 1) % max(1, n // 10) == 0:
                progress = ((i + 1) / n) * 100
                print(f"Progress: {progress:.1f}%")
                logger.info(f"Cosine similarity progress: {progress:.1f}%")

            for j in range(n):
                cosine_matrix[i][j] = self._cosine_similarity(
                    all_tfidf_vectors[i],
                    all_tfidf_vectors[j]
                )

        self.cosine_sim_matrix = cosine_matrix

        if verbose:
            print("\n=== VECTORIZATION COMPLETE ===")
            logger.info("Full vectorization completed successfully")

        # Simpan ke cache
        if self.use_cache:
            if verbose:
                print("\n[CACHE] Saving precomputed vectors to disk...")
            self.cache_service.save_precomputed_vectors(all_datas, all_tfidf_vectors, cosine_matrix)
            if verbose:
                cache_info = self.cache_service.get_cache_info()
                print(f"\nCache Info:")
                for key, value in cache_info.items():
                    print(f"  - {key}: {value}")