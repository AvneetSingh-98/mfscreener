

from fastapi import FastAPI, APIRouter, HTTPException, Cookie, Header, Response, UploadFile, File
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone, timedelta
import httpx
import numpy as np
from dotenv import load_dotenv
load_dotenv()

from models import (
    Fund, User, UserSession, UserPreferences, UserWeightset,
    MetricsRaw, MetricsPercentiles, Metrics, ScoreCache
)
from scoring import (
    calculate_daily_returns, calculate_std_dev, calculate_max_drawdown,
    calculate_sharpe, calculate_sortino, calculate_beta,
    calculate_information_ratio, calculate_treynor, calculate_rolling_return,
    calculate_hit_ratio, percentile_rank, calculate_final_score
)
print("MONGO_URL:", os.environ.get("MONGO_URL"))
print("DB_NAME:", os.environ.get("DB_NAME"))

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

app = FastAPI()
api_router = APIRouter(prefix="/api")

EMERGENT_AUTH_URL = "https://demobackend.emergentagent.com/auth/v1/env/oauth/session-data"

class LoginRequest(BaseModel):
    email: str
    password: str

class SessionDataResponse(BaseModel):
    id: str
    email: str
    name: str
    picture: Optional[str] = None
    session_token: str

async def get_current_user(session_token: Optional[str] = Cookie(None), authorization: Optional[str] = Header(None)) -> User:
    token = session_token
    
    if not token and authorization:
        if authorization.startswith("Bearer "):
            token = authorization.replace("Bearer ", "")
    
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    session_doc = await db.user_sessions.find_one({"session_token": token}, {"_id": 0})
    if not session_doc:
        raise HTTPException(status_code=401, detail="Invalid session")
    
    expires_at = session_doc["expires_at"]
    if isinstance(expires_at, str):
        expires_at = datetime.fromisoformat(expires_at)
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    
    if expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail="Session expired")
    
    user_doc = await db.users.find_one({"user_id": session_doc["user_id"]}, {"_id": 0})
    if not user_doc:
        raise HTTPException(status_code=404, detail="User not found")
    
    if isinstance(user_doc.get('created_at'), str):
        user_doc['created_at'] = datetime.fromisoformat(user_doc['created_at'])
    
    return User(**user_doc)

