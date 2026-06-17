import logging
from sqlmodel import Session, select
from app.model.vectorization_cache import VectorizationCache
from datetime import datetime

logger = logging.getLogger(__name__)

class VectorizationCacheRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_cache(self, cache_key: str = "default"):
        """Get cache by key"""
        try:
            statement = select(VectorizationCache).where(
                VectorizationCache.cache_key == cache_key
            )
            return self.session.exec(statement).first()
        except Exception as e:
            logger.error(f"Error getting cache: {str(e)}")
            return None

    def save_cache(self, vectors_data: bytes, metadata: dict, total_papers: int, matrix_size: int, cache_key: str = "default"):
        """Save cache to database"""
        try:
            existing = self.get_cache(cache_key)

            file_size_bytes = len(vectors_data)

            if existing:
                existing.vectors_data = vectors_data # type: ignore
                existing.metadata = metadata # type: ignore
                existing.total_papers = total_papers # type: ignore
                existing.matrix_size = matrix_size # type: ignore
                existing.file_size_bytes = file_size_bytes # type: ignore
                existing.updated_at = datetime.now() # type: ignore
            else:
                cache_record = VectorizationCache(
                    cache_key=cache_key,
                    vectors_data=vectors_data,
                    metadata=metadata,
                    total_papers=total_papers,
                    matrix_size=matrix_size,
                    file_size_bytes=file_size_bytes
                )
                self.session.add(cache_record)

            self.session.commit()
            logger.info(f"Cache saved successfully: {total_papers} papers, {matrix_size}x{matrix_size} matrix")
            return True

        except Exception as e:
            logger.error(f"Error saving cache: {str(e)}")
            self.session.rollback()
            return False

    def delete_cache(self, cache_key: str = "default"):
        """Delete cache from database"""
        try:
            cache = self.get_cache(cache_key)
            if cache:
                self.session.delete(cache)
                self.session.commit()
                logger.info(f"Cache deleted: {cache_key}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting cache: {str(e)}")
            self.session.rollback()
            return False

    def get_cache_info(self, cache_key: str = "default"):
        """Get cache metadata"""
        try:
            cache = self.get_cache(cache_key)
            if not cache:
                return None

            return {
                "total_papers": cache.total_papers,
                "matrix_size": cache.matrix_size,
                "file_size_mb": round(cache.file_size_bytes / (1024 * 1024), 2), # type: ignore
                "created_at": cache.created_at.isoformat() if cache.created_at else None, # type: ignore
                "updated_at": cache.updated_at.isoformat() if cache.updated_at else None # type: ignore
            }
        except Exception as e:
            logger.error(f"Error getting cache info: {str(e)}")
            return None
