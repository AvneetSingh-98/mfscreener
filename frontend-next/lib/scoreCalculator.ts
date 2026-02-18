import { NormalizedSubScores } from "./types";

/**
 * Weight Presets
 * Each preset defines weights for the 5 main scoring categories
 * Weights must sum to 100
 */
export interface WeightPreset {
  consistency: number;
  recent_performance: number;
  risk: number;
  valuation: number;
  portfolio_quality: number;
}

export const WEIGHT_PRESETS: Record<string, WeightPreset> = {
  balanced: {
    consistency: 25,
    recent_performance: 20,
    risk: 20,
    valuation: 15,
    portfolio_quality: 20,
  },
  aggressive: {
    consistency: 15,
    recent_performance: 35,
    risk: 10,
    valuation: 15,
    portfolio_quality: 25,
  },
  conservative: {
    consistency: 35,
    recent_performance: 10,
    risk: 25,
    valuation: 20,
    portfolio_quality: 10,
  },
};

/**
 * Helper function to calculate weighted average
 * Returns null if ANY value is missing (strict mode)
 */
function weightedAverage(values: Array<{ value: number | null | undefined, weight: number }>): number | null {
  // Check if ANY value is missing
  const hasAnyMissing = values.some((v) => v.value == null || isNaN(v.value));
  if (hasAnyMissing) return null;
  
  const validValues = values.filter((v) => v.value != null && !isNaN(v.value));
  const totalWeight = validValues.reduce((sum, v) => sum + v.weight, 0);
  const weightedSum = validValues.reduce((sum, v) => sum + (v.value! * v.weight), 0);
  
  return weightedSum / totalWeight;
}

/**
 * Calculate main category scores from sub-scores with weighted averages
 * 
 * SUB-WEIGHTS:
 * 
 * Consistency:
 * - rolling_3y: 40%
 * - rolling_5y: 30%
 * - confidence: 10%
 * - iqr_3y: 10%
 * - iqr_5y: 10%
 * 
 * Recent Performance:
 * - cagr_3y: 30%
 * - cagr_5y: 25%
 * - cagr_1y: 20%
 * - return_6m: 15%
 * - return_3m: 10%
 * 
 * Risk:
 * - volatility: 20%
 * - max_dd: 15%
 * - sharpe: 15%
 * - sortino: 15%
 * - ir: 15%
 * - up_beta: 10%
 * - down_beta: 10%
 * 
 * Valuation:
 * - roe: 50%
 * - pe: 40%
 * - pb: 10%
 * 
 * Portfolio Quality:
 * - manager_experience: 20%
 * - turnover: 20%
 * - aum: 10%
 * - sector_hhi: 10%
 * - ter: 10%
 * - stock_count: 10%
 * - top10: 10%
 * - top3_sector: 10%
 * 
 * STRICT MODE: Returns null if ANY sub-metric is missing
 */
export function calculateMainScores(ns: NormalizedSubScores) {
  // Consistency
  const consistencyScore = weightedAverage([
    { value: ns.consistency.alpha_3y, weight: 25 },
    { value: ns.consistency.alpha_5y, weight: 25 },
    { value: ns.consistency.confidence, weight: 30 },
    { value: ns.consistency.alpha_iqr_3y, weight: 10 },
    { value: ns.consistency.alpha_iqr_5y, weight: 10 },
  ]);

  // Recent Performance
  const recentPerformanceScore = weightedAverage([
    { value: ns.returns.cagr_3y, weight: 30 },
    { value: ns.returns.cagr_5y, weight: 25 },
    { value: ns.returns.cagr_1y, weight: 20 },
    { value: ns.returns.return_6m, weight: 15 },
    { value: ns.returns.return_3m, weight: 10 },
  ]);

  // Risk
  const riskScore = weightedAverage([
    { value: ns.risk.volatility, weight: 20 },
    { value: ns.risk.max_dd, weight: 15 },
    { value: ns.risk_adjusted.sharpe, weight: 15 },
    { value: ns.risk_adjusted.sortino, weight: 15 },
    { value: ns.risk_adjusted.ir, weight: 15 },
    { value: ns.risk.up_beta, weight: 10 },
    { value: ns.risk.down_beta, weight: 10 },
  ]);

  // Valuation
  const valuationScore = weightedAverage([
    { value: ns.valuation.roe, weight: 50 },
    { value: ns.valuation.pe, weight: 40 },
    { value: ns.valuation.pb, weight: 10 },
  ]);

  // Portfolio Quality
  const portfolioQualityScore = weightedAverage([
    { value: ns.portfolio_quality.manager_experience, weight: 20 },
    { value: ns.portfolio_quality.turnover, weight: 20 },
    { value: ns.portfolio_quality.aum, weight: 10 },
    { value: ns.portfolio_quality.sector_hhi, weight: 10 },
    { value: ns.portfolio_quality.ter, weight: 10 },
    { value: ns.portfolio_quality.stock_count, weight: 10 },
    { value: ns.portfolio_quality.top10, weight: 10 },
    { value: ns.portfolio_quality.top3_sector, weight: 10 },
  ]);

  return {
    consistency: consistencyScore,
    recent_performance: recentPerformanceScore,
    risk: riskScore,
    valuation: valuationScore,
    portfolio_quality: portfolioQualityScore,
  };
}

/**
 * Calculate overall weighted score
 * Returns null if ANY metric is missing (strict requirement)
 */
export function calculateOverallScore(
  ns: NormalizedSubScores,
  weights: WeightPreset = WEIGHT_PRESETS.balanced
): number | null {
  const mainScores = calculateMainScores(ns);

  // Check if ALL 5 main categories have scores
  // If ANY category is missing, return null (don't score the fund)
  if (
    mainScores.consistency == null ||
    mainScores.recent_performance == null ||
    mainScores.risk == null ||
    mainScores.valuation == null ||
    mainScores.portfolio_quality == null
  ) {
    return null;
  }

  // All categories present - calculate weighted score
  const overallScore =
    (mainScores.consistency * weights.consistency +
      mainScores.recent_performance * weights.recent_performance +
      mainScores.risk * weights.risk +
      mainScores.valuation * weights.valuation +
      mainScores.portfolio_quality * weights.portfolio_quality) /
    100;

  return Math.round(overallScore * 10) / 10; // Round to 1 decimal
}
