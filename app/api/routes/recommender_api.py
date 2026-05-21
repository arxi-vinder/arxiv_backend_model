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
async def get_cache_status(current_user: User = Depends(get_current_user)):
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
async def clear_cache(current_user: User = Depends(get_current_user)):
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
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
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