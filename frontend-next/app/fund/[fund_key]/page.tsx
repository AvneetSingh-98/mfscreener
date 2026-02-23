import { headers } from "next/headers";
import CategoryNav from "@/Components/CategoryNav";
import FundDetailClient from "./FundDetailClient";

type PageProps = {
  params: Promise<{ fund_key: string }>;
};

export default async function FundDetailPage({ params }: PageProps) {
  const { fund_key } = await params;

  // Build absolute URL
  const h = await headers();
  const host = h.get("host");
  const protocol = process.env.NODE_ENV === "development" ? "http" : "https";

  if (!host) {
    throw new Error("Host header missing");
  }

  const detailUrl = `${protocol}://${host}/api/funds/${fund_key}/detail`;
  const navUrl = `${protocol}://${host}/api/funds/${fund_key}/nav?days=all`; // Fetch complete history

  // Fetch fund detail and NAV history in parallel
  const [detailRes, navRes] = await Promise.all([
    fetch(detailUrl, { cache: "no-store" }),
    fetch(navUrl, { cache: "no-store" }),
  ]);

  if (!detailRes.ok) {
    throw new Error("Failed to fetch fund details");
  }

  const fundDetail = await detailRes.json();
  const navData = navRes.ok ? await navRes.json() : null;

  return (
    <div style={{ backgroundColor: "var(--bg-page)", minHeight: "100vh" }}>
      <CategoryNav />
      <FundDetailClient fundDetail={fundDetail} navData={navData} />
    </div>
  );
}
