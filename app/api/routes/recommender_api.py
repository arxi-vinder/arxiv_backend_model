import traceback
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from app.db.database import get_db
from app.model.user import User
from app.repositories.feedback_repository import FeedbackRepository
from app.repositories.paper_repository import PaperRepository
from app.repositories.recommendation_log_repository import RecommendationLogRepository
from app.services import recommendation_service
from app.services.recommendation_log_service import RecommendationLogService
from app.services.vectorization_cache_service import VectorizationCacheService
from app.services.vectorization_async_service import get_vectorization_async_service
from app.services.ucb_service import UCBService
from app.utils.jwt import get_current_user


router = APIRouter(
    prefix='/api/v1'
)


@router.get("/recommend/{paper_id}")
async def get_recommendation(
    paper_id: int,
    top_n: int = 5,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    repo = PaperRepository(db)

    service = recommendation_service.RecommendationService(repo)

    results = service.get_recommendations_by_paper_id(
        paper_id,
        top_n
    )

    if not results:
        raise HTTPException(status_code=404, detail="Paper not found")

    feedback_repo = FeedbackRepository(db)

    ucb_service = UCBService(
        feedback_repo=feedback_repo,
        paper_repo=repo,
        cbf_service=service
    )

    final_results = ucb_service.rank_from_list(paper_id)
    log_repo = RecommendationLogRepository(db)
    log_service = RecommendationLogService(log_repo)

    recommendation_ids: list[int] = [int(rec["paper_id"]) for rec in final_results["data"]]  # type: ignore

    existing_log = log_repo.get_latest_by_user(current_user.id)
    if not existing_log or set(recommendation_ids) != set(existing_log.recommendations or []):  # type: ignore
        log_service.create_log(
            user_id=current_user.id,
            recommendations=recommendation_ids,
            relevants=[]
        )

    return {
        "status": "success",
        "message": "Recommendations retrieved successfully",
        "data": {
            "paper_id": paper_id,
            "recommendations": final_results
        }
    }


@router.post("/vectorize-all-papers")
async def vectorize_all_papers(
    batch_size: int = 100,
    db: Session = Depends(get_db)
):
    """
    Full vectorization untuk semua papers dalam database dengan batch processing.
    - Memproses ALL papers (bukan hanya 100)
    - Batch preprocessing untuk efisiensi memory
    - Precompute vectors dan simpan ke cache
    - Process ini bisa memakan waktu lama (8-10 menit untuk 5000 papers)
    """
    try:
        repo = PaperRepository(db)
        service = recommendation_service.RecommendationService(repo, auto_build=False, use_cache=True)
        print(f"[VECTORIZATION API] Batch size: {batch_size}")

        service.build_full_model_batch(batch_size=batch_size, verbose=True)

        total_papers = len(service.datas)
        matrix_size = len(service.cosine_sim_matrix)

        return {
            "status": "success",
            "message": "Full vectorization completed and cached successfully",
            "data": {
                "total_papers_processed": total_papers,
                "cosine_matrix_size": f"{matrix_size}x{matrix_size}",
                "batch_size_used": batch_size,
                "cached": True
            }
        }

    except Exception as e:
        print(f"[VECTORIZATION API ERROR] {type(e).__name__}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "error_type": type(e).__name__,
                "message": str(e),
                "traceback": traceback.format_exc()
            }
        )


@router.get("/cache/status")
async def get_cache_status():
    """
    Check status cache precomputed vectors
    """
    try:
        cache_service = VectorizationCacheService()
        cache_info = cache_service.get_cache_info()

        return {
            "status": "success",
            "data": cache_info
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "error_type": type(e).__name__,
                "message": str(e)
            }
        )


@router.delete("/cache/clear")
async def clear_cache():
    """
    Clear cached vectors (ADMIN ONLY)
    """
    try:
        cache_service = VectorizationCacheService()
        success = cache_service.clear_cache()

        if success:
            return {
                "status": "success",
                "message": "Cache cleared successfully"
            }
        else:
            raise HTTPException(
                status_code=500,
                detail={
                    "status": "error",
                    "message": "Failed to clear cache"
                }
            )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "error_type": type(e).__name__,
                "message": str(e)
            }
        )


