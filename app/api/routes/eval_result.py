from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from app.db.database import get_db
from app.repositories.evaluation_repository import EvaluationRepository
from app.services.evaluation_service import EvaluationService
from app.repositories.recommendation_log_repository import RecommendationLogRepository
from app.model.user import User

router = APIRouter(prefix="/api/v1/evaluation")


@router.post("/sync")
def sync_evaluation(db: Session = Depends(get_db)):
    try:
        log_repo = RecommendationLogRepository(db)
        logs = log_repo.get_all()

        if not logs:
            raise HTTPException(status_code=400, detail="No logs found")

        repo = EvaluationRepository(db)
        service = EvaluationService(repo)

        K_VALUES = [1,2, 3,4, 5]
        user_k_metrics = {}

        for log in logs:
            user_id = log.user_id
            recs = log.recommendations or []
            rels = log.relevants or []

            if user_id not in user_k_metrics:
                user_k_metrics[user_id] = {
                    k: {"p": [], "r": [], "ap": []} for k in K_VALUES
                }

            for k in K_VALUES:
                if len(recs) < k: # type: ignore
                    continue

                p = service.precision_at_k(recs, rels, k)
                r = service.recall_at_k(recs, rels, k)
                ap = service.average_precision(recs, rels, k)

                user_k_metrics[user_id][k]["p"].append(p)
                user_k_metrics[user_id][k]["r"].append(r)
                user_k_metrics[user_id][k]["ap"].append(ap)

        evaluation_results = []

        for user_id, k_data in user_k_metrics.items():
            for k, metrics in k_data.items():

                if not metrics["p"]:
                    continue

                n = len(metrics["p"])

                avg_p = sum(metrics["p"]) / n
                avg_r = sum(metrics["r"]) / n
                avg_ap = sum(metrics["ap"]) / n

                if avg_p + avg_r > 0:
                    f1 = 2 * (avg_p * avg_r) / (avg_p + avg_r)
                else:
                    f1 = 0

                evaluation_results.append({
                    "user_id": user_id,
                    "precision": avg_p,
                    "recall": avg_r,
                    "f1_score": f1,
                    "map_score": avg_ap,
                    "k": k
                })

        
        all_ap = [r["map_score"] for r in evaluation_results if r["map_score"] is not None]

        mean_ap = sum(all_ap) / len(all_ap) if all_ap else 0
        service.eval_repo.delete_all()
        service.eval_repo.save_bulk(evaluation_results)

        summary = service.calculate_mean_metrics(evaluation_results)

        return {
            "message": "Evaluation synced successfully",
            "summary": summary,
            "mean_average_precision": mean_ap, 
            "total_rows": len(evaluation_results)
        }

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/precision")
def get_precision(db: Session = Depends(get_db)):
    try:
        repo = EvaluationRepository(db)
        service = EvaluationService(repo)
        results = repo.get_all_with_username()

        user_map = {}

        for r in results:
            user_id = r.user_id
            username = r.username

            if user_id not in user_map:
                user_map[user_id] = {
                    "user_id": user_id,
                    "username": username,
                    "k1": 0,
                    "k2":0,
                    "k3": 0,
                    "k4":0,
                    "k5": 0
                }

            if r.k == 1:
                user_map[user_id]["k1"] = r.precision
            elif r.k == 2:
                user_map[user_id]["k2"] = r.precision
            elif r.k == 3:
                user_map[user_id]["k3"] = r.precision
            elif r.k == 4:
                user_map[user_id]["k4"] = r.precision
            elif r.k == 5:
                user_map[user_id]["k5"] = r.precision

        return list(user_map.values())

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/recall")
def get_recall(db: Session = Depends(get_db)):
    try:
        repo = EvaluationRepository(db)
        service = EvaluationService(repo)
        results = repo.get_all_with_username()


        user_map = {}

        for r in results:
            user_id = r.user_id
            username = r.username

            if user_id not in user_map:
                user_map[user_id] = {
                    "user_id": user_id,
                    "username": username,
                    "k1": 0,
                    "k2":0,
                    "k3": 0,
                    "k4":0,
                    "k5": 0
                }

            if r.k == 1:
                user_map[user_id]["k1"] = r.recall
            elif r.k == 2:
                user_map[user_id]["k2"] =r.recall
            elif r.k == 3:
                user_map[user_id]["k3"] = r.recall
            elif r.k == 4:
                user_map[user_id]["k4"] = r.recall
            elif r.k == 5:
                user_map[user_id]["k5"] = r.recall

        return list(user_map.values())

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/f1")
def get_f1(db: Session = Depends(get_db)):
    try:
        repo = EvaluationRepository(db)
        service = EvaluationService(repo)
        results = repo.get_all_with_username()


        user_map = {}

        for r in results:
            user_id = r.user_id
            username = r.username

            if user_id not in user_map:
                user_map[user_id] = {
                    "user_id": user_id,
                    "username": username,
                    "k1": 0,
                    "k2":0,
                    "k3": 0,
                    "k4":0,
                    "k5": 0
                }

            if r.k == 1:
                user_map[user_id]["k1"] = r.f1_score
            elif r.k == 2:
                user_map[user_id]["k2"] = r.f1_score
            elif r.k == 3:
                user_map[user_id]["k3"] = r.f1_score
            elif r.k == 4:
                user_map[user_id]["k4"] = r.f1_score
            elif r.k == 5:
                user_map[user_id]["k5"] = r.f1_score

        return list(user_map.values())

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Internal server error")
    
