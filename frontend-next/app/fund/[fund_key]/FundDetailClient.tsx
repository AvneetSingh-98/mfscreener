"use client";

import { calculateMainScores, calculateOverallScore, WEIGHT_PRESETS } from "@/lib/scoreCalculator";
import Link from "next/link";
import NAVChart from "./NAVChart";
import ScoreRadarChart from "./ScoreRadarChart";
import SectorPieChart from "./SectorPieChart";

interface FundDetailClientProps {
  fundDetail: any;
  navData: any;
}

const score = (v?: number | null) => (v == null ? "—" : v.toFixed(1));

const getScoreColor = (v?: number | null): string => {
  if (v == null) return "#999";
  if (v >= 70) return "#22c55e";
  if (v >= 40) return "#eab308";
  return "#ef4444";
};

export default function FundDetailClient({ fundDetail, navData }: FundDetailClientProps) {
  const { fund_info, normalized_scores, portfolio, sector_concentration, qualitative_attributes } = fundDetail;

  // Calculate scores
  const mainScores = normalized_scores ? calculateMainScores(normalized_scores.sub_scores) : null;
  const overallScore = normalized_scores ? calculateOverallScore(normalized_scores.sub_scores, WEIGHT_PRESETS.balanced) : null;

  return (
    <div style={{ padding: 24, maxWidth: 1400, margin: "0 auto", backgroundColor: "var(--bg-page)", minHeight: "100vh" }}>
      {/* Header */}
      <div style={{ marginBottom: 24 }}>
        <Link 
          href={`/category/${fund_info.category.toLowerCase().replace(/ /g, "-").replace(/&/g, "and")}`}
          style={{ color: "var(--positive)", textDecoration: "none", fontSize: 14 }}
        >
          ← Back to {fund_info.category}
        </Link>
        <h1 style={{ fontSize: 28, fontWeight: 700, margin: "12px 0 8px 0", color: "var(--text-primary)" }}>
          {fund_info.scheme_name}
        </h1>
        <div style={{ fontSize: 16, color: "var(--text-secondary)" }}>
          {fund_info.amc} • {fund_info.category}
          {fund_info.benchmark && ` • Benchmark: ${fund_info.benchmark}`}
        </div>
      </div>

      {/* Overall Score and Radar Chart */}
      {overallScore != null && mainScores && (
        <div className="responsive-grid-2" style={{ display: "grid", gap: 24, marginBottom: 24 }}>
          {/* Overall Score Card */}
          <div style={{
            padding: 24,
            backgroundColor: "var(--bg-card)",
            borderRadius: 12,
            border: "1px solid var(--border-default)"
          }}>
            <div style={{ marginBottom: 24 }}>
              <div style={{ fontSize: 14, color: "var(--text-secondary)", marginBottom: 4 }}>Overall Score</div>
              <div style={{
                fontSize: 56,
                fontWeight: 700,
                color: getScoreColor(overallScore)
              }}>
                {score(overallScore)}
              </div>
            </div>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
              {Object.entries(mainScores).map(([key, value]) => (
                <div key={key} style={{
                  padding: 12,
                  backgroundColor: "var(--bg-elevated)",
                  borderRadius: 8,
                  border: "1px solid var(--border-default)"
                }}>
                  <div style={{ fontSize: 11, color: "var(--text-secondary)", marginBottom: 4, textTransform: "capitalize" }}>
                    {key.replace(/_/g, " ")}
                  </div>
                  <div style={{ fontSize: 20, fontWeight: 600, color: getScoreColor(value as number) }}>
                    {score(value as number)}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Score Radar Chart */}
          <div style={{
            padding: 24,
            backgroundColor: "var(--bg-card)",
            borderRadius: 12,
            border: "1px solid var(--border-default)"
          }}>
            <h3 style={{ fontSize: 16, fontWeight: 600, marginBottom: 16, color: "var(--text-primary)" }}>Score Breakdown</h3>
            <ScoreRadarChart mainScores={mainScores} />
          </div>
        </div>
      )}

      {/* Two Column Layout */}
      <div className="responsive-grid-2" style={{ display: "grid", gap: 24, marginBottom: 24 }}>
        
        {/* Qualitative Attributes */}
        {qualitative_attributes && (
          <div style={{
            padding: 20,
            backgroundColor: "var(--bg-card)",
            borderRadius: 8,
            border: "1px solid var(--border-default)"
          }}>
            <h2 style={{ fontSize: 18, fontWeight: 600, marginBottom: 16, color: "var(--text-primary)" }}>Fund Details</h2>
            <div style={{ display: "grid", gap: 12 }}>
              {qualitative_attributes.monthly_avg_aum_cr && (
                <div>
                  <div style={{ fontSize: 12, color: "var(--text-secondary)" }}>AUM</div>
                  <div style={{ fontSize: 16, fontWeight: 500, color: "var(--text-primary)" }}>
                    ₹{Math.round(qualitative_attributes.monthly_avg_aum_cr).toLocaleString()} Cr
                  </div>
                </div>
              )}
              {qualitative_attributes.ter_direct_pct != null && (
                <div>
                  <div style={{ fontSize: 12, color: "var(--text-secondary)" }}>TER (Direct)</div>
                  <div style={{ fontSize: 16, fontWeight: 500, color: "var(--text-primary)" }}>
                    {qualitative_attributes.ter_direct_pct.toFixed(2)}%
                  </div>
                </div>
              )}
              {qualitative_attributes.portfolio_turnover != null && (
                <div>
                  <div style={{ fontSize: 12, color: "var(--text-secondary)" }}>Portfolio Turnover</div>
                  <div style={{ fontSize: 16, fontWeight: 500, color: "var(--text-primary)" }}>
                    {(qualitative_attributes.portfolio_turnover * 100).toFixed(1)}%
                  </div>
                </div>
              )}
              {qualitative_attributes.fund_manager && qualitative_attributes.fund_manager.length > 0 && (
                <div>
                  <div style={{ fontSize: 12, color: "var(--text-secondary)" }}>Fund Manager(s)</div>
                  <div style={{ fontSize: 14, fontWeight: 500, color: "var(--text-primary)" }}>
                    {qualitative_attributes.fund_manager.map((m: any) => m.name || "Unknown").join(", ")}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Portfolio Stats */}
        {portfolio && (
          <div style={{
            padding: 20,
            backgroundColor: "var(--bg-card)",
            borderRadius: 8,
            border: "1px solid var(--border-default)"
          }}>
            <h2 style={{ fontSize: 18, fontWeight: 600, marginBottom: 16, color: "var(--text-primary)" }}>Portfolio Stats</h2>
            <div style={{ display: "grid", gap: 12 }}>
              {portfolio.equity_stock_count && (
                <div>
                  <div style={{ fontSize: 12, color: "var(--text-secondary)" }}>Number of Stocks</div>
                  <div style={{ fontSize: 16, fontWeight: 500, color: "var(--text-primary)" }}>{portfolio.equity_stock_count}</div>
                </div>
              )}
              {portfolio.top_10_weight != null && (
                <div>
                  <div style={{ fontSize: 12, color: "var(--text-secondary)" }}>Top 10 Holdings</div>
                  <div style={{ fontSize: 16, fontWeight: 500, color: "var(--text-primary)" }}>{portfolio.top_10_weight.toFixed(2)}%</div>
                </div>
              )}
              {portfolio.portfolio_valuation?.portfolio_pe && (
                <div>
                  <div style={{ fontSize: 12, color: "var(--text-secondary)" }}>Portfolio P/E</div>
                  <div style={{ fontSize: 16, fontWeight: 500, color: "var(--text-primary)" }}>
                    {portfolio.portfolio_valuation.portfolio_pe.toFixed(2)}
                  </div>
                </div>
              )}
              {portfolio.portfolio_valuation?.portfolio_pb && (
                <div>
                  <div style={{ fontSize: 12, color: "var(--text-secondary)" }}>Portfolio P/B</div>
                  <div style={{ fontSize: 16, fontWeight: 500, color: "var(--text-primary)" }}>
                    {portfolio.portfolio_valuation.portfolio_pb.toFixed(2)}
                  </div>
                </div>
              )}
              {portfolio.portfolio_valuation?.portfolio_roe && (
                <div>
                  <div style={{ fontSize: 12, color: "var(--text-secondary)" }}>Portfolio ROE</div>
                  <div style={{ fontSize: 16, fontWeight: 500, color: "var(--text-primary)" }}>
                    {portfolio.portfolio_valuation.portfolio_roe.toFixed(2)}%
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Sector Allocation with Pie Chart */}
      {sector_concentration && sector_concentration.sector_weights && (
        <div style={{
          padding: 20,
          backgroundColor: "var(--bg-card)",
          borderRadius: 8,
          border: "1px solid var(--border-default)",
          marginBottom: 24
        }}>
          <h2 style={{ fontSize: 18, fontWeight: 600, marginBottom: 16, color: "var(--text-primary)" }}>Sector Allocation</h2>
          <SectorPieChart sectorWeights={sector_concentration.sector_weights} />
        </div>
      )}

      {/* Top Holdings */}
      {portfolio && portfolio.holdings && portfolio.holdings.length > 0 && (
        <div style={{
          padding: 20,
          backgroundColor: "var(--bg-card)",
          borderRadius: 8,
          border: "1px solid var(--border-default)",
          marginBottom: 24
        }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
            <h2 style={{ fontSize: 18, fontWeight: 600, margin: 0, color: "var(--text-primary)" }}>Top 10 Holdings</h2>
            <Link
              href={`/fund/${fundDetail.fund_info.fund_key}/holdings`}
              style={{
                color: "var(--positive)",
                textDecoration: "none",
                fontSize: 14,
                fontWeight: 500,
                padding: "6px 12px",
                borderRadius: 6,
                border: "1px solid var(--positive)",
                transition: "all 0.2s",
              }}
            >
              View All Holdings →
            </Link>
          </div>
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr style={{ borderBottom: "2px solid var(--border-default)" }}>
                <th style={{ textAlign: "left", padding: "8px 0", fontSize: 13, color: "var(--text-secondary)" }}>#</th>
                <th style={{ textAlign: "left", padding: "8px 0", fontSize: 13, color: "var(--text-secondary)" }}>Company</th>
                <th style={{ textAlign: "left", padding: "8px 0", fontSize: 13, color: "var(--text-secondary)" }}>Sector</th>
                <th style={{ textAlign: "right", padding: "8px 0", fontSize: 13, color: "var(--text-secondary)" }}>Weight %</th>
              </tr>
            </thead>
            <tbody>
              {portfolio.holdings.slice(0, 10).map((holding: any, idx: number) => (
                <tr key={idx} style={{ borderBottom: "1px solid var(--border-default)" }}>
                  <td style={{ padding: "12px 0", fontSize: 14, color: "var(--text-primary)" }}>{idx + 1}</td>
                  <td style={{ padding: "12px 0", fontSize: 14, fontWeight: 500, color: "var(--text-primary)" }}>{holding.company || holding.name || "Unknown"}</td>
                  <td style={{ padding: "12px 0", fontSize: 14, color: "var(--text-secondary)", textTransform: "capitalize" }}>
                    {holding.sector?.replace(/_/g, " ") || "—"}
                  </td>
                  <td style={{ padding: "12px 0", fontSize: 14, fontWeight: 600, textAlign: "right", color: "var(--text-primary)" }}>
                    {holding.weight?.toFixed(2) || "—"}%
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* NAV Chart */}
      {navData && navData.fund_nav && navData.fund_nav.length > 0 && (
        <div style={{
          padding: 20,
          backgroundColor: "var(--bg-card)",
          borderRadius: 8,
          border: "1px solid var(--border-default)"
        }}>
          <h2 style={{ fontSize: 18, fontWeight: 600, marginBottom: 16, color: "var(--text-primary)" }}>NAV History</h2>
          <NAVChart navData={navData} />
        </div>
      )}
    </div>
  );
}
