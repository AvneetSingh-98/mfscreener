import { NextRequest, NextResponse } from "next/server";
import { getDb } from "@/lib/db";

export async function GET(
  req: NextRequest,
  { params }: { params: Promise<{ fund_key: string }> }
) {
  try {
    const { fund_key } = await params;

    if (!fund_key) {
      return NextResponse.json({ error: "Fund key is required" }, { status: 400 });
    }

    const db = await getDb();

    // Fetch all related data in parallel
    const [fundMaster, portfolioHoldings, sectorConcentration, qualitativeAttributes, normalizedScores] = await Promise.all([
      db.collection("fund_master_v2").findOne({ fund_key }),
      // Get the latest portfolio holdings by sorting by as_of date descending
      db.collection("portfolio_holdings_v2")
        .find({ fund_key })
        .sort({ as_of: -1 })
        .limit(1)
        .toArray()
        .then(results => results[0] || null),
      db.collection("qual_sector_concentration").findOne({ fund_key }),
      db.collection("qualitative_fund_attributes").findOne({ fund_key }),
      // Find normalized scores across all categories
      Promise.all([
        db.collection("normalized_large_cap_scores").findOne({ fund_key }),
        db.collection("normalized_mid_cap_scores").findOne({ fund_key }),
        db.collection("normalized_small_cap_scores").findOne({ fund_key }),
        db.collection("normalized_flexi_cap_scores").findOne({ fund_key }),
        db.collection("normalized_multi_cap_scores").findOne({ fund_key }),
        db.collection("normalized_value_scores").findOne({ fund_key }),
        db.collection("normalized_elss_scores").findOne({ fund_key }),
        db.collection("normalized_contra_scores").findOne({ fund_key }),
        db.collection("normalized_focused_scores").findOne({ fund_key }),
        db.collection("normalized_large_&_mid_cap_scores").findOne({ fund_key }),
      ]).then(results => results.find(r => r !== null)),
    ]);

    if (!fundMaster) {
      return NextResponse.json({ error: "Fund not found" }, { status: 404 });
    }

    // Build response
    const response = {
      fund_info: {
        scheme_code: fundMaster.scheme_code,
        fund_key: fundMaster.fund_key,
        scheme_name: fundMaster.scheme_name,
        amc: fundMaster.amc,
        category: fundMaster.category,
        sub_category: fundMaster.sub_category,
        asset_class: fundMaster.asset_class,
        benchmark: fundMaster.benchmark,
      },
      
      normalized_scores: normalizedScores ? {
        category: normalizedScores.category,
        sub_scores: normalizedScores.normalized_sub_scores,
        meta: normalizedScores.meta,
      } : null,

      portfolio: portfolioHoldings ? {
        holdings: portfolioHoldings.holdings || [],
        top_10_weight: portfolioHoldings.top_10_weight,
        equity_stock_count: portfolioHoldings.equity_stock_count || portfolioHoldings.metrics?.equity_stock_count,
        portfolio_valuation: portfolioHoldings.portfolio_valuation || {},
        as_of_date: portfolioHoldings.as_of_date,
      } : null,

      sector_concentration: sectorConcentration ? {
        sector_weights: sectorConcentration.sector_concentration?.sector_weights || {},
        top_sector_pct: sectorConcentration.sector_concentration?.top_sector_pct,
        top_3_sector_pct: sectorConcentration.sector_concentration?.top_3_sector_pct,
        hhi: sectorConcentration.sector_concentration?.hhi,
      } : null,

      qualitative_attributes: qualitativeAttributes ? {
        fund_manager: qualitativeAttributes.fund_manager || [],
        monthly_avg_aum_cr: qualitativeAttributes.monthly_avg_aum_cr,
        portfolio_turnover: qualitativeAttributes.portfolio_turnover,
        ter_direct_pct: qualitativeAttributes.ter_direct_pct,
        ter_regular_pct: qualitativeAttributes.ter_regular_pct,
        exit_load: qualitativeAttributes.exit_load,
        min_sip_amount: qualitativeAttributes.min_sip_amount,
        min_lumpsum_amount: qualitativeAttributes.min_lumpsum_amount,
      } : null,
    };

    return NextResponse.json(response);
  } catch (e) {
    console.error("API Error:", e);
    return NextResponse.json(
      { error: "Internal error", details: e instanceof Error ? e.message : String(e) },
      { status: 500 }
    );
  }
}