@router.get("/mape")
def get_map(db: Session = Depends(get_db)):
    try:
        log_repo = RecommendationLogRepository(db)
        eval_repo = EvaluationRepository(db)
        service = EvaluationService(eval_repo)

        logs = log_repo.get_all()

        if not logs:
            return {
                "message": "No evaluation data found",
                "mean_average_precision": 0,
                "average_precision_per_user": []
            }

        user_ap_map = {}

        
        K_VALUES = [1, 3, 5]
        user_ap_map_k = {}  # {user_id: {k: []}}

        for log in logs:
            user_id = log.user_id
            recommended = log.recommendations or []
            relevant = log.relevants or []

            if not recommended: # type: ignore
                continue

            ap = service.average_precision(
                recommended=recommended,
                relevant=relevant,
                k=len(recommended) # type: ignore
            )

            if user_id not in user_ap_map:
                user_ap_map[user_id] = []

            user_ap_map[user_id].append(ap)


            if user_id not in user_ap_map_k:
                user_ap_map_k[user_id] = {k: [] for k in K_VALUES}

            for k in K_VALUES:
                ap_k = service.average_precision(
                    recommended=recommended,
                    relevant=relevant,
                    k=k
                )
                user_ap_map_k[user_id][k].append(ap_k)


        average_precision_per_user = []

        # Get username for each user
        users = db.query(User.id, User.username).all()
        user_map_username = {u.id: u.username for u in users}

        for user_id, values in user_ap_map.items():
            ap_user = sum(values) / len(values) if values else 0
            username = user_map_username.get(user_id, "Unknown")

            average_precision_per_user.append({
                "user_id": user_id,
                "username": username,
                "average_precision": round(ap_user, 4)
            })

        all_user_ap = [u["average_precision"] for u in average_precision_per_user]
        mean_ap = sum(all_user_ap) / len(all_user_ap) if all_user_ap else 0

        map_k_result = {}

        for k in K_VALUES:
            all_ap_k = []

            for user_id in user_ap_map_k:
                values = user_ap_map_k[user_id][k]
                ap_user_k = sum(values) / len(values) if values else 0
                all_ap_k.append(ap_user_k)

            map_k = sum(all_ap_k) / len(all_ap_k) if all_ap_k else 0
            map_k_result[f"map@{k}"] = round(map_k, 5)

        return {
            "mean_average_precision": round(mean_ap, 5),
            "map_at_k": map_k_result,
            "average_precision_per_user": average_precision_per_user,
            "total_user": len(average_precision_per_user)
        }

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/average-metrics")
def get_average_metrics(db: Session = Depends(get_db)):
    """
    Get average evaluation metrics based on:
    - Sum of metrics from evaluation_results table
    - Divided by count of unique users in recommendation_logs table
    """
    try:
        log_repo = RecommendationLogRepository(db)
        eval_repo = EvaluationRepository(db)
        service = EvaluationService(eval_repo, log_repo)

        result = service.calculate_average_metrics_from_db()

        if result is None:
            raise HTTPException(status_code=400, detail="Repository not initialized")

        return result

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/average-metrics-by-k")
def get_average_metrics_by_k(db: Session = Depends(get_db)):
    """
    Get average evaluation metrics for each k value.
    Returns average precision, recall, f1_score, and map for each k (k=1, k=3, k=5, etc)
    """
    try:
        log_repo = RecommendationLogRepository(db)
        eval_repo = EvaluationRepository(db)
        service = EvaluationService(eval_repo, log_repo)

        result = service.calculate_average_metrics_by_k()

        if result is None:
            raise HTTPException(status_code=400, detail="Repository not initialized")

        return result

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Internal server error")