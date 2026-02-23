import { NextRequest, NextResponse } from "next/server";
import { getDb } from "@/lib/db";
import { calculateOverallScore } from "@/lib/scoreCalculator";

/**
 * SLUG → NORMALIZED COLLECTION MAPPING
 * Maps URL slugs to normalized score collections
 */
const CATEGORY_CONFIG: Record<
  string,
  {
    displayName: string;
    normalizedCollection: string;
  }
> = {
  "large-cap": {
    displayName: "Large Cap",
    normalizedCollection: "normalized_large_cap_scores",
  },
  "mid-cap": {
    displayName: "Mid Cap",
    normalizedCollection: "normalized_mid_cap_scores",
  },
  "small-cap": {
    displayName: "Small Cap",
    normalizedCollection: "normalized_small_cap_scores",
  },
  "flexi-cap": {
    displayName: "Flexi Cap",
    normalizedCollection: "normalized_flexi_cap_scores",
  },
  "value": {
    displayName: "Value",
    normalizedCollection: "normalized_value_scores",
  },
  "contra": {
    displayName: "Contra",
    normalizedCollection: "normalized_contra_scores",
  },
  "focused": {
    displayName: "Focused",
    normalizedCollection: "normalized_focused_scores",
  },
  "elss": {
    displayName: "ELSS",
    normalizedCollection: "normalized_elss_scores",
  },
  "multi-cap": {
    displayName: "Multi Cap",
    normalizedCollection: "normalized_multi_cap_scores",
  },
  "large-and-mid-cap": {
    displayName: "Large & Mid Cap",
    normalizedCollection: "normalized_large_&_mid_cap_scores",
  },
  "large-mid-cap": {
    displayName: "Large & Mid Cap",
    normalizedCollection: "normalized_large_&_mid_cap_scores",
  },
  "healthcare": {
    displayName: "Healthcare",
    normalizedCollection: "normalized_healthcare_scores",
  },
  "banking-financial-services": {
    displayName: "Banking & Financial Services",
    normalizedCollection: "normalized_banking_&_financial_services_scores",
  },
  "technology": {
    displayName: "Technology",
    normalizedCollection: "normalized_technology_scores",
  },
  "quant": {
    displayName: "Quant",
    normalizedCollection: "normalized_quant_scores",
  },
  "infrastructure": {
    displayName: "Infrastructure",
    normalizedCollection: "normalized_infrastructure_scores",
  },
  "business-cycle": {
    displayName: "Business Cycle",
    normalizedCollection: "normalized_business_cycle_scores",
  },
  "esg": {
    displayName: "ESG",
    normalizedCollection: "normalized_esg_scores",
  },
  "consumption": {
    displayName: "Consumption",
    normalizedCollection: "normalized_consumption_scores",
  },
};

