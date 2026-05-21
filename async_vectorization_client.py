"""
Async Vectorization Client - Python SDK untuk async vectorization API
Provides easy-to-use client untuk start dan monitor vectorization jobs
"""

import requests
import time
import json
from typing import Optional, Dict, Any, Callable
from dataclasses import dataclass
from datetime import datetime


@dataclass
class VectorizationProgress:
    """Progress information untuk vectorization job"""
    total_papers: int
    processed_papers: int
    progress_percentage: float
    current_batch: int
    total_batches: int

    def __repr__(self) -> str:
        return f"Progress({self.progress_percentage}% - {self.processed_papers}/{self.total_papers} papers)"


@dataclass
class JobStatus:
    """Status information untuk vectorization job"""
    job_id: str
    status: str  # pending | running | completed | failed | cancelled
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    progress: VectorizationProgress
    elapsed_time_seconds: Optional[float]
    batch_size: int
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    error_traceback: Optional[str] = None

    def is_complete(self) -> bool:
        """Check if job is completed (success or failure)"""
        return self.status in ("completed", "failed", "cancelled")

    def is_success(self) -> bool:
        """Check if job completed successfully"""
        return self.status == "completed"

    def is_failed(self) -> bool:
        """Check if job failed"""
        return self.status == "failed"

    def is_running(self) -> bool:
        """Check if job is currently running"""
        return self.status == "running"

    def __repr__(self) -> str:
        return f"JobStatus({self.job_id[:8]}... | {self.status} | {self.progress.progress_percentage}%)"


