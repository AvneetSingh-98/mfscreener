import { FundRankingRow } from "./types";

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';

export async function getCategoryRankings(slug: string): Promise<FundRankingRow[]> {
  const res = await fetch(`${API_URL}/api/rankings?category=${slug}`, { cache: "no-store" });
  
  if (!res.ok) {
    throw new Error("Failed to fetch category rankings");
  }
  
  return res.json();
}