@api_router.post("/auth/session")
async def create_session_from_google(session_id: str, response: Response):
    async with httpx.AsyncClient() as http_client:
        try:
            result = await http_client.get(
                EMERGENT_AUTH_URL,
                headers={"X-Session-ID": session_id},
                timeout=10.0
            )
            result.raise_for_status()
            session_data = SessionDataResponse(**result.json())
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to verify session: {str(e)}")
    
    user_id = f"user_{uuid.uuid4().hex[:12]}"
    existing_user = await db.users.find_one({"email": session_data.email}, {"_id": 0})
    
    if existing_user:
        user_id = existing_user["user_id"]
        await db.users.update_one(
            {"user_id": user_id},
            {"$set": {
                "name": session_data.name,
                "picture": session_data.picture
            }}
        )
    else:
        new_user = {
            "user_id": user_id,
            "email": session_data.email,
            "name": session_data.name,
            "picture": session_data.picture,
            "preferences": {
                "default_weights": None,
                "saved_weights": [],
                "min_history_years": 3
            },
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.users.insert_one(new_user)
    
    expires_at = datetime.now(timezone.utc) + timedelta(days=7)
    user_session = {
        "user_id": user_id,
        "session_token": session_data.session_token,
        "expires_at": expires_at.isoformat(),
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.user_sessions.delete_many({"user_id": user_id})
    await db.user_sessions.insert_one(user_session)
    
    response.set_cookie(
        key="session_token",
        value=session_data.session_token,
        httponly=True,
        secure=True,
        samesite="none",
        max_age=7 * 24 * 60 * 60,
        path="/"
    )
    
    user_doc = await db.users.find_one({"user_id": user_id}, {"_id": 0})
    if isinstance(user_doc.get('created_at'), str):
        user_doc['created_at'] = datetime.fromisoformat(user_doc['created_at'])
    
    return {"user": user_doc}

@api_router.get("/auth/me")
async def get_me(session_token: Optional[str] = Cookie(None), authorization: Optional[str] = Header(None)):
    user = await get_current_user(session_token, authorization)
    return user

@api_router.post("/auth/logout")
async def logout(response: Response, session_token: Optional[str] = Cookie(None)):
    if session_token:
        await db.user_sessions.delete_many({"session_token": session_token})
    
    response.delete_cookie(key="session_token", path="/")
    return {"message": "Logged out successfully"}

from datetime import datetime, timedelta

@app.get("/api/funds")
async def get_funds(
    category: str | None = None,
    min_history_years: int = 0,
    page: int = 1,
    limit: int = 50,
):
    query = {}

    if category:
     query["category"] = {
        "$regex": f"^{category.replace(' ', '')}$",
        "$options": "i"
     }


    if min_history_years and min_history_years > 0:
        cutoff_date = datetime.utcnow() - timedelta(days=365 * min_history_years)

        # ✅ IMPORTANT: use $lte (older than cutoff)
        query["inception_date"] = {
            "$lte": cutoff_date
        }

    cursor = (
        db.funds
        .find(query, {"_id": 0})
        .skip((page - 1) * limit)
        .limit(limit)
    )

    funds = await cursor.to_list(length=limit)
    total = await db.funds.count_documents(query)

    return {
        "funds": funds,
        "total": total,
        "page": page,
        "limit": limit,
    }

@api_router.get("/funds/{fund_id}")
async def get_fund_detail(fund_id: str):
    fund = await db.funds.find_one({"fund_id": fund_id}, {"_id": 0})
    if not fund:
        raise HTTPException(status_code=404, detail="Fund not found")
    
    nav_cursor = db.nav_history.find(
        {"fund_id": fund_id},
        {"_id": 0}
    ).sort("date", -1).limit(1825)
    nav_history = await nav_cursor.to_list(length=1825)
    
    metrics_doc = await db.metrics.find_one({"fund_id": fund_id}, {"_id": 0})
    
    portfolio_doc = await db.portfolio_snapshots.find_one(
        {"fund_id": fund_id},
        {"_id": 0}
    )
    
    score_doc = await db.score_cache.find_one({"fund_id": fund_id}, {"_id": 0})
    
    return {
        "fund": fund,
        "nav_history": nav_history,
        "metrics": metrics_doc,
        "portfolio": portfolio_doc,
        "score": score_doc
    }

@api_router.get("/metrics/{fund_id}")
async def get_metrics(fund_id: str):
    metrics_doc = await db.metrics.find_one({"fund_id": fund_id}, {"_id": 0})
    if not metrics_doc:
        raise HTTPException(status_code=404, detail="Metrics not found")
    
    return metrics_doc

@api_router.put("/user/preferences")
async def update_preferences(preferences: UserPreferences, session_token: Optional[str] = Cookie(None), authorization: Optional[str] = Header(None)):
    user = await get_current_user(session_token, authorization)
    
    await db.users.update_one(
        {"user_id": user.user_id},
        {"$set": {"preferences": preferences.model_dump()}}
    )
    
    return {"message": "Preferences updated successfully"}

@api_router.post("/admin/recompute")
async def trigger_recompute(min_history_years: int = 3, session_token: Optional[str] = Cookie(None), authorization: Optional[str] = Header(None)):
    try:
        user = await get_current_user(session_token, authorization)
    except:
        pass
    
    min_date = datetime.now(timezone.utc) - timedelta(days=min_history_years * 365)
    
    funds_cursor = db.funds.find(
        {"inception_date": {"$lte": min_date.isoformat()}},
        {"_id": 0}
    )
    eligible_funds = await funds_cursor.to_list(length=1000)
    
    computed_count = 0
    for fund in eligible_funds:
        fund_id = fund["fund_id"]
        
        nav_cursor = db.nav_history.find(
            {"fund_id": fund_id},
            {"_id": 0}
        ).sort("date", 1)
        nav_history = await nav_cursor.to_list(length=10000)
        
        if len(nav_history) < min_history_years * 252:
            continue
        
        nav_values = [n["nav"] for n in nav_history]
        daily_returns = calculate_daily_returns(nav_values)
        
        last_year_returns = daily_returns[-252:] if len(daily_returns) >= 252 else daily_returns
        
        return_1y = calculate_rolling_return(nav_values[-1], nav_values[-252], 1) if len(nav_values) >= 252 else 0
        return_3y = calculate_rolling_return(nav_values[-1], nav_values[-756], 3) if len(nav_values) >= 756 else 0
        return_5y = calculate_rolling_return(nav_values[-1], nav_values[-1260], 5) if len(nav_values) >= 1260 else 0
        
        benchmark_cursor = db.benchmark_history.find(
            {"index": fund["benchmark"]},
            {"_id": 0}
        ).sort("date", 1)
        benchmark_history = await benchmark_cursor.to_list(length=10000)
        benchmark_values = [b["value"] for b in benchmark_history]
        benchmark_returns = calculate_daily_returns(benchmark_values)
        
        min_len = min(len(daily_returns), len(benchmark_returns))
        fund_returns_aligned = daily_returns[-min_len:]
        bench_returns_aligned = benchmark_returns[-min_len:]
        
        metrics_raw = MetricsRaw(
            return_1y=return_1y,
            return_3y=return_3y,
            return_5y=return_5y,
            rolling_3y_vs_category=return_3y,
            rolling_5y_vs_category=return_5y,
            hit_ratio_3y=50.0,
            std_dev_1y=calculate_std_dev(last_year_returns),
            max_drawdown=calculate_max_drawdown(nav_values[-252:]),
            beta=calculate_beta(fund_returns_aligned, bench_returns_aligned),
            sharpe=calculate_sharpe(last_year_returns),
            sortino=calculate_sortino(last_year_returns),
            information_ratio=calculate_information_ratio(return_1y, 0.1, fund_returns_aligned, bench_returns_aligned),
            treynor=calculate_treynor(return_1y, calculate_beta(fund_returns_aligned, bench_returns_aligned)),
            vol_skew=1.0
        )
        
        metrics_doc = {
            "fund_id": fund_id,
            "date": datetime.now(timezone.utc).isoformat(),
            "raw": metrics_raw.model_dump(),
            "percentiles": {},
            "eligible_for_ranking": True
        }
        
        await db.metrics.update_one(
            {"fund_id": fund_id},
            {"$set": metrics_doc},
            upsert=True
        )
        
        computed_count += 1
    
    category_map = {}
    for fund in eligible_funds:
        cat = fund["category"]
        if cat not in category_map:
            category_map[cat] = []
        category_map[cat].append(fund["fund_id"])
    
    for category, fund_ids in category_map.items():
        metrics_cursor = db.metrics.find(
            {"fund_id": {"$in": fund_ids}},
            {"_id": 0}
        )
        all_metrics = await metrics_cursor.to_list(length=len(fund_ids))
        
        metric_names = ['return_1y', 'return_3y', 'return_5y', 'rolling_3y_vs_category', 
                       'rolling_5y_vs_category', 'hit_ratio_3y', 'std_dev_1y', 'max_drawdown',
                       'beta', 'sharpe', 'sortino', 'information_ratio', 'treynor', 'vol_skew']
        
        for metric_name in metric_names:
            values = [m["raw"].get(metric_name) for m in all_metrics if m["raw"].get(metric_name) is not None]
            
            for metric_doc in all_metrics:
                raw_value = metric_doc["raw"].get(metric_name)
                if raw_value is not None:
                    percentile = percentile_rank(raw_value, values)
                    
                    if metric_name in ['std_dev_1y', 'max_drawdown']:
                        percentile = 100 - percentile
                    
                    if "percentiles" not in metric_doc:
                        metric_doc["percentiles"] = {}
                    metric_doc["percentiles"][metric_name] = percentile
                    
                    await db.metrics.update_one(
                        {"fund_id": metric_doc["fund_id"]},
                        {"$set": {"percentiles": metric_doc["percentiles"]}}
                    )
    
    for fund in eligible_funds:
        fund_id = fund["fund_id"]
        metrics_doc = await db.metrics.find_one({"fund_id": fund_id}, {"_id": 0})
        
        if metrics_doc and "percentiles" in metrics_doc:
            score_result = calculate_final_score(metrics_doc["percentiles"], {})
            
            score_cache = {
                "fund_id": fund_id,
                "date": datetime.now(timezone.utc).isoformat(),
                "final_score_default": score_result["final_score"],
                "bucket_scores": score_result["bucket_scores"]
            }
            
            await db.score_cache.update_one(
                {"fund_id": fund_id},
                {"$set": score_cache},
                upsert=True
            )
    
    return {
        "message": "Recompute triggered successfully",
        "computed_funds": computed_count,
        "total_eligible": len(eligible_funds)
    }

@api_router.post("/admin/upload-factsheet")
async def upload_factsheet(file: UploadFile = File(...), session_token: Optional[str] = Cookie(None), authorization: Optional[str] = Header(None)):
    try:
        user = await get_current_user(session_token, authorization)
    except:
        pass
    
    return {"message": "Factsheet upload feature coming soon"}

@api_router.get("/categories")
async def get_categories():
    categories = await db.funds.distinct("category")
    return {"categories": categories}

app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
@app.get("/debug/categories")
async def debug_categories():
    return await db.funds.distinct("category")