@router.post("/recommend/{paper_id}/refresh-ucb")
async def refresh_ucb_scores(
    paper_id: int,
    top_n: int = 5,
    db: Session = Depends(get_db)
):
    """
    Refresh dan recalculate UCB scores berdasarkan feedback terbaru.
    Endpoint ini akan fetch ulang semua feedback data dan recalculate UCB scores
    sehingga ranking rekomendasi akan update sesuai dengan data feedback terbaru.

    Args:
        paper_id: ID paper yang akan di-refresh UCB scoresnya
        top_n: Jumlah top recommendations yang akan dikembalikan (default: 5)
        current_user: User yang authenticated (required untuk security)
    """
    try:
        repo = PaperRepository(db)
        service = recommendation_service.RecommendationService(repo)

        feedback_repo = FeedbackRepository(db)

        ucb_service = UCBService(
            feedback_repo=feedback_repo,
            paper_repo=repo,
            cbf_service=service
        )

        refreshed_results = ucb_service.refresh_ucb_scores(paper_id, top_k=top_n)

        return {
            "status": "success",
            "message": "UCB scores refreshed successfully",
            "data": {
                "paper_id": paper_id,
                "recommendations": refreshed_results
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "error_type": type(e).__name__,
                "message": str(e),
                "traceback": traceback.format_exc()
            }
        )


@router.get("/cache/info")
async def get_cache_info():
    """
    Get detailed cache information (equivalent to CLI: cache-info command)

    Returns:
        - Cache status (cached/no_cache/error)
        - Total papers cached
        - Matrix size
        - File size in MB
        - Last saved timestamp
        - Cache file location
    """
    try:
        cache_service = VectorizationCacheService()
        cache_info = cache_service.get_cache_info()

        if cache_info.get("status") == "no_cache":
            return {
                "status": "success",
                "cache_status": "no_cache",
                "message": "No cache found. Run vectorization to create cache.",
                "data": None
            }
        elif cache_info.get("status") == "error":
            return {
                "status": "success",
                "cache_status": "error",
                "message": cache_info.get("message"),
                "data": None
            }
        else:
            return {
                "status": "success",
                "cache_status": "cached",
                "message": "Cache is available",
                "data": {
                    "total_papers": cache_info.get("total_papers"),
                    "matrix_size": f"{cache_info.get('matrix_size')}x{cache_info.get('matrix_size')}",
                    "file_size_mb": cache_info.get("file_size_mb"),
                    "last_saved": cache_info.get("saved_at"),
                    "cache_location": cache_info.get("cache_file")
                }
            }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "error_type": type(e).__name__,
                "message": str(e)
            }
        )


@router.get("/vectorization/status")
async def get_vectorization_status(
    db: Session = Depends(get_db)
):
    """
    Get complete vectorization status (equivalent to CLI: status command)

    Returns:
        - Database info (total papers)
        - Cache info (status, papers cached, matrix size, file size, last updated)
    """
    try:
        # Get database info
        repo = PaperRepository(db)
        total_papers = repo.get_total_papers_count()

        # Get cache info
        cache_service = VectorizationCacheService()
        cache_info = cache_service.get_cache_info()

        db_info = {
            "total_papers_in_db": total_papers
        }

        if cache_info.get("status") == "no_cache":
            cache_status = {
                "status": "not_cached",
                "message": "No cache found",
                "data": None
            }
        elif cache_info.get("status") == "error":
            cache_status = {
                "status": "error",
                "message": cache_info.get("message"),
                "data": None
            }
        else:
            cache_status = {
                "status": "cached",
                "message": "Cache is available",
                "data": {
                    "papers_cached": cache_info.get("total_papers"),
                    "matrix_size": f"{cache_info.get('matrix_size')}x{cache_info.get('matrix_size')}",
                    "file_size_mb": cache_info.get("file_size_mb"),
                    "last_updated": cache_info.get("saved_at"),
                    "cache_location": cache_info.get("cache_file")
                }
            }

        return {
            "status": "success",
            "database": db_info,
            "cache": cache_status
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "error_type": type(e).__name__,
                "message": str(e)
            }
        )


