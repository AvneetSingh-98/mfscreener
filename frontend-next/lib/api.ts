import { FundRankingRow } from "./types";

export async function getCategoryRankings(
  slug: string
): Promise<FundRankingRow[]> {
  const res = await fetch(
    `http://localhost:3000/api/rankings?category=${slug}`,
    { cache: "no-store" }
  );

  if (!res.ok) {
    throw new Error("Failed to fetch category rankings");
  }

  return res.json();
}
