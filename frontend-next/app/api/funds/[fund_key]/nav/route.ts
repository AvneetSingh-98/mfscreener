import { NextRequest, NextResponse } from "next/server";
import { getDb } from "@/lib/db";

export async function GET(
  req: NextRequest,
  { params }: { params: Promise<{ fund_key: string }> }
) {
  try {
    const { fund_key } = await params;
    const { searchParams } = new URL(req.url);
    
    // Optional date range filters
    const startDate = searchParams.get("start_date");
    const endDate = searchParams.get("end_date");
    const days = searchParams.get("days"); // e.g., 365 for 1 year, or "all" for complete history

    if (!fund_key) {
      return NextResponse.json({ error: "Fund key is required" }, { status: 400 });
    }

    const db = await getDb();

    // Get fund info and benchmark mapping
    const [fundMaster, benchmarkMap] = await Promise.all([
      db.collection("fund_master_v2").findOne({ fund_key }),
      db.collection("fund_benchmark_map").findOne({ fund_key }),
    ]);
    
    if (!fundMaster) {
      return NextResponse.json({ error: "Fund not found" }, { status: 404 });
    }

    // Build date filter
    const dateFilter: any = {};
    if (days && days !== "all") {
      const daysAgo = new Date();
      daysAgo.setDate(daysAgo.getDate() - parseInt(days));
      dateFilter.$gte = daysAgo;
    } else if (startDate || endDate) {
      if (startDate) dateFilter.$gte = new Date(startDate);
      if (endDate) dateFilter.$lte = new Date(endDate);
    }

    // Fetch NAV history
    const navQuery: any = { scheme_code: fundMaster.scheme_code };
    if (Object.keys(dateFilter).length > 0) {
      navQuery.date = dateFilter;
    }

    const fundNavHistory = await db
      .collection("nav_history")
      .find(navQuery)
      .sort({ date: 1 })
      .toArray();

    // Fetch benchmark history if available
    let benchmarkNavHistory: any[] = [];
    const benchmarkName = benchmarkMap?.benchmark || fundMaster.benchmark;
    
    if (benchmarkName) {
      const benchmarkQuery: any = { benchmark: benchmarkName };
      if (Object.keys(dateFilter).length > 0) {
        benchmarkQuery.date = dateFilter;
      }

      benchmarkNavHistory = await db
        .collection("benchmark_nav")
        .find(benchmarkQuery)
        .sort({ date: 1 })
        .toArray();
    }

    // Format response
    const response = {
      fund_key,
      scheme_code: fundMaster.scheme_code,
      scheme_name: fundMaster.scheme_name,
      benchmark_name: benchmarkName,
      
      fund_nav: fundNavHistory.map((nav: any) => ({
        date: nav.date,
        nav: nav.nav,
      })),
      
      benchmark_nav: benchmarkNavHistory.map((bench: any) => ({
        date: bench.date,
        nav: bench.nav,
      })),
      
      data_points: {
        fund: fundNavHistory.length,
        benchmark: benchmarkNavHistory.length,
      },
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