class AsyncVectorizationClient:
    """Client untuk async vectorization API"""

    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        timeout: int = 30
    ):
        """
        Initialize client

        Args:
            base_url: Base URL dari API server (default: http://localhost:8000)
            timeout: Request timeout dalam detik (default: 30)
        """
        self.base_url = base_url
        self.api_base = f"{base_url}/api/v1"
        self.timeout = timeout

    def start_vectorization(self, batch_size: int = 100) -> str:
        """
        Start vectorization job

        Args:
            batch_size: Ukuran batch untuk processing (default: 100)

        Returns:
            Job ID sebagai string

        Raises:
            requests.RequestException: Jika request gagal
        """
        try:
            response = requests.post(
                f"{self.api_base}/vectorize-async",
                params={"batch_size": batch_size},
                timeout=self.timeout
            )
            response.raise_for_status()

            data = response.json()
            if data.get("status") != "success":
                raise RuntimeError(f"API error: {data.get('message', 'Unknown error')}")

            return data["data"]["job_id"]

        except requests.RequestException as e:
            raise RuntimeError(f"Failed to start vectorization: {str(e)}")

    def get_status(self, job_id: str) -> JobStatus:
        """
        Get job status

        Args:
            job_id: Job ID dari start_vectorization

        Returns:
            JobStatus object

        Raises:
            requests.RequestException: Jika request gagal
            ValueError: Jika job tidak ditemukan
        """
        try:
            response = requests.get(
                f"{self.api_base}/vectorization-job/{job_id}/status",
                timeout=self.timeout
            )
            response.raise_for_status()

            data = response.json()
            job_data = data.get("data")

            if not job_data:
                raise ValueError(f"Job {job_id} not found")

            # Parse timestamps
            created_at = datetime.fromisoformat(job_data["created_at"])
            started_at = datetime.fromisoformat(job_data["started_at"]) if job_data.get("started_at") else None
            completed_at = datetime.fromisoformat(job_data["completed_at"]) if job_data.get("completed_at") else None

            # Parse progress
            progress_data = job_data["progress"]
            progress = VectorizationProgress(
                total_papers=progress_data["total_papers"],
                processed_papers=progress_data["processed_papers"],
                progress_percentage=progress_data["progress_percentage"],
                current_batch=progress_data["current_batch"],
                total_batches=progress_data["total_batches"]
            )

            # Parse error jika ada
            error_data = job_data.get("error", {})

            return JobStatus(
                job_id=job_data["job_id"],
                status=job_data["status"],
                created_at=created_at,
                started_at=started_at,
                completed_at=completed_at,
                progress=progress,
                elapsed_time_seconds=job_data.get("elapsed_time_seconds"),
                batch_size=job_data["batch_size"],
                result=job_data.get("result"),
                error_message=error_data.get("message"),
                error_traceback=error_data.get("traceback")
            )

        except requests.RequestException as e:
            raise RuntimeError(f"Failed to get status: {str(e)}")

    def cancel(self, job_id: str) -> bool:
        """
        Cancel pending job

        Args:
            job_id: Job ID untuk di-cancel

        Returns:
            True jika berhasil, False jika job tidak pending

        Raises:
            requests.RequestException: Jika request gagal
        """
        try:
            response = requests.delete(
                f"{self.api_base}/vectorization-job/{job_id}/cancel",
                timeout=self.timeout
            )
            return response.status_code == 200

        except requests.RequestException as e:
            raise RuntimeError(f"Failed to cancel job: {str(e)}")

    def wait_for_completion(
        self,
        job_id: str,
        timeout: int = 3600,
        check_interval: int = 5,
        on_progress: Optional[Callable[[JobStatus], None]] = None
    ) -> JobStatus:
        """
        Wait for job completion dengan polling

        Args:
            job_id: Job ID untuk di-wait
            timeout: Timeout dalam detik (default: 3600 = 1 jam)
            check_interval: Interval antar polling dalam detik (default: 5)
            on_progress: Optional callback untuk progress updates

        Returns:
            Final JobStatus

        Raises:
            TimeoutError: Jika job tidak complete dalam timeout
            RuntimeError: Jika terjadi error saat polling
        """
        start_time = time.time()

        while True:
            elapsed = time.time() - start_time

            # Check timeout
            if elapsed > timeout:
                raise TimeoutError(
                    f"Job {job_id} did not complete within {timeout} seconds"
                )

            try:
                status = self.get_status(job_id)

                # Call progress callback jika ada
                if on_progress:
                    on_progress(status)

                # Check jika job complete
                if status.is_complete():
                    return status

                # Wait before next poll
                time.sleep(check_interval)

            except ValueError:
                # Job tidak ditemukan
                raise RuntimeError(f"Job {job_id} not found")

    def wait_with_progress_bar(
        self,
        job_id: str,
        timeout: int = 3600,
        check_interval: int = 5
    ) -> JobStatus:
        """
        Wait for completion dengan progress bar di console

        Args:
            job_id: Job ID untuk di-wait
            timeout: Timeout dalam detik
            check_interval: Interval antar polling

        Returns:
            Final JobStatus
        """
        def print_progress(status: JobStatus):
            """Print progress bar"""
            percentage = status.progress.progress_percentage
            elapsed = status.elapsed_time_seconds or 0

            # Simple progress bar
            bar_length = 50
            filled = int(bar_length * percentage / 100)
            bar = "█" * filled + "░" * (bar_length - filled)

            print(
                f"\r[{bar}] {percentage:6.1f}% | "
                f"{status.progress.processed_papers}/{status.progress.total_papers} papers | "
                f"Elapsed: {int(elapsed)}s",
                end="", flush=True
            )

        status = self.wait_for_completion(
            job_id,
            timeout=timeout,
            check_interval=check_interval,
            on_progress=print_progress
        )

        print()  # New line after progress bar
        return status

    def get_all_jobs(self) -> Dict[str, JobStatus]:
        """
        Get all vectorization jobs

        Returns:
            Dictionary berisi semua jobs
        """
        try:
            response = requests.get(
                f"{self.api_base}/vectorization-jobs",
                timeout=self.timeout
            )
            response.raise_for_status()

            data = response.json()
            jobs_data = data.get("data", {})

            # Parse semua jobs
            jobs = {}
            for job_id, job_info in jobs_data.items():
                try:
                    created_at = datetime.fromisoformat(job_info["created_at"])
                    started_at = datetime.fromisoformat(job_info["started_at"]) if job_info.get("started_at") else None
                    completed_at = datetime.fromisoformat(job_info["completed_at"]) if job_info.get("completed_at") else None

                    progress_data = job_info["progress"]
                    progress = VectorizationProgress(
                        total_papers=progress_data["total_papers"],
                        processed_papers=progress_data["processed_papers"],
                        progress_percentage=progress_data["progress_percentage"],
                        current_batch=progress_data["current_batch"],
                        total_batches=progress_data["total_batches"]
                    )

                    error_data = job_info.get("error", {})

                    jobs[job_id] = JobStatus(
                        job_id=job_info["job_id"],
                        status=job_info["status"],
                        created_at=created_at,
                        started_at=started_at,
                        completed_at=completed_at,
                        progress=progress,
                        elapsed_time_seconds=job_info.get("elapsed_time_seconds"),
                        batch_size=job_info["batch_size"],
                        result=job_info.get("result"),
                        error_message=error_data.get("message"),
                        error_traceback=error_data.get("traceback")
                    )
                except Exception as e:
                    print(f"Warning: Failed to parse job {job_id}: {str(e)}")

            return jobs

        except requests.RequestException as e:
            raise RuntimeError(f"Failed to get all jobs: {str(e)}")

    def print_status(self, status: JobStatus):
        """Print status dengan format yang rapi"""
        print(f"\n{'='*60}")
        print(f"Job Status: {status.job_id[:8]}...")
        print(f"{'='*60}")
        print(f"Status: {status.status}")
        print(f"Created: {status.created_at.isoformat()}")
        if status.started_at:
            print(f"Started: {status.started_at.isoformat()}")
        if status.completed_at:
            print(f"Completed: {status.completed_at.isoformat()}")
        print(f"Elapsed time: {status.elapsed_time_seconds}s" if status.elapsed_time_seconds else "Elapsed time: -")
        print(f"\nProgress: {status.progress.progress_percentage}%")
        print(f"Papers: {status.progress.processed_papers}/{status.progress.total_papers}")
        print(f"Batch: {status.progress.current_batch}/{status.progress.total_batches}")

        if status.is_success() and status.result:
            print(f"\nResult:")
            print(json.dumps(status.result, indent=2))

        if status.is_failed():
            print(f"\nError: {status.error_message}")
            if status.error_traceback:
                print(f"Traceback:\n{status.error_traceback}")

        print(f"{'='*60}\n")


# Example usage
if __name__ == "__main__":
    # Initialize client
    client = AsyncVectorizationClient()

    # Example 1: Simple usage
    print("Starting vectorization...")
    job_id = client.start_vectorization(batch_size=100)
    print(f"Job ID: {job_id}")

    # Example 2: Wait dengan progress bar
    print("\nWaiting for completion...")
    try:
        final_status = client.wait_with_progress_bar(
            job_id,
            timeout=3600,
            check_interval=5
        )

        # Print hasil
        if final_status.is_success():
            print("✓ Vectorization completed successfully!")
            print(json.dumps(final_status.result, indent=2))
        elif final_status.is_failed():
            print("✗ Vectorization failed!")
            print(f"Error: {final_status.error_message}")

    except TimeoutError as e:
        print(f"✗ Error: {e}")
        # Optionally cancel the job
        if client.cancel(job_id):
            print("Job cancelled")
    except Exception as e:
        print(f"✗ Error: {e}")

    # Example 3: Get all jobs
    print("\n\nListing all jobs...")
    all_jobs = client.get_all_jobs()
    for job_id, status in all_jobs.items():
        print(f"  {status}")
