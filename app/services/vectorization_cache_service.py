import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Optional
import pickle

logger = logging.getLogger(__name__)

CACHE_DIR = Path("app/cache/vectorization")
VECTORS_CACHE_FILE = CACHE_DIR / "precomputed_vectors.pkl"
METADATA_FILE = CACHE_DIR / "metadata.json"


class VectorizationCacheService:
    def __init__(self):
        self.cache_dir = CACHE_DIR
        self.vectors_file = VECTORS_CACHE_FILE
        self.metadata_file = METADATA_FILE
        self._ensure_cache_dir()

    def _ensure_cache_dir(self):
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Cache directory ready: {self.cache_dir}")

    def save_precomputed_vectors(self, datas: list, tfidf_vectors: list, cosine_matrix: list):
        try:
            cache_data = {
                "datas": datas,
                "tfidf_vectors": tfidf_vectors,
                "cosine_matrix": cosine_matrix
            }


            with open(self.vectors_file, "wb") as f:
                pickle.dump(cache_data, f)

            metadata = {
                "total_papers": len(datas),
                "matrix_size": len(cosine_matrix),
                "saved_at": datetime.now().isoformat(),
                "cache_file": str(self.vectors_file)
            }

            with open(self.metadata_file, "w") as f:
                json.dump(metadata, f, indent=2)

            logger.info(f"Vectors cached: {len(datas)} papers")
            print(f"\n[OK] Vectors cached successfully!")
            print(f"  - Papers: {len(datas)}")
            print(f"  - Matrix: {len(cosine_matrix)}x{len(cosine_matrix)}")
            print(f"  - Cache file: {self.vectors_file}")

            return True

        except Exception as e:
            logger.error(f"Error saving cache: {str(e)}")
            print(f"[ERROR] Error saving cache: {str(e)}")
            return False

    def load_precomputed_vectors(self) -> Optional[dict]:
        try:
            if not self.vectors_file.exists():
                logger.warning("Cache file not found")
                return None

            with open(self.vectors_file, "rb") as f:
                cache_data: dict = pickle.load(f)

            datas = cache_data.get("datas", [])
            logger.info(f"Vectors loaded from cache: {len(datas)} papers")
            print(f"\n[OK] Vectors loaded from cache!")
            print(f"  - Papers: {len(datas)}")

            return cache_data

        except Exception as e:
            logger.error(f"Error loading cache: {str(e)}")
            print(f"[ERROR] Error loading cache: {str(e)}")
            return None

    def get_metadata(self) -> Optional[dict]:
        """Get cache metadata"""
        try:
            if not self.metadata_file.exists():
                return None

            with open(self.metadata_file, "r") as f:
                return json.load(f)

        except Exception as e:
            logger.error(f"Error reading metadata: {str(e)}")
            return None

    def is_cache_valid(self) -> bool:
        return self.vectors_file.exists() and self.metadata_file.exists()

    def clear_cache(self):
        try:
            if self.vectors_file.exists():
                self.vectors_file.unlink()
            if self.metadata_file.exists():
                self.metadata_file.unlink()
            logger.info("Cache cleared")
            print("[OK] Cache cleared")
            return True
        except Exception as e:
            logger.error(f"Error clearing cache: {str(e)}")
            print(f"[ERROR] Error clearing cache: {str(e)}")
            return False

    def get_cache_info(self) -> dict:
        if not self.is_cache_valid():
            return {"status": "no_cache"}

        try:
            metadata = self.get_metadata()
            if not metadata:
                return {"status": "no_cache"}

            file_size_mb = self.vectors_file.stat().st_size / (1024 * 1024)

            return {
                "status": "cached",
                "total_papers": metadata.get("total_papers", 0),
                "matrix_size": metadata.get("matrix_size", 0),
                "file_size_mb": round(file_size_mb, 2),
                "saved_at": metadata.get("saved_at"),
                "cache_file": str(self.vectors_file)
            }
        except Exception as e:
            logger.error(f"Error getting cache info: {str(e)}")
            return {"status": "error", "message": str(e)}
