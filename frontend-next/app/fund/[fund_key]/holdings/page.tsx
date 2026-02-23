import { headers } from "next/headers";
import CategoryNav from "@/Components/CategoryNav";
import HoldingsClient from "./HoldingsClient";

type PageProps = {
  params: Promise<{ fund_key: string }>;
};

export default async function HoldingsPage({ params }: PageProps) {
  const { fund_key } = await params;

  // Build absolute URL
  const h = await headers();
  const host = h.get("host");
  const protocol = process.env.NODE_ENV === "development" ? "http" : "https";

  if (!host) {
    throw new Error("Host header missing");
  }

  const detailUrl = `${protocol}://${host}/api/funds/${fund_key}/detail`;

  // Fetch fund detail
  const detailRes = await fetch(detailUrl, { cache: "no-store" });

  if (!detailRes.ok) {
    throw new Error("Failed to fetch fund details");
  }

  const fundDetail = await detailRes.json();

  return (
    <div style={{ backgroundColor: "var(--bg-page)", minHeight: "100vh" }}>
      <CategoryNav />
      <HoldingsClient fundDetail={fundDetail} />
    </div>
  );
}
