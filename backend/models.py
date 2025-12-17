from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class Fund(BaseModel):
    fund_id: str
    name: str
    amc: str
    category: str
    benchmark: str
    inception_date: datetime
    created_at: datetime
    updated_at: datetime

class NavHistoryItem(BaseModel):
    fund_id: str
    date: datetime
    nav: float
    plan: str = "Growth"

class BenchmarkHistoryItem(BaseModel):
    index: str
    date: datetime
    value: float

class PortfolioSnapshot(BaseModel):
    fund_id: str
    date: datetime
    pe: Optional[float] = None
    pb: Optional[float] = None
    aum: Optional[float] = None
    top10_weight: Optional[float] = None
    num_stocks: Optional[int] = None
    turnover_ratio: Optional[float] = None
    holdings: List[Dict[str, Any]] = []

class MetricsRaw(BaseModel):
    return_1y: Optional[float] = None
    return_3y: Optional[float] = None
    return_5y: Optional[float] = None
    rolling_3y_vs_category: Optional[float] = None
    rolling_5y_vs_category: Optional[float] = None
    hit_ratio_3y: Optional[float] = None
    std_dev_1y: Optional[float] = None
    max_drawdown: Optional[float] = None
    beta: Optional[float] = None
    sharpe: Optional[float] = None
    sortino: Optional[float] = None
    information_ratio: Optional[float] = None
    treynor: Optional[float] = None
    vol_skew: Optional[float] = None

class MetricsPercentiles(BaseModel):
    return_1y: Optional[float] = None
    return_3y: Optional[float] = None
    return_5y: Optional[float] = None
    rolling_3y_vs_category: Optional[float] = None
    rolling_5y_vs_category: Optional[float] = None
    hit_ratio_3y: Optional[float] = None
    std_dev_1y: Optional[float] = None
    max_drawdown: Optional[float] = None
    beta: Optional[float] = None
    sharpe: Optional[float] = None
    sortino: Optional[float] = None
    information_ratio: Optional[float] = None
    treynor: Optional[float] = None
    vol_skew: Optional[float] = None

class Metrics(BaseModel):
    fund_id: str
    date: datetime
    raw: MetricsRaw
    percentiles: MetricsPercentiles
    eligible_for_ranking: bool

class ScoreCache(BaseModel):
    fund_id: str
    date: datetime
    final_score_default: float
    bucket_scores: Dict[str, float]

class UserWeightset(BaseModel):
    name: str
    weights: Dict[str, Any]

class UserPreferences(BaseModel):
    default_weights: Optional[Dict[str, Any]] = None
    saved_weights: List[UserWeightset] = []
    min_history_years: int = 3

class User(BaseModel):
    user_id: str
    email: str
    name: str
    picture: Optional[str] = None
    preferences: Optional[UserPreferences] = None
    created_at: datetime

class UserSession(BaseModel):
    user_id: str
    session_token: str
    expires_at: datetime
    created_at: datetime
