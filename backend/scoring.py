import numpy as np
from scipy import stats
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import math

# Risk-free rate (10-year G-sec annualized, configurable)
RISK_FREE_RATE = 0.07

def percentile_rank(value: float, arr: List[float]) -> float:
    """
    Calculate percentile rank: (count of values <= x) / total * 100
    """
    if not arr or value is None:
        return 50.0
    count_le = sum(1 for v in arr if v is not None and v <= value)
    return (count_le / len(arr)) * 100

def calculate_rolling_return(nav_current: float, nav_past: float, years: int) -> float:
    """
    Calculate annualized rolling return
    """
    if nav_past <= 0 or nav_current <= 0:
        return 0.0
    return ((nav_current / nav_past) ** (1 / years)) - 1

def calculate_daily_returns(nav_series: List[float]) -> List[float]:
    """
    Calculate daily returns from NAV series
    """
    if len(nav_series) < 2:
        return []
    returns = []
    for i in range(1, len(nav_series)):
        if nav_series[i-1] > 0:
            returns.append((nav_series[i] / nav_series[i-1]) - 1)
        else:
            returns.append(0.0)
    return returns

def calculate_std_dev(daily_returns: List[float], periods: int = 252) -> float:
    """
    Calculate standard deviation (annualized)
    """
    if not daily_returns or len(daily_returns) < 2:
        return 0.0
    return np.std(daily_returns) * np.sqrt(periods)

def calculate_max_drawdown(nav_series: List[float]) -> float:
    """
    Calculate maximum drawdown
    """
    if not nav_series or len(nav_series) < 2:
        return 0.0
    
    peak = nav_series[0]
    max_dd = 0.0
    
    for nav in nav_series:
        if nav > peak:
            peak = nav
        drawdown = (nav - peak) / peak if peak > 0 else 0.0
        if drawdown < max_dd:
            max_dd = drawdown
    
    return max_dd

def calculate_sharpe(daily_returns: List[float], risk_free_rate: float = RISK_FREE_RATE) -> float:
    """
    Calculate Sharpe ratio
    """
    if not daily_returns or len(daily_returns) < 2:
        return 0.0
    
    excess_returns = [r - (risk_free_rate / 252) for r in daily_returns]
    mean_excess = np.mean(excess_returns)
    std_excess = np.std(excess_returns)
    
    if std_excess == 0:
        return 0.0
    
    return (mean_excess / std_excess) * np.sqrt(252)

def calculate_sortino(daily_returns: List[float], risk_free_rate: float = RISK_FREE_RATE) -> float:
    """
    Calculate Sortino ratio
    """
    if not daily_returns or len(daily_returns) < 2:
        return 0.0
    
    excess_returns = [r - (risk_free_rate / 252) for r in daily_returns]
    downside_returns = [r for r in excess_returns if r < 0]
    
    if not downside_returns:
        return 0.0
    
    downside_deviation = np.sqrt(np.mean([r**2 for r in downside_returns])) * np.sqrt(252)
    mean_excess = np.mean(excess_returns)
    
    if downside_deviation == 0:
        return 0.0
    
    return mean_excess * np.sqrt(252) / downside_deviation

def calculate_beta(fund_returns: List[float], benchmark_returns: List[float]) -> float:
    """
    Calculate beta
    """
    if not fund_returns or not benchmark_returns or len(fund_returns) != len(benchmark_returns):
        return 1.0
    
    if len(fund_returns) < 2:
        return 1.0
    
    covariance = np.cov(fund_returns, benchmark_returns)[0][1]
    variance = np.var(benchmark_returns)
    
    if variance == 0:
        return 1.0
    
    return covariance / variance

def calculate_information_ratio(
    fund_annual_return: float,
    benchmark_annual_return: float,
    fund_returns: List[float],
    benchmark_returns: List[float]
) -> float:
    """
    Calculate information ratio
    """
    if not fund_returns or not benchmark_returns or len(fund_returns) != len(benchmark_returns):
        return 0.0
    
    active_return = fund_annual_return - benchmark_annual_return
    tracking_diff = [f - b for f, b in zip(fund_returns, benchmark_returns)]
    tracking_error = np.std(tracking_diff) * np.sqrt(252)
    
    if tracking_error == 0:
        return 0.0
    
    return active_return / tracking_error