@router.post("/vectorize-async")
async def vectorize_all_papers_async(batch_size: int = 100):
    """
    Start async vectorization (non-blocking)

    Ini adalah endpoint yang tidak akan timeout karena proses vectorization
    dijalankan di background thread. Response langsung kembali dengan job_id
    yang bisa digunakan untuk polling status.

    Keuntungan:
    - Response immediate (tidak timeout)
    - Bisa polling progress dengan job_id
    - Bisa check multiple jobs sekaligus
    - Cocok untuk long-running processes

    Parameters:
        batch_size: Ukuran batch untuk processing (default: 100)

    Returns:
        job_id: Unique identifier untuk track vectorization job
        Gunakan job_id untuk polling status dengan endpoint: /vectorization-job/{job_id}/status
    """
    try:
        async_service = get_vectorization_async_service()

        # Check if too many jobs already running
        active_count = async_service.get_active_jobs_count()
        if active_count > 3:
            raise HTTPException(
                status_code=429,
                detail={
                    "status": "error",
                    "message": f"Too many vectorization jobs running ({active_count}). Please wait for some to complete."
                }
            )

        # Create job dan start async processing
        job_id = async_service.job_service.create_job(batch_size)
        async_service.start_vectorization_async(job_id, batch_size)

        return {
            "status": "success",
            "message": "Vectorization started in background",
            "data": {
                "job_id": job_id,
                "batch_size": batch_size,
                "status_url": f"/api/v1/vectorization-job/{job_id}/status",
                "next_step": f"Poll status dengan: GET /api/v1/vectorization-job/{job_id}/status"
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "error_type": type(e).__name__,
                "message": str(e),
                "traceback": traceback.format_exc()
            }
        )


@router.get("/vectorization-job/{job_id}/status")
async def get_vectorization_job_status(job_id: str):
    """
    Check status of a vectorization job

    Endpoint ini digunakan untuk polling status vectorization yang dijalankan async.
    Return progress, status, dan result (jika completed).

    Parameters:
        job_id: Job ID dari POST /vectorize-async response

    Returns:
        Status: pending | running | completed | failed | cancelled
        Progress: Total papers, processed papers, percentage
        Elapsed time dalam detik
    """
    try:
        async_service = get_vectorization_async_service()
        job_status = async_service.get_job_status(job_id)

        if not job_status:
            raise HTTPException(
                status_code=404,
                detail={
                    "status": "error",
                    "message": f"Job {job_id} not found"
                }
            )

        return {
            "status": "success",
            "data": job_status
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "error_type": type(e).__name__,
                "message": str(e)
            }
        )


@router.delete("/vectorization-job/{job_id}/cancel")
async def cancel_vectorization_job(job_id: str):
    """
    Cancel a pending vectorization job

    Hanya bisa cancel job yang masih pending (belum running).
    Tidak bisa cancel job yang sudah running.

    Parameters:
        job_id: Job ID dari POST /vectorize-async response

    Returns:
        Success/failure message
    """
    try:
        async_service = get_vectorization_async_service()
        success = async_service.cancel_job(job_id)

        if success:
            return {
                "status": "success",
                "message": f"Job {job_id} cancelled successfully"
            }
        else:
            job = async_service.job_service.get_job(job_id)
            if not job:
                raise HTTPException(
                    status_code=404,
                    detail={
                        "status": "error",
                        "message": f"Job {job_id} not found"
                    }
                )
            else:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "status": "error",
                        "message": f"Cannot cancel job - job status is '{job.status.value}' (only pending jobs can be cancelled)"
                    }
                )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "error_type": type(e).__name__,
                "message": str(e)
            }
        )


@router.get("/vectorization-jobs")
async def list_all_vectorization_jobs():
    """
    List all vectorization jobs (active dan completed)

    Useful untuk monitoring dan debugging.
    Return semua jobs dengan status mereka.

    Returns:
        Dictionary berisi semua jobs dengan status lengkap
    """
    try:
        async_service = get_vectorization_async_service()
        all_jobs = async_service.get_active_jobs()

        return {
            "status": "success",
            "total_jobs": len(all_jobs),
            "active_jobs": async_service.get_active_jobs_count(),
            "data": all_jobs
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "error_type": type(e).__name__,
                "message": str(e)
            }
        )