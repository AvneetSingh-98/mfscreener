import { NextResponse } from "next/server";
import { CATEGORIES } from "@/lib/categories";

/**
 * GET /api/categories
 * Returns list of all available fund categories
 */
export async function GET() {
  return NextResponse.json({
    categories: CATEGORIES.map(cat => ({
      slug: cat.slug,
      label: cat.label,
      url: `/category/${cat.slug}`,
    })),
    total: CATEGORIES.length,
  });
}
