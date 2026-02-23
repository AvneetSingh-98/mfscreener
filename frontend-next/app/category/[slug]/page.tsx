import { headers } from "next/headers";
import { FundRankingRow } from "@/lib/types";
import CategoryClient from "./CategoryClient";
import CategoryNav from "@/Components/CategoryNav";

type PageProps = {
  params: Promise<{ slug: string }>;
};

export default async function CategoryPage({ params }: PageProps) {
  // ✅ Next.js 16: params is async
  const { slug } = await params;

  // ✅ Build absolute URL (Node fetch requirement)
  const h = await headers();
  const host = h.get("host");
  const protocol = process.env.NODE_ENV === "development" ? "http" : "https";

  if (!host) {
    throw new Error("Host header missing");
  }

  const url = `${protocol}://${host}/api/rankings?category=${slug}`;

  const res = await fetch(url, { cache: "no-store" });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(`Failed to fetch rankings: ${errorData.error || res.statusText}`);
  }

  const rows: FundRankingRow[] = await res.json();

  const categoryName = slug.replace(/-/g, " ").toUpperCase();

  return (
    <div style={{ backgroundColor: "var(--bg-page)", minHeight: "100vh" }}>
      <CategoryNav />
      <CategoryClient initialRows={rows} categoryName={categoryName} />
    </div>
  );
}