export async function GET(req: NextRequest) {
  try {
    const { searchParams } = new URL(req.url);
    const slug = searchParams.get("category");

    if (!slug || !CATEGORY_CONFIG[slug]) {
      return NextResponse.json(
        { error: "Invalid category" },
        { status: 400 }
      );
    }

    const config = CATEGORY_CONFIG[slug];
    const db = await getDb();

    // Fetch normalized scores
    const normalizedScores = await db
      .collection(config.normalizedCollection)
      .find({})
      .toArray();

    // Fetch fund master for display names
    const fundMaster = await db
      .collection("fund_master_v2")
      .find({})
      .toArray();

    const fundMap = Object.fromEntries(
      fundMaster.map((f: any) => [f.fund_key, f])
    );

    // Fetch actual values from score collections
    // Handle different collection naming patterns
    let scoreCollection = config.normalizedCollection.replace("normalized_", "score_").replace("_scores", "");
    
    // Special handling for categories with different naming conventions
    if (slug === "elss") {
      scoreCollection = "score_elss_cap";
    } else if (slug === "large-and-mid-cap" || slug === "large-mid-cap") {
      scoreCollection = "score_large_mid_cap";
    } else if (slug === "contra") {
      scoreCollection = "score_contra_cap";
    } else if (slug === "value") {
      scoreCollection = "score_value_cap";
    } else if (slug === "focused") {
      scoreCollection = "score_focused_cap";
    } else if (slug === "banking-financial-services") {
      scoreCollection = "score_banking_financial_services";
    } else if (slug === "business-cycle") {
      scoreCollection = "score_business_cycle";
    } else if (slug === "quant") {
      scoreCollection = "score_quant_multifactor";
    }
    
    const scoreData = await db
      .collection(scoreCollection)
      .find({})
      .toArray();

    const scoreMap = Object.fromEntries(
      scoreData.map((s: any) => [s.scheme_code, s])
    );

    // Fetch consistency data
    const consistencyCollection = `${scoreCollection}_consistency`;
    const consistencyData = await db
      .collection(consistencyCollection)
      .find({})
      .toArray();

    const consistencyMap = Object.fromEntries(
      consistencyData.map((c: any) => [c.scheme_code, c])
    );

    // Fetch qualitative attributes for AUM, TER, Turnover
    const qualData = await db
      .collection("qualitative_fund_attributes")
      .find({})
      .toArray();

    const qualMap = Object.fromEntries(
      qualData.map((q: any) => [q.fund_key, q])
    );

    // Transform normalized scores to frontend format
    const rows = normalizedScores.map((score: any) => {
      const fund = fundMap[score.fund_key] || {};
      const ns = score.normalized_sub_scores || {};
      const actualScore = scoreMap[score.scheme_code] || {};
      const consistency = consistencyMap[score.scheme_code] || {};
      const qual = qualMap[score.fund_key] || {};

      const perf = actualScore.metrics?.performance || {};
      const risk = actualScore.metrics?.risk || {};
      const riskAdj = actualScore.metrics?.risk_adjusted || {};
      const cons = consistency.consistency || {};

      // Map old field names to new alpha-based field names for consistency
      const consistencyNormalized = ns.consistency || {};
      const mappedConsistency = {
        alpha_3y: consistencyNormalized.alpha_3y ?? consistencyNormalized.rolling_3y,
        alpha_5y: consistencyNormalized.alpha_5y ?? consistencyNormalized.rolling_5y,
        confidence: consistencyNormalized.confidence,
        alpha_iqr_3y: consistencyNormalized.alpha_iqr_3y ?? consistencyNormalized.iqr_3y,
        alpha_iqr_5y: consistencyNormalized.alpha_iqr_5y ?? consistencyNormalized.iqr_5y,
      };

      // Debug logging for first fund
      if (score.scheme_code === "119678") {
        console.log("DEBUG - Fund 119678:");
        console.log("consistencyNormalized:", JSON.stringify(consistencyNormalized, null, 2));
        console.log("mappedConsistency:", JSON.stringify(mappedConsistency, null, 2));
        console.log("ns.returns:", JSON.stringify(ns.returns, null, 2));
        console.log("ns.risk:", JSON.stringify(ns.risk, null, 2));
        console.log("ns.risk_adjusted:", JSON.stringify(ns.risk_adjusted, null, 2));
        console.log("ns.portfolio_quality:", JSON.stringify(ns.portfolio_quality, null, 2));
        console.log("ns.valuation:", JSON.stringify(ns.valuation, null, 2));
      }

      const row = {
        scheme_code: score.scheme_code,
        fund_key: score.fund_key,
        scheme_name: fund.scheme_name || "Unknown Fund",
        amc: fund.amc || "Unknown AMC",

        // Normalized sub-scores (0-100 range) - for scoring only
        normalized_scores: {
          returns: ns.returns || {},
          consistency: mappedConsistency,
          risk: ns.risk || {},
          risk_adjusted: ns.risk_adjusted || {},
          portfolio_quality: ns.portfolio_quality || {},
          valuation: ns.valuation || {},
        },

        // Actual values for display
        actual_values: {
          returns: {
            return_3m: perf.return_3m,
            return_6m: perf.return_6m,
            cagr_1y: perf.cagr_1y,
            cagr_3y: perf.cagr_3y,
            cagr_5y: perf.cagr_5y,
          },
          consistency: {
            rolling_3y: cons.rolling_3y?.median,
            rolling_5y: cons.rolling_5y?.median,
          },
          risk: {
            volatility: risk.volatility,
            up_beta: riskAdj.upside_beta_3y,
            down_beta: riskAdj.downside_beta_3y,
          },
          risk_adjusted: {
            sharpe: riskAdj.sharpe_3y,
            sortino: riskAdj.sortino_3y,
            ir: riskAdj.information_ratio_3y,
          },
          portfolio_quality: {
            aum: qual.monthly_avg_aum_cr,
            ter: qual.ter_direct_pct,
            turnover: qual.portfolio_turnover,
          },
        },

        meta: score.meta || {},
      };

      // Calculate overall score using balanced weights
      const overallScore = calculateOverallScore(row.normalized_scores);
      
      // Debug logging for first fund
      if (score.scheme_code === "119678") {
        console.log("DEBUG - Overall score for 119678:", overallScore);
      }
      
      return {
        ...row,
        overall_score: overallScore,
      };
    });

    // Sort by overall score (descending), then by 3Y CAGR as tiebreaker
    rows.sort((a, b) => {
      const scoreA = a.overall_score ?? -Infinity;
      const scoreB = b.overall_score ?? -Infinity;
      
      if (scoreA !== scoreB) {
        return scoreB - scoreA;
      }
      
      // Tiebreaker: 3Y CAGR
      const cagr3yA = a.normalized_scores.returns.cagr_3y ?? -Infinity;
      const cagr3yB = b.normalized_scores.returns.cagr_3y ?? -Infinity;
      return cagr3yB - cagr3yA;
    });

    return NextResponse.json(rows);
  } catch (e) {
    console.error("API Error:", e);
    return NextResponse.json(
      { error: "Internal error", details: e instanceof Error ? e.message : String(e) },
      { status: 500 }
    );
  }
}