def calculate_treynor(
    fund_annual_return: float,
    beta: float,
    risk_free_rate: float = RISK_FREE_RATE
) -> float:
    """
    Calculate Treynor ratio
    """
    if beta == 0:
        return 0.0
    
    return (fund_annual_return - risk_free_rate) / beta

def calculate_hit_ratio(
    fund_nav_history: List[Dict[str, Any]],
    category_median_history: List[Dict[str, Any]],
    years: int = 3
) -> float:
    """
    Calculate hit ratio (percentage of rolling periods where fund outperforms category median)
    """
    if len(fund_nav_history) < years * 252:
        return 0.0
    
    windows = min(36, len(fund_nav_history) - years * 252)  # Check last 36 months
    wins = 0
    
    for i in range(windows):
        start_idx = i
        end_idx = i + years * 252
        
        if end_idx < len(fund_nav_history):
            fund_return = calculate_rolling_return(
                fund_nav_history[end_idx]['nav'],
                fund_nav_history[start_idx]['nav'],
                years
            )
            
            if end_idx < len(category_median_history):
                cat_return = calculate_rolling_return(
                    category_median_history[end_idx]['value'],
                    category_median_history[start_idx]['value'],
                    years
                )
                
                if fund_return > cat_return:
                    wins += 1
    
    return (wins / windows * 100) if windows > 0 else 0.0

def calculate_final_score(
    percentiles: Dict[str, float],
    weights: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Calculate final score based on percentiles and weights
    """
    # Default sub-weights (absolute points out of 100)
    default_sub_weights = {
        'rolling_3y_vs_category': 12,
        'rolling_5y_vs_category': 6,
        'hit_ratio_3y': 4,
        'sharpe': 4,
        'sortino': 3,
        'information_ratio': 2,
        'treynor': 1,
        'std_dev_1y': 8,
        'max_drawdown': 6,
        'beta': 4,
        'vol_skew': 2,
        'return_1y': 3,
        'return_3y': 8,
        'return_5y': 4
    }
    
    # Use custom weights if provided, otherwise use defaults
    sub_weights = weights.get('sub_weights', default_sub_weights)
    
    # Calculate weighted score
    total_score = 0.0
    bucket_scores = {
        'Consistency': 0.0,
        'Volatility': 0.0,
        'Performance': 0.0,
        'Portfolio Quality': 0.0,
        'Valuation': 0.0
    }
    
    # Consistency (30 points)
    consistency_metrics = [
        ('rolling_3y_vs_category', 12),
        ('rolling_5y_vs_category', 6),
        ('hit_ratio_3y', 4),
        ('sharpe', 4),
        ('sortino', 3),
        ('information_ratio', 2),
        ('treynor', 1)
    ]
    
    for metric, weight in consistency_metrics:
        if metric in percentiles and percentiles[metric] is not None:
            bucket_scores['Consistency'] += (percentiles[metric] / 100) * weight
    
    # Volatility (20 points) - invert for lower-is-better metrics
    volatility_metrics = [
        ('std_dev_1y', 8, True),
        ('max_drawdown', 6, True),
        ('beta', 4, False),
        ('vol_skew', 2, False)
    ]
    
    for metric, weight, invert in volatility_metrics:
        if metric in percentiles and percentiles[metric] is not None:
            percentile = percentiles[metric]
            if invert:
                percentile = 100 - percentile
            bucket_scores['Volatility'] += (percentile / 100) * weight
    
    # Performance (15 points)
    performance_metrics = [
        ('return_1y', 3),
        ('return_3y', 8),
        ('return_5y', 4)
    ]
    
    for metric, weight in performance_metrics:
        if metric in percentiles and percentiles[metric] is not None:
            bucket_scores['Performance'] += (percentiles[metric] / 100) * weight
    
    # Portfolio Quality & Valuation would need additional data
    # For now, we'll allocate proportional scores
    bucket_scores['Portfolio Quality'] = 15.0  # Placeholder
    bucket_scores['Valuation'] = 10.0  # Placeholder
    
    total_score = sum(bucket_scores.values())
    
    return {
        'final_score': total_score,
        'bucket_scores': bucket_scores
    }
