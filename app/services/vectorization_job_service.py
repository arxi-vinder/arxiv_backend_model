"""
Vectorization Job Service - Manage background vectorization tasks
Handles long-running vectorization processes dengan progress tracking
"""

import uuid
import logging
import threading
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum

logger = logging.getLogger(__name__)


class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class VectorizationJob:
    """Model untuk tracking vectorization job"""

    def __init__(self, job_id: str, batch_size: int = 100):
        self.job_id = job_id
        self.batch_size = batch_size
        self.status = JobStatus.PENDING
        self.created_at = datetime.now()
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None

        # Progress tracking
        self.total_papers = 0
        self.processed_papers = 0
        self.current_batch = 0
        self.total_batches = 0

        # Result
        self.result: Optional[Dict[str, Any]] = None
        self.error_message: Optional[str] = None
        self.error_traceback: Optional[str] = None


class VectorizationJobService:
    """Service untuk manage background vectorization jobs"""

    def __init__(self):
        self.jobs: Dict[str, VectorizationJob] = {}
        self._lock = threading.Lock()

    def create_job(self, batch_size: int = 100) -> str:
        """Create new vectorization job dan return job ID"""
        job_id = str(uuid.uuid4())
        job = VectorizationJob(job_id, batch_size)

        with self._lock:
            self.jobs[job_id] = job

        logger.info(f"Created vectorization job: {job_id}")
        return job_id

    def get_job(self, job_id: str) -> Optional[VectorizationJob]:
        """Get job by ID"""
        with self._lock:
            return self.jobs.get(job_id)

    def start_job(self, job_id: str) -> bool:
        """Mark job as running"""
        job = self.get_job(job_id)
        if not job:
            return False

        with self._lock:
            job.status = JobStatus.RUNNING
            job.started_at = datetime.now()

        return True

    def update_progress(
        self,
        job_id: str,
        total_papers: int,
        processed_papers: int,
        current_batch: int,
        total_batches: int
    ) -> bool:
        """Update job progress"""
        job = self.get_job(job_id)
        if not job:
            return False

        with self._lock:
            job.total_papers = total_papers
            job.processed_papers = processed_papers
            job.current_batch = current_batch
            job.total_batches = total_batches

        return True

    def complete_job(self, job_id: str, result: Dict[str, Any]) -> bool:
        """Mark job as completed dengan result"""
        job = self.get_job(job_id)
        if not job:
            return False

        with self._lock:
            job.status = JobStatus.COMPLETED
            job.completed_at = datetime.now()
            job.result = result

        logger.info(f"Completed vectorization job: {job_id}")
        return True

    def fail_job(self, job_id: str, error_message: str, traceback: str = "") -> bool:
        """Mark job as failed"""
        job = self.get_job(job_id)
        if not job:
            return False

        with self._lock:
            job.status = JobStatus.FAILED
            job.completed_at = datetime.now()
            job.error_message = error_message
            job.error_traceback = traceback

        logger.error(f"Failed vectorization job {job_id}: {error_message}")
        return True

    def cancel_job(self, job_id: str) -> bool:
        """Cancel job (if still pending)"""
        job = self.get_job(job_id)
        if not job:
            return False

        with self._lock:
            if job.status == JobStatus.PENDING:
                job.status = JobStatus.CANCELLED
                job.completed_at = datetime.now()
                return True

        return False

    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job status as dict"""
        job = self.get_job(job_id)
        if not job:
            return None

        elapsed_time = None
        if job.started_at:
            if job.completed_at:
                elapsed_time = (job.completed_at - job.started_at).total_seconds()
            else:
                elapsed_time = (datetime.now() - job.started_at).total_seconds()

        progress_percentage = 0
        if job.total_papers > 0:
            progress_percentage = round((job.processed_papers / job.total_papers) * 100, 2)

        status_dict = {
            "job_id": job.job_id,
            "status": job.status.value,
            "created_at": job.created_at.isoformat(),
            "started_at": job.started_at.isoformat() if job.started_at else None,
            "completed_at": job.completed_at.isoformat() if job.completed_at else None,
            "progress": {
                "total_papers": job.total_papers,
                "processed_papers": job.processed_papers,
                "progress_percentage": progress_percentage,
                "current_batch": job.current_batch,
                "total_batches": job.total_batches
            },
            "elapsed_time_seconds": elapsed_time,
            "batch_size": job.batch_size
        }

        if job.status == JobStatus.COMPLETED and job.result:
            status_dict["result"] = job.result

        if job.status == JobStatus.FAILED:
            status_dict["error"] = {
                "message": job.error_message,
                "traceback": job.error_traceback
            }

        return status_dict

    def cleanup_old_jobs(self, keep_hours: int = 24) -> int:
        """Clean up completed jobs older than keep_hours"""
        now = datetime.now()
        removed_count = 0

        job_ids_to_remove = []
        with self._lock:
            for job_id, job in self.jobs.items():
                if job.status in (JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED):
                    if job.completed_at:
                        age_hours = (now - job.completed_at).total_seconds() / 3600
                        if age_hours > keep_hours:
                            job_ids_to_remove.append(job_id)

            for job_id in job_ids_to_remove:
                del self.jobs[job_id]
                removed_count += 1

        logger.info(f"Cleaned up {removed_count} old vectorization jobs")
        return removed_count

    def get_all_jobs(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all jobs"""
        with self._lock:
            return {
                job_id: self.get_job_status(job_id)
                for job_id in self.jobs.keys()
            } # type: ignore

    def get_active_jobs_count(self) -> int:
        """Get count of active (pending/running) jobs"""
        with self._lock:
            return sum(
                1 for job in self.jobs.values()
                if job.status in (JobStatus.PENDING, JobStatus.RUNNING)
            )


# Global singleton instance
_job_service: Optional[VectorizationJobService] = None


def get_vectorization_job_service() -> VectorizationJobService:
    """Get or create global job service instance"""
    global _job_service
    if _job_service is None:
        _job_service = VectorizationJobService()
    return _job_service
