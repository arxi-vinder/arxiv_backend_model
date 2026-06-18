# import logging
# import threading
# from app.db.database import SessionLocal
# from app.repositories.paper_repository import PaperRepository
# from app.services.recommendation_service import RecommendationService
# from app.services.vectorization_cache_service import VectorizationCacheService

# logger = logging.getLogger(__name__)


# def check_and_build_cache():
#     """Check if cache exists, build if not. Non-blocking, runs in background."""
#     def build_cache_background():
#         try:
#             db = SessionLocal()
#             cache_service = VectorizationCacheService(db_session=db)

#             if cache_service.is_cache_valid():
#                 logger.info("[STARTUP] Cache already exists, skipping vectorization")
#                 print("[STARTUP] Cache already exists, using cached vectors")
#                 return

#             logger.info("[STARTUP] Cache not found, starting full vectorization in background...")
#             print("[STARTUP] Building cache with all papers (this may take a few minutes)...")

#             paper_repo = PaperRepository(db)
#             service = RecommendationService(paper_repo, auto_build=False, use_cache=True, db_session=db)

#             total_papers = paper_repo.get_total_papers_count()
#             if total_papers == 0:
#                 logger.warning("[STARTUP] No papers in database, skipping vectorization")
#                 print("[STARTUP] No papers in database")
#                 return

#             logger.info(f"[STARTUP] Starting vectorization for {total_papers} papers")
#             print(f"[STARTUP] Total papers to vectorize: {total_papers}")

#             service.build_full_model_batch(batch_size=100, verbose=True)
#             logger.info("[STARTUP] Vectorization completed successfully")
#             print("[STARTUP] Cache ready!")

#         except Exception as e:
#             logger.error(f"[STARTUP] Error during vectorization: {str(e)}")
#             print(f"[STARTUP ERROR] Could not build cache: {str(e)}")
#         finally:
#             try:
#                 db.close()
#             except:
#                 pass

#     thread = threading.Thread(target=build_cache_background, daemon=True)
#     thread.start()
