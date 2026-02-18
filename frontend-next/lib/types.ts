export interface NormalizedSubScores {
  returns: {
    cagr_1y?: number | null;
    cagr_3y?: number | null;
    cagr_5y?: number | null;
    return_3m?: number | null;
    return_6m?: number | null;
  };
  consistency: {
    alpha_3y?: number | null;
    alpha_5y?: number | null;
    confidence?: number | null;
    alpha_iqr_3y?: number | null;
    alpha_iqr_5y?: number | null;
  };
  risk: {
    volatility?: number | null;
    max_dd?: number | null;
    up_beta?: number | null;
    down_beta?: number | null;
  };
  risk_adjusted: {
    sharpe?: number | null;
    sortino?: number | null;
    ir?: number | null;
  };
  portfolio_quality: {
    stock_count?: number | null;
    aum?: number | null;
    top10?: number | null;
    sector_hhi?: number | null;
    top3_sector?: number | null;
    turnover?: number | null;
    ter?: number | null;
    manager_experience?: number | null;
  };
  valuation: {
    pe?: number | null;
    pb?: number | null;
    roe?: number | null;
  };
}

export interface FundRankingRow {
  scheme_code: string;
  fund_key: string;
  scheme_name: string;
  amc: string;

  normalized_scores: NormalizedSubScores;
  
  // Actual values for display
  actual_values: {
    returns: {
      return_3m?: number | null;
      return_6m?: number | null;
      cagr_1y?: number | null;
      cagr_3y?: number | null;
      cagr_5y?: number | null;
    };
    consistency: {
      rolling_3y?: number | null;
      rolling_5y?: number | null;
    };
    risk: {
      volatility?: number | null;
      up_beta?: number | null;
      down_beta?: number | null;
    };
    risk_adjusted: {
      sharpe?: number | null;
      sortino?: number | null;
      ir?: number | null;
    };
    portfolio_quality: {
      aum?: number | null;
      ter?: number | null;
      turnover?: number | null;
    };
  };
  
  overall_score?: number | null; // Computed client-side

  meta: {
    universe_size?: number;
    normalized_at?: string;
  };
}

