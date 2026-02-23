import { NextResponse } from "next/server";
import { WEIGHT_PRESETS } from "@/lib/scoreCalculator";

/**
 * GET /api/weights
 * Returns the default weight presets
 */
export async function GET() {
  return NextResponse.json({
    presets: WEIGHT_PRESETS,
    default: "balanced",
  });
}
