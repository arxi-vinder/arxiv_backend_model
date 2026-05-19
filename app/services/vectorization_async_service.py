"""
Vectorization Async Service - Handle long-running vectorization in background
Menggunakan threading untuk menjalankan vectorization tanpa blocking HTTP request
"""

import logging
import threading
import traceback
from typing import Optional
from app.db.database import SessionLocal
from app.repositories.paper_repository import PaperRepository
from app.services.recommendation_service import RecommendationService
from app.services.vectorization_job_service import get_vectorization_job_service

logger = logging.getLogger(__name__)


class VectorizationAsyncService:
    """Service untuk handle async vectorization dengan background threads"""

    def __init__(self):
        self.job_service = get_vectorization_job_service()
        self._threads: dict = {}

    def start_vectorization_async(self, job_id: str, batch_size: int = 100) -> bool:
        """
        Start vectorization di background thread
        Return True jika thread berhasil distart
        """
        if job_id in self._threads:
            logger.warning(f"Job {job_id} already running")
            return False

        # Create dan start thread
        thread = threading.Thread(
            target=self._vectorization_worker,
            args=(job_id, batch_size),
            daemon=False,
            name=f"vectorization-{job_id}"
        )

        self._threads[job_id] = thread
        thread.start()

        logger.info(f"Started vectorization thread for job {job_id}")
        return True

    def _vectorization_worker(self, job_id: str, batch_size: int):
        """Worker function yang dijalankan di background thread"""
        logger.info(f"[Worker] Starting vectorization for job {job_id}")

        try:
            # Mark job as running
            self.job_service.start_job(job_id)

            # Create database session
            db = SessionLocal()

            try:
                # Initialize repositories
                paper_repo = PaperRepository(db)
                total_papers = paper_repo.get_total_papers_count()

                logger.info(f"[Worker] Found {total_papers} papers in database")

                if total_papers == 0:
                    error_msg = "No papers found in database"
                    logger.warning(f"[Worker] {error_msg}")
                    self.job_service.fail_job(job_id, error_msg)
                    return

                # Create recommendation service dengan custom progress callback
                rec_service = RecommendationService(
                    paper_repository=paper_repo,
                    auto_build=False,
                    use_cache=True
                )

                logger.info(f"[Worker] Building model with batch size: {batch_size}")

                # Calculate total batches
                total_batches = (total_papers + batch_size - 1) // batch_size

                # Custom callback untuk track progress
                def progress_callback(processed_count: int, batch_num: int):
                    """Callback untuk update progress"""
                    self.job_service.update_progress(
                        job_id=job_id,
                        total_papers=total_papers,
                        processed_papers=processed_count,
                        current_batch=batch_num,
                        total_batches=total_batches
                    )

                # Build model dengan batch processing (sudah verbose)
                rec_service.build_full_model_batch(
                    batch_size=batch_size,
                    verbose=True
                )

                # Get final statistics
                final_stats = {
                    "total_papers_processed": total_papers,
                    "cosine_matrix_size": f"{len(rec_service.cosine_sim_matrix)}x{len(rec_service.cosine_sim_matrix)}",
                    "batch_size_used": batch_size,
                    "cached": True
                }

                logger.info(f"[Worker] Vectorization completed successfully for job {job_id}")
                logger.info(f"[Worker] Stats: {final_stats}")

                # Mark job as completed
                self.job_service.complete_job(job_id, final_stats)

            finally:
                db.close()

        except Exception as e:
            error_message = str(e)
            error_traceback = traceback.format_exc()

            logger.error(f"[Worker] Error during vectorization for job {job_id}:")
            logger.error(f"[Worker] {error_message}")
            logger.error(f"[Worker] Traceback:\n{error_traceback}")

            # Mark job as failed
            self.job_service.fail_job(job_id, error_message, error_traceback)

    def get_job_status(self, job_id: str) -> Optional[dict]:
        """Get status of a vectorization job"""
        return self.job_service.get_job_status(job_id)

    def cancel_job(self, job_id: str) -> bool:
        """Cancel a pending job (cannot cancel running job)"""
        success = self.job_service.cancel_job(job_id)

        if job_id in self._threads:
            # Remove dari threads dict
            thread = self._threads[job_id]
            if not thread.is_alive():
                del self._threads[job_id]

        return success

    def is_job_running(self, job_id: str) -> bool:
        """Check if job is currently running"""
        if job_id in self._threads:
            return self._threads[job_id].is_alive()
        return False

    def get_active_jobs(self) -> dict:
        """Get all active jobs"""
        return self.job_service.get_all_jobs()

    def get_active_jobs_count(self) -> int:
        """Get count of active jobs"""
        return self.job_service.get_active_jobs_count()

    def cleanup_old_jobs(self, keep_hours: int = 24) -> int:
        """Cleanup old completed jobs"""
        return self.job_service.cleanup_old_jobs(keep_hours)


# Global singleton instance
_async_service: Optional[VectorizationAsyncService] = None


def get_vectorization_async_service() -> VectorizationAsyncService:
    """Get or create global async service instance"""
    global _async_service
    if _async_service is None:
        _async_service = VectorizationAsyncService()
    return _async_service
