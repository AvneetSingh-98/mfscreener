import { NextRequest, NextResponse } from "next/server";
import { getDb } from "@/lib/db";

function categoryToCollection(category: string) {
  return `normalized_${category.replace("-", "_")}_scores`;
}

export async function GET(req: NextRequest) {
  try {
    const { searchParams } = new URL(req.url);
    const category = searchParams.get("category");

    if (!category) {
      return NextResponse.json(
        { error: "category query param required" },
        { status: 400 }
      );
    }

    const db = await getDb();
    
    // 1️⃣ Fund master (names, AMC, scheme_code, fund_key)
    const fundMaster = await db.collection("fund_master").find({}).toArray();

    // 2️⃣ Normalized scores collection
    const normalizedCollection = categoryToCollection(category);
    const normalizedScores = await db.collection(normalizedCollection).find({}).toArray();

    // 3️⃣ Join on scheme_code
    const scoreMap = new Map(
      normalizedScores.map((s) => [s.scheme_code, s])
    );

    const rows = fundMaster
      .filter((f) => f.category.toLowerCase().replace(" ", "-") === category)
      .map((fund) => {
        const score = scoreMap.get(fund.scheme_code);

        return {
          scheme_code: fund.scheme_code,
          fund_name: fund.scheme_name,
          amc: fund.amc,

          // metrics (NO scoring yet)
          cagr_1y: score?.metrics?.performance?.cagr_1y ?? null,
          cagr_3y: score?.metrics?.performance?.cagr_3y ?? null,
          cagr_5y: score?.metrics?.performance?.cagr_5y ?? null,
          return_3m: score?.metrics?.performance?.return_3m ?? null,
          return_6m: score?.metrics?.performance?.return_6m ?? null,

          sharpe_3y: score?.metrics?.risk_adjusted?.sharpe_3y ?? null,
          sortino_3y: score?.metrics?.risk_adjusted?.sortino_3y ?? null,
          information_ratio_3y:
            score?.metrics?.risk_adjusted?.information_ratio_3y ?? null,

          volatility: score?.metrics?.risk?.volatility ?? null,
          max_drawdown: score?.metrics?.risk?.max_drawdown ?? null,
        };
      });

    return NextResponse.json({ category, count: rows.length, rows });
  } catch (err: any) {
    console.error(err);
    return NextResponse.json(
      { error: err.message },
      { status: 500 }
    );
  }
}
