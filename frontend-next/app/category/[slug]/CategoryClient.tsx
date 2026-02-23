"use client";

import { useState, useMemo, useCallback } from "react";
import Link from "next/link";
import { calculateOverallScore, WeightPreset, WEIGHT_PRESETS } from "@/lib/scoreCalculator";
import { getScoreColor, getReturnColor } from "@/lib/colorUtils";
import WeightCustomizer from "./WeightCustomizer";
import { FundRankingRow } from "@/lib/types";

interface CategoryClientProps {
  initialRows: FundRankingRow[];
  categoryName: string;
}

type SortField = 
  | "overall_score"
  | "return_3m" | "return_6m" | "cagr_1y" | "cagr_3y" | "cagr_5y"
  | "rolling_3y" | "rolling_5y"
  | "volatility" | "up_beta" | "down_beta"
  | "sharpe" | "sortino" | "ir"
  | "aum" | "ter" | "turnover";

type SortDirection = "asc" | "desc";

// Formatting helpers
const score = (v?: number | null) => (v == null ? "—" : v.toFixed(1));
const percent = (v?: number | null) => (v == null ? "—" : v.toFixed(1) + "%");
const decimal = (v?: number | null) => (v == null ? "—" : v.toFixed(2));

// Clean fund name by removing common suffixes
const cleanFundName = (name: string) => {
  return name
    .replace(/\s*-\s*(Direct|Growth|Dividend|Regular|Plan|Option|IDCW).*$/i, '')
    .replace(/\s*\((Direct|Growth|Dividend|Regular|Plan|Option|IDCW).*\)$/i, '')
    .trim();
};

type MobileMetric = "overall_score" | "cagr_3y" | "cagr_5y" | "rolling_3y" | "rolling_5y" | "sharpe" | "sortino" | "volatility" | "ir" | "aum";

export default function CategoryClient({ initialRows, categoryName }: CategoryClientProps) {
  console.log("CategoryClient loaded");
  
  const [weights, setWeights] = useState<WeightPreset>(WEIGHT_PRESETS.balanced);
  const [searchQuery, setSearchQuery] = useState("");
  const [debouncedSearchQuery, setDebouncedSearchQuery] = useState("");
  const [selectedAMC, setSelectedAMC] = useState<string>("all");
  const [sortField, setSortField] = useState<SortField>("overall_score");
  const [sortDirection, setSortDirection] = useState<SortDirection>("desc");
  const [mobileMetric, setMobileMetric] = useState<MobileMetric>("overall_score");
  const [mobileViewMode, setMobileViewMode] = useState<"card" | "table">("card");
  
  console.log("mobileViewMode:", mobileViewMode);

  // Debounce search input
  const handleSearchChange = useCallback((value: string) => {
    setSearchQuery(value);
    
    // Debounce the actual search query used for filtering
    const timeoutId = setTimeout(() => {
      setDebouncedSearchQuery(value);
    }, 300);
    
    return () => clearTimeout(timeoutId);
  }, []);

  const uniqueAMCs = useMemo(() => {
    const amcs = new Set(initialRows.map(row => row.amc));
    return Array.from(amcs).sort();
  }, [initialRows]);

  const mobileMetrics = [
    { key: "overall_score" as MobileMetric, label: "Score", field: "overall_score" as SortField },
    { key: "cagr_3y" as MobileMetric, label: "3Y CAGR", field: "cagr_3y" as SortField },
    { key: "cagr_5y" as MobileMetric, label: "5Y CAGR", field: "cagr_5y" as SortField },
    { key: "rolling_3y" as MobileMetric, label: "Roll 3Y", field: "rolling_3y" as SortField },
    { key: "rolling_5y" as MobileMetric, label: "Roll 5Y", field: "rolling_5y" as SortField },
    { key: "sharpe" as MobileMetric, label: "Sharpe", field: "sharpe" as SortField },
    { key: "sortino" as MobileMetric, label: "Sortino", field: "sortino" as SortField },
    { key: "volatility" as MobileMetric, label: "Volatility", field: "volatility" as SortField },
    { key: "ir" as MobileMetric, label: "IR", field: "ir" as SortField },
    { key: "aum" as MobileMetric, label: "AUM", field: "aum" as SortField },
  ];

  const handleMobileMetricChange = (metric: MobileMetric, field: SortField) => {
    setMobileMetric(metric);
    setSortField(field);
    setSortDirection("desc");
  };

  const getMobileMetricValue = (r: FundRankingRow & { overall_score?: number | null }, metric: MobileMetric) => {
    const av = r.actual_values;
    switch (metric) {
      case "overall_score":
        return { value: r.overall_score, formatter: score, color: getScoreColor(r.overall_score) };
      case "cagr_3y":
        return { value: av.returns.cagr_3y, formatter: percent, color: getReturnColor(av.returns.cagr_3y) };
      case "cagr_5y":
        return { value: av.returns.cagr_5y, formatter: percent, color: getReturnColor(av.returns.cagr_5y) };
      case "rolling_3y":
        return { value: av.consistency.rolling_3y, formatter: decimal, color: "var(--text-primary)" };
      case "rolling_5y":
        return { value: av.consistency.rolling_5y, formatter: decimal, color: "var(--text-primary)" };
      case "sharpe":
        return { value: av.risk_adjusted.sharpe, formatter: decimal, color: "var(--text-primary)" };
      case "sortino":
        return { value: av.risk_adjusted.sortino, formatter: decimal, color: "var(--text-primary)" };
      case "volatility":
        return { value: av.risk.volatility, formatter: decimal, color: "var(--text-primary)" };
      case "ir":
        return { value: av.risk_adjusted.ir, formatter: decimal, color: "var(--text-primary)" };
      case "aum":
        return { 
          value: av.portfolio_quality.aum, 
          formatter: (v?: number | null) => v != null ? `₹${Math.round(v).toLocaleString()} Cr` : "—",
          color: "var(--text-primary)" 
        };
      default:
        return { value: null, formatter: score, color: "var(--text-muted)" };
    }
  };

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortDirection(sortDirection === "asc" ? "desc" : "asc");
    } else {
      setSortField(field);
      setSortDirection("desc");
    }
  };

  const sortedRows = useMemo(() => {
    const rowsWithScores = initialRows.map((row) => ({
      ...row,
      overall_score: calculateOverallScore(row.normalized_scores, weights),
    }));

    let filtered = rowsWithScores;

    if (debouncedSearchQuery.trim()) {
      const query = debouncedSearchQuery.toLowerCase();
      filtered = filtered.filter(
        (row) =>
          row.scheme_name.toLowerCase().includes(query) ||
          row.amc.toLowerCase().includes(query)
      );
    }

    if (selectedAMC !== "all") {
      filtered = filtered.filter((row) => row.amc === selectedAMC);
    }

    // First, assign ranks based on overall_score (descending)
    const rankedByScore = [...filtered].sort((a, b) => {
      const scoreA = a.overall_score ?? 0;
      const scoreB = b.overall_score ?? 0;
      return scoreB - scoreA;
    }).map((row, index) => ({
      ...row,
      scoreRank: index + 1,
    }));

    // Then sort by the selected field
    return rankedByScore.sort((a, b) => {
      let valA: number | null = null;
      let valB: number | null = null;

      switch (sortField) {
        case "overall_score":
          valA = a.overall_score;
          valB = b.overall_score;
          break;
        case "return_3m":
          valA = a.actual_values.returns.return_3m ?? null;
          valB = b.actual_values.returns.return_3m ?? null;
          break;
        case "return_6m":
          valA = a.actual_values.returns.return_6m ?? null;
          valB = b.actual_values.returns.return_6m ?? null;
          break;
        case "cagr_1y":
          valA = a.actual_values.returns.cagr_1y ?? null;
          valB = b.actual_values.returns.cagr_1y ?? null;
          break;
        case "cagr_3y":
          valA = a.actual_values.returns.cagr_3y ?? null;
          valB = b.actual_values.returns.cagr_3y ?? null;
          break;
        case "cagr_5y":
          valA = a.actual_values.returns.cagr_5y ?? null;
          valB = b.actual_values.returns.cagr_5y ?? null;
          break;
        case "rolling_3y":
          valA = a.actual_values.consistency.rolling_3y ?? null;
          valB = b.actual_values.consistency.rolling_3y ?? null;
          break;
        case "rolling_5y":
          valA = a.actual_values.consistency.rolling_5y ?? null;
          valB = b.actual_values.consistency.rolling_5y ?? null;
          break;
        case "volatility":
          valA = a.actual_values.risk.volatility ?? null;
          valB = b.actual_values.risk.volatility ?? null;
          break;
        case "up_beta":
          valA = a.actual_values.risk.up_beta ?? null;
          valB = b.actual_values.risk.up_beta ?? null;
          break;
        case "down_beta":
          valA = a.actual_values.risk.down_beta ?? null;
          valB = b.actual_values.risk.down_beta ?? null;
          break;
        case "sharpe":
          valA = a.actual_values.risk_adjusted.sharpe ?? null;
          valB = b.actual_values.risk_adjusted.sharpe ?? null;
          break;
        case "sortino":
          valA = a.actual_values.risk_adjusted.sortino ?? null;
          valB = b.actual_values.risk_adjusted.sortino ?? null;
          break;
        case "ir":
          valA = a.actual_values.risk_adjusted.ir ?? null;
          valB = b.actual_values.risk_adjusted.ir ?? null;
          break;
        case "aum":
          valA = a.actual_values.portfolio_quality.aum ?? null;
          valB = b.actual_values.portfolio_quality.aum ?? null;
          break;
        case "ter":
          valA = a.actual_values.portfolio_quality.ter ?? null;
          valB = b.actual_values.portfolio_quality.ter ?? null;
          break;
        case "turnover":
          valA = a.actual_values.portfolio_quality.turnover ?? null;
          valB = b.actual_values.portfolio_quality.turnover ?? null;
          break;
      }

      if (valA == null && valB == null) return 0;
      if (valA == null) return 1;
      if (valB == null) return -1;

      return sortDirection === "desc" ? valB - valA : valA - valB;
    });
  }, [initialRows, weights, debouncedSearchQuery, selectedAMC, sortField, sortDirection]);

  const SortableHeader = ({ field, children, align = "center", minWidth = 100 }: { field: SortField; children: React.ReactNode; align?: "left" | "center" | "right"; minWidth?: number }) => {
    const [isHovered, setIsHovered] = useState(false);
    const isActive = sortField === field;

    return (
      <th
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
        onClick={() => handleSort(field)}
        style={{
          cursor: "pointer",
          userSelect: "none",
          padding: "12px 8px",
          fontSize: 9,
          fontWeight: 700,
          color: isActive ? "var(--accent-teal)" : "var(--text-secondary)",
          backgroundColor: isHovered ? "rgba(255,255,255,0.05)" : "transparent",
          borderBottom: "1px solid var(--border-default)",
          transition: "all 0.15s ease",
          textAlign: align,
          textTransform: "uppercase",
          letterSpacing: "0.05em",
          fontFamily: "Inter, system-ui, sans-serif",
          lineHeight: 1.2,
          verticalAlign: "middle",
          minWidth: minWidth,
          maxWidth: minWidth + 20,
          height: "60px",
        }}
      >
        <div style={{ 
          display: "flex", 
          flexDirection: "column",
          alignItems: "center", 
          justifyContent: "center",
          gap: 3,
          height: "100%",
        }}>
          <span style={{ 
            display: "block",
            textAlign: "center",
          }}>
            {children}
          </span>
          {(isHovered || isActive) && (
            <span style={{ fontSize: 7, color: isActive ? "var(--accent-teal)" : "var(--text-muted)" }}>
              {isActive && sortDirection === "desc" ? "▼" : "▲"}
            </span>
          )}
        </div>
      </th>
    );
  };

  const TableRow = ({ r, i }: { r: FundRankingRow & { overall_score?: number | null }, i: number }) => {
    const [isHovered, setIsHovered] = useState(false);
    const av = r.actual_values;
    const bgColor = isHovered ? "var(--bg-card-hover)" : "transparent";

    return (
      <tr
        style={{
          borderBottom: "1px solid var(--border-default)",
          transition: "background-color 0.2s ease",
          backgroundColor: bgColor,
        }}
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
      >
        <td style={{
          padding: "14px 16px",
          fontWeight: 600,
          color: "var(--text-muted)",
          textAlign: "center",
          fontSize: 12,
          position: "sticky",
          left: 0,
          backgroundColor: bgColor,
          zIndex: 5,
          fontFamily: "'SF Mono', 'Monaco', monospace",
        }}>
          {i + 1}
        </td>
        <td style={{
          padding: "14px 16px",
          position: "sticky",
          left: 50,
          backgroundColor: bgColor,
          zIndex: 5,
          minWidth: 400,
          maxWidth: 400,
        }}>
          <Link
            href={`/fund/${r.fund_key}`}
            style={{
              color: "var(--text-primary)",
              textDecoration: "none",
              fontWeight: 600,
              fontSize: 13,
              transition: "color 0.15s",
              display: "block",
              overflow: "hidden",
              textOverflow: "ellipsis",
              whiteSpace: "nowrap",
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.color = "var(--text-primary)";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.color = "var(--text-primary)";
            }}
            title={r.scheme_name}
          >
            {r.scheme_name}
          </Link>
        </td>
        <td style={{ 
          padding: "14px 16px", 
          color: "var(--text-secondary)", 
          fontSize: 12, 
          fontWeight: 500,
          minWidth: 140,
          maxWidth: 200,
          overflow: "hidden",
          textOverflow: "ellipsis",
          whiteSpace: "nowrap",
        }}>
          {r.amc}
        </td>
        <td style={{
          padding: "14px 16px",
          textAlign: "center",
          fontWeight: 800,
          fontSize: 20,
          color: getScoreColor(r.overall_score),
          fontFamily: "'SF Mono', 'Monaco', monospace",
        }}>
          {score(r.overall_score)}
        </td>
        <td style={{ padding: "14px 12px", textAlign: "center", fontWeight: 700, fontSize: 13, color: getReturnColor(av.returns.return_3m), fontFamily: "'SF Mono', 'Monaco', monospace" }}>
          {percent(av.returns.return_3m)}
        </td>
        <td style={{ padding: "14px 12px", textAlign: "center", fontWeight: 700, fontSize: 13, color: getReturnColor(av.returns.return_6m), fontFamily: "'SF Mono', 'Monaco', monospace" }}>
          {percent(av.returns.return_6m)}
        </td>
        <td style={{ padding: "14px 12px", textAlign: "center", fontWeight: 700, fontSize: 13, color: getReturnColor(av.returns.cagr_1y), fontFamily: "'SF Mono', 'Monaco', monospace" }}>
          {percent(av.returns.cagr_1y)}
        </td>
        <td style={{ padding: "14px 12px", textAlign: "center", fontWeight: 700, fontSize: 13, color: getReturnColor(av.returns.cagr_3y), fontFamily: "'SF Mono', 'Monaco', monospace" }}>
          {percent(av.returns.cagr_3y)}
        </td>
        <td style={{ padding: "14px 12px", textAlign: "center", fontWeight: 700, fontSize: 13, color: getReturnColor(av.returns.cagr_5y), fontFamily: "'SF Mono', 'Monaco', monospace" }}>
          {percent(av.returns.cagr_5y)}
        </td>
        <td style={{ padding: "14px 12px", textAlign: "center", fontWeight: 600, fontSize: 13, color: "var(--text-primary)", fontFamily: "'SF Mono', 'Monaco', monospace" }}>
          {decimal(av.consistency.rolling_3y)}
        </td>
        <td style={{ padding: "14px 12px", textAlign: "center", fontWeight: 600, fontSize: 13, color: "var(--text-primary)", fontFamily: "'SF Mono', 'Monaco', monospace" }}>
          {decimal(av.consistency.rolling_5y)}
        </td>
        <td style={{ padding: "14px 12px", textAlign: "center", fontWeight: 600, fontSize: 13, color: "var(--text-primary)", fontFamily: "'SF Mono', 'Monaco', monospace" }}>
          {decimal(av.risk.volatility)}
        </td>
        <td style={{ padding: "14px 12px", textAlign: "center", fontWeight: 600, fontSize: 13, color: "var(--text-primary)", fontFamily: "'SF Mono', 'Monaco', monospace" }}>
          {decimal(av.risk.up_beta)}
        </td>
        <td style={{ padding: "14px 12px", textAlign: "center", fontWeight: 600, fontSize: 13, color: "var(--text-primary)", fontFamily: "'SF Mono', 'Monaco', monospace" }}>
          {decimal(av.risk.down_beta)}
        </td>
        <td style={{ padding: "14px 12px", textAlign: "center", fontWeight: 600, fontSize: 13, color: "var(--text-primary)", fontFamily: "'SF Mono', 'Monaco', monospace" }}>
          {decimal(av.risk_adjusted.sharpe)}
        </td>
        <td style={{ padding: "14px 12px", textAlign: "center", fontWeight: 600, fontSize: 13, color: "var(--text-primary)", fontFamily: "'SF Mono', 'Monaco', monospace" }}>
          {decimal(av.risk_adjusted.sortino)}
        </td>
        <td style={{ padding: "14px 12px", textAlign: "center", fontWeight: 600, fontSize: 13, color: "var(--text-primary)", fontFamily: "'SF Mono', 'Monaco', monospace" }}>
          {decimal(av.risk_adjusted.ir)}
        </td>
        <td style={{ padding: "14px 12px", textAlign: "right", fontWeight: 600, fontSize: 13, color: "var(--text-primary)", fontFamily: "'SF Mono', 'Monaco', monospace" }}>
          {av.portfolio_quality.aum != null ? Math.round(av.portfolio_quality.aum).toLocaleString() : "—"}
        </td>
        <td style={{ padding: "14px 12px", textAlign: "center", fontWeight: 600, fontSize: 13, color: "var(--text-primary)", fontFamily: "'SF Mono', 'Monaco', monospace" }}>
          {percent(av.portfolio_quality.ter)}
        </td>
        <td style={{ padding: "14px 12px", textAlign: "center", fontWeight: 600, fontSize: 13, color: "var(--text-primary)", fontFamily: "'SF Mono', 'Monaco', monospace" }}>
          {av.portfolio_quality.turnover != null ? percent(av.portfolio_quality.turnover * 100) : "—"}
        </td>
      </tr>
    );
  };

  return (
    <div style={{ backgroundColor: "var(--bg-page)", minHeight: "100vh", padding: "16px", fontFamily: "Inter, system-ui, sans-serif", overflowX: "hidden" }}>
      {/* Mobile/Desktop responsive styles */}
      <style jsx>{`
        .fund-card {
          background-color: var(--bg-card);
          border: 1px solid var(--border-default);
          border-radius: 16px;
          padding: 16px;
          margin-bottom: 16px;
          box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
          transition: all 0.2s ease;
        }
        .fund-card:hover {
          box-shadow: 0 10px 15px rgba(0, 0, 0, 0.4);
          transform: translateY(-2px);
        }
        .fund-card a {
          color: var(--text-primary);
        }
        .hide-scrollbar {
          scrollbar-width: none;
          -ms-overflow-style: none;
        }
        .hide-scrollbar::-webkit-scrollbar {
          display: none;
        }
        @media (max-width: 768px) {
          .desktop-table {
            display: none !important;
          }
          .mobile-cards {
            display: block !important;
          }
          .header-title {
            font-size: 24px !important;
          }
          .filter-container {
            flex-direction: column !important;
          }
          .filter-container > div {
            flex: 1 1 100% !important;
          }
        }
        @media (min-width: 769px) {
          .desktop-table {
            display: block !important;
          }
          .mobile-cards {
            display: none !important;
          }
        }
      `}</style>

      {/* Header */}
      <div style={{ marginBottom: 24, maxWidth: 1800, margin: "0 auto 24px auto", padding: "0 16px" }}>
        <h1 className="header-title" style={{ fontSize: 32, fontWeight: 700, color: "var(--text-primary)", marginBottom: 8, letterSpacing: "-0.02em" }}>
          {categoryName}
        </h1>
        <p style={{ fontSize: 14, color: "var(--text-secondary)", fontWeight: 500 }}>
          {sortedRows.length} of {initialRows.length} funds ranked
        </p>
      </div>

      <div style={{ maxWidth: 1800, margin: "0 auto", padding: "0 16px" }}>
        {/* Weight Customizer */}
        <WeightCustomizer onWeightsChange={setWeights} />

        {/* Search & Filter */}
        <div style={{
          marginBottom: 24,
          padding: "16px",
          backgroundColor: "var(--bg-card)",
          border: "1px solid var(--border-default)",
          borderRadius: 16,
          boxShadow: "0 4px 6px rgba(0, 0, 0, 0.3)",
        }}>
          <div className="filter-container" style={{ display: "flex", flexDirection: "column", gap: 12 }}>
            <div style={{ width: "100%" }}>
              <input
                type="text"
                placeholder="Search funds..."
                value={searchQuery}
                onChange={(e) => handleSearchChange(e.target.value)}
                style={{
                  width: "100%",
                  padding: "12px 16px",
                  fontSize: 14,
                  border: "1px solid var(--border-default)",
                  borderRadius: 12,
                  outline: "none",
                  transition: "all 0.2s ease",
                  backgroundColor: "var(--bg-card)",
                  color: "var(--text-primary)",
                  fontFamily: "Inter, system-ui, sans-serif",
                  boxSizing: "border-box",
                }}
                onFocus={(e) => {
                  e.target.style.borderColor = "var(--accent-primary)";
                  e.target.style.boxShadow = "0 0 0 3px rgba(59, 130, 246, 0.1)";
                }}
                onBlur={(e) => {
                  e.target.style.borderColor = "var(--border-default)";
                  e.target.style.boxShadow = "none";
                }}
              />
            </div>

            <div style={{ width: "100%" }}>
              <select
                value={selectedAMC}
                onChange={(e) => setSelectedAMC(e.target.value)}
                style={{
                  width: "100%",
                  padding: "12px 16px",
                  fontSize: 14,
                  border: "1px solid var(--border-default)",
                  borderRadius: 12,
                  outline: "none",
                  backgroundColor: "var(--bg-card)",
                  color: "var(--text-primary)",
                  cursor: "pointer",
                  fontWeight: 500,
                  fontFamily: "Inter, system-ui, sans-serif",
                  transition: "all 0.2s ease",
                  boxSizing: "border-box",
                }}
                onFocus={(e) => {
                  e.currentTarget.style.borderColor = "var(--accent-primary)";
                  e.currentTarget.style.boxShadow = "0 0 0 3px rgba(59, 130, 246, 0.1)";
                }}
                onBlur={(e) => {
                  e.currentTarget.style.borderColor = "var(--border-default)";
                  e.currentTarget.style.boxShadow = "none";
                }}
              >
                <option value="all">All AMCs</option>
                {uniqueAMCs.map((amc) => (
                  <option key={amc} value={amc}>{amc}</option>
                ))}
              </select>
            </div>

            {(searchQuery || selectedAMC !== "all") && (
              <button
                onClick={() => {
                  setSearchQuery("");
                  setDebouncedSearchQuery("");
                  setSelectedAMC("all");
                }}
                style={{
                  padding: "12px 20px",
                  fontSize: 13,
                  fontWeight: 600,
                  border: "1px solid var(--negative)",
                  borderRadius: 12,
                  backgroundColor: "transparent",
                  color: "var(--negative)",
                  cursor: "pointer",
                  transition: "all 0.2s ease",
                  fontFamily: "Inter, system-ui, sans-serif",
                  whiteSpace: "nowrap",
                  width: "100%",
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.backgroundColor = "var(--negative)";
                  e.currentTarget.style.color = "var(--bg-page)";
                  e.currentTarget.style.transform = "translateY(-1px)";
                  e.currentTarget.style.boxShadow = "0 4px 6px rgba(239, 68, 68, 0.3)";
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.backgroundColor = "transparent";
                  e.currentTarget.style.color = "var(--negative)";
                  e.currentTarget.style.transform = "translateY(0)";
                  e.currentTarget.style.boxShadow = "none";
                }}
              >
                Clear
              </button>
            )}
          </div>
        </div>

        {/* No Results */}
        {sortedRows.length === 0 ? (
          <div style={{
            padding: 40,
            textAlign: "center",
            backgroundColor: "var(--bg-card)",
            border: "1px solid var(--border-default)",
            borderRadius: 16,
            boxShadow: "0 4px 6px rgba(0, 0, 0, 0.3)",
          }}>
            <div style={{ fontSize: 18, fontWeight: 600, color: "var(--text-primary)", marginBottom: 8 }}>
              No funds found
            </div>
            <div style={{ fontSize: 14, color: "var(--text-muted)" }}>
              Try adjusting your search or filters
            </div>
          </div>
        ) : (
          <div>
            {/* Mobile View Toggle - Only on Mobile */}
            <div className="mobile-cards" style={{ display: "block", marginBottom: 16 }}>
              <div style={{ display: "flex", gap: 12, justifyContent: "flex-start" }}>
                <button
                  onClick={() => {
                    console.log("Card view clicked");
                    setMobileViewMode("card");
                  }}
                  style={{
                    padding: "10px 16px",
                    fontSize: 14,
                    fontWeight: 600,
                    borderRadius: 12,
                    border: "1px solid var(--border-default)",
                    backgroundColor: mobileViewMode === "card" ? "var(--accent-primary)" : "transparent",
                    color: mobileViewMode === "card" ? "#FFFFFF" : "var(--text-secondary)",
                    cursor: "pointer",
                    transition: "all 0.2s ease",
                    minHeight: 44,
                    display: "flex",
                    alignItems: "center",
                    gap: 8,
                  }}
                >
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <rect x="3" y="3" width="7" height="7" />
                    <rect x="14" y="3" width="7" height="7" />
                    <rect x="3" y="14" width="7" height="7" />
                    <rect x="14" y="14" width="7" height="7" />
                  </svg>
                </button>
                <button
                  onClick={() => {
                    console.log("Table view clicked");
                    setMobileViewMode("table");
                  }}
                  style={{
                    padding: "10px 16px",
                    fontSize: 14,
                    fontWeight: 600,
                    borderRadius: 12,
                    border: "1px solid var(--border-default)",
                    backgroundColor: mobileViewMode === "table" ? "var(--accent-primary)" : "transparent",
                    color: mobileViewMode === "table" ? "#FFFFFF" : "var(--text-secondary)",
                    cursor: "pointer",
                    transition: "all 0.2s ease",
                    minHeight: 44,
                    display: "flex",
                    alignItems: "center",
                    gap: 8,
                  }}
                >
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <line x1="8" y1="6" x2="21" y2="6" />
                    <line x1="8" y1="12" x2="21" y2="12" />
                    <line x1="8" y1="18" x2="21" y2="18" />
                    <line x1="3" y1="6" x2="3.01" y2="6" />
                    <line x1="3" y1="12" x2="3.01" y2="12" />
                    <line x1="3" y1="18" x2="3.01" y2="18" />
                  </svg>
                </button>
              </div>
            </div>

            {/* Mobile Metric Selector - Only on Mobile */}
            {mobileViewMode === "card" && (
              <div className="mobile-cards" style={{ display: "block", marginBottom: 20 }}>
                <div style={{ 
                  overflowX: "auto", 
                  WebkitOverflowScrolling: "touch",
                  scrollbarWidth: "none",
                  msOverflowStyle: "none",
                }}
                className="hide-scrollbar">
                  <div style={{ 
                    display: "flex", 
                    gap: 8,
                    paddingBottom: 4,
                    minWidth: "min-content",
                  }}>
                    {mobileMetrics.map((metric) => (
                    <button
                      key={metric.key}
                      onClick={() => handleMobileMetricChange(metric.key, metric.field)}
                      style={{
                        padding: "10px 20px",
                        fontSize: 14,
                        fontWeight: 600,
                        whiteSpace: "nowrap",
                        borderRadius: 12,
                        border: mobileMetric === metric.key ? "1px solid var(--accent-primary)" : "1px solid var(--border-default)",
                        backgroundColor: mobileMetric === metric.key ? "rgba(59, 130, 246, 0.15)" : "transparent",
                        color: mobileMetric === metric.key ? "var(--accent-primary)" : "var(--text-secondary)",
                        cursor: "pointer",
                        transition: "all 0.2s ease",
                        minHeight: 44,
                      }}
                    >
                      {metric.label}
                    </button>
                  ))}
                </div>
              </div>
              </div>
            )}

            {/* Mobile Card View */}
            {mobileViewMode === "card" && (
              <div className="mobile-cards" style={{ display: "block" }}>
                {sortedRows.map((r, i) => {
                const av = r.actual_values;
                const scoreClass = 
                  r.overall_score == null ? "" :
                  r.overall_score >= 80 ? "excellent" :
                  r.overall_score >= 60 ? "good" :
                  r.overall_score >= 40 ? "average" : "poor";
                
                return (
                  <div
                    key={`${r.scheme_code}-${i}`}
                    className="fund-card"
                  >
                    {/* Top Row: Rank/Fund/AMC (LEFT) + Score Badge (RIGHT) */}
                    <div style={{ 
                      display: "flex", 
                      gap: 16, 
                      marginBottom: 16,
                      alignItems: "flex-start",
                      justifyContent: "space-between",
                    }}>
                      {/* LEFT: Rank, Fund Name, AMC */}
                      <div style={{ flex: 1, minWidth: 0 }}>
                        {/* Rank # */}
                        <div style={{
                          fontSize: 14,
                          color: "var(--text-muted)",
                          marginBottom: 6,
                          fontFamily: "var(--font-mono)",
                          fontWeight: 600,
                        }}>
                          #{i + 1}
                        </div>

                        {/* Fund Name */}
                        <Link
                          href={`/fund/${r.fund_key}`}
                          style={{
                            fontSize: 17,
                            fontWeight: 700,
                            color: "var(--text-primary)",
                            lineHeight: 1.3,
                            fontFamily: "var(--font-display)",
                            textDecoration: "none",
                            transition: "color 0.2s ease",
                            marginBottom: 6,
                            display: "block",
                          }}
                        >
                          {r.scheme_name}
                        </Link>

                        {/* AMC Name */}
                        <div style={{
                          fontSize: 13,
                          color: "var(--text-muted)",
                          fontWeight: 500,
                        }}>
                          {r.amc}
                        </div>
                      </div>

                      {/* RIGHT: Large Score Badge */}
                      <div style={{
                        minHeight: 64,
                        minWidth: 64,
                        display: "flex",
                        flexDirection: "column",
                        alignItems: "center",
                        justifyContent: "center",
                        padding: "10px 14px",
                        borderRadius: 12,
                        backgroundColor: "var(--accent-primary)",
                        flexShrink: 0,
                      }}>
                        <div style={{
                          fontSize: 28,
                          fontWeight: 800,
                          color: "#FFFFFF",
                          lineHeight: 1,
                          fontFamily: "var(--font-mono)",
                        }}>
                          {score(r.overall_score)}
                        </div>
                        <div style={{
                          fontSize: 10,
                          color: "rgba(255, 255, 255, 0.8)",
                          marginTop: 4,
                          textTransform: "uppercase",
                          letterSpacing: "0.05em",
                          fontWeight: 600,
                        }}>
                          SCORE
                        </div>
                      </div>
                    </div>

                    {/* Key Metrics Grid */}
                    <div style={{ 
                      display: "grid", 
                      gridTemplateColumns: "1fr 1fr", 
                      gap: 12,
                      rowGap: 16,
                    }}>
                      <div>
                        <div style={{ 
                          fontSize: 10, 
                          color: "var(--text-muted)", 
                          marginBottom: 4,
                          textTransform: "uppercase",
                          letterSpacing: "0.05em",
                          fontWeight: 600,
                        }}>
                          3Y
                        </div>
                        <div className="metric-value" style={{ 
                          color: getReturnColor(av.returns.cagr_3y),
                          fontSize: 16,
                          fontWeight: 700,
                        }}>
                          {percent(av.returns.cagr_3y)}
                        </div>
                      </div>
                      <div>
                        <div style={{ 
                          fontSize: 10, 
                          color: "var(--text-muted)", 
                          marginBottom: 4,
                          textTransform: "uppercase",
                          letterSpacing: "0.05em",
                          fontWeight: 600,
                        }}>
                          5Y
                        </div>
                        <div className="metric-value" style={{ 
                          color: getReturnColor(av.returns.cagr_5y),
                          fontSize: 16,
                          fontWeight: 700,
                        }}>
                          {percent(av.returns.cagr_5y)}
                        </div>
                      </div>
                      <div>
                        <div style={{ 
                          fontSize: 10, 
                          color: "var(--text-muted)", 
                          marginBottom: 4,
                          textTransform: "uppercase",
                          letterSpacing: "0.05em",
                          fontWeight: 600,
                        }}>
                          Sharpe
                        </div>
                        <div className="metric-value" style={{ 
                          color: "var(--text-primary)",
                          fontSize: 16,
                          fontWeight: 700,
                        }}>
                          {decimal(av.risk_adjusted.sharpe)}
                        </div>
                      </div>
                      <div>
                        <div style={{ 
                          fontSize: 10, 
                          color: "var(--text-muted)", 
                          marginBottom: 4,
                          textTransform: "uppercase",
                          letterSpacing: "0.05em",
                          fontWeight: 600,
                        }}>
                          AUM
                        </div>
                        <div className="metric-value" style={{ 
                          color: "var(--text-primary)",
                          fontSize: 16,
                          fontWeight: 700,
                        }}>
                          {av.portfolio_quality.aum != null ? `₹${Math.round(av.portfolio_quality.aum).toLocaleString()} Cr` : "—"}
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })}
              </div>
            )}

            {/* Mobile Table View - Simple 2-column with metric selector */}
            {mobileViewMode === "table" && (
              <div className="mobile-cards" style={{ display: "block" }}>
                {/* Metric Selector for Table View */}
                <div style={{ marginBottom: 16 }}>
                  <div style={{ 
                    overflowX: "auto", 
                    WebkitOverflowScrolling: "touch",
                    scrollbarWidth: "none",
                    msOverflowStyle: "none",
                  }}
                  className="hide-scrollbar">
                    <div style={{ 
                      display: "flex", 
                      gap: 8,
                      paddingBottom: 4,
                      minWidth: "min-content",
                    }}>
                      {mobileMetrics.map((metric) => (
                        <button
                          key={metric.key}
                          onClick={() => handleMobileMetricChange(metric.key, metric.field)}
                          style={{
                            padding: "10px 20px",
                            fontSize: 14,
                            fontWeight: 600,
                            whiteSpace: "nowrap",
                            borderRadius: 12,
                            border: mobileMetric === metric.key ? "1px solid var(--accent-primary)" : "1px solid var(--border-default)",
                            backgroundColor: mobileMetric === metric.key ? "rgba(59, 130, 246, 0.15)" : "transparent",
                            color: mobileMetric === metric.key ? "var(--accent-primary)" : "var(--text-secondary)",
                            cursor: "pointer",
                            transition: "all 0.2s ease",
                            minHeight: 44,
                          }}
                        >
                          {metric.label}
                        </button>
                      ))}
                    </div>
                  </div>
                </div>

                {/* Simple 2-column table */}
                <div style={{
                  backgroundColor: "var(--bg-card)",
                  border: "1px solid var(--border-default)",
                  borderRadius: 16,
                  overflow: "hidden",
                  boxShadow: "0 4px 6px rgba(0, 0, 0, 0.3)",
                }}>
                  {/* Header Row */}
                  <div style={{
                    display: "grid",
                    gridTemplateColumns: "auto 1fr auto",
                    padding: "14px 20px",
                    backgroundColor: "var(--bg-elevated)",
                    borderBottom: "1px solid var(--border-default)",
                    gap: 16,
                  }}>
                    <div style={{
                      fontSize: 11,
                      fontWeight: 700,
                      color: "var(--text-muted)",
                      textTransform: "uppercase",
                      letterSpacing: "0.05em",
                      textAlign: "center",
                      minWidth: 40,
                    }}>
                      RANK
                    </div>
                    <div style={{
                      fontSize: 11,
                      fontWeight: 700,
                      color: "var(--text-muted)",
                      textTransform: "uppercase",
                      letterSpacing: "0.05em",
                    }}>
                      FUND
                    </div>
                    <div 
                      onClick={() => handleSort(mobileMetrics.find(m => m.key === mobileMetric)?.field || "overall_score")}
                      style={{
                        fontSize: 11,
                        fontWeight: 700,
                        color: sortField === mobileMetrics.find(m => m.key === mobileMetric)?.field ? "var(--accent-teal)" : "var(--text-muted)",
                        textTransform: "uppercase",
                        letterSpacing: "0.05em",
                        textAlign: "center",
                        minWidth: 80,
                        cursor: "pointer",
                        userSelect: "none",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        gap: 4,
                      }}
                    >
                      <span>{mobileMetrics.find(m => m.key === mobileMetric)?.label.toUpperCase()}</span>
                      {sortField === mobileMetrics.find(m => m.key === mobileMetric)?.field && (
                        <span style={{ fontSize: 9 }}>
                          {sortDirection === "desc" ? "▼" : "▲"}
                        </span>
                      )}
                    </div>
                  </div>

                  {/* Data Rows */}
                  {sortedRows.map((r, i) => {
                    const metricData = getMobileMetricValue(r, mobileMetric);
                    return (
                      <div
                        key={`${r.scheme_code}-${i}`}
                        style={{
                          display: "grid",
                          gridTemplateColumns: "auto 1fr auto",
                          padding: "16px 20px",
                          borderBottom: i < sortedRows.length - 1 ? "1px solid var(--border-default)" : "none",
                          transition: "background-color 0.2s ease",
                          backgroundColor: "transparent",
                          gap: 16,
                          alignItems: "center",
                        }}
                      >
                        {/* Rank */}
                        <div style={{
                          fontSize: 14,
                          fontWeight: 600,
                          color: "var(--text-muted)",
                          textAlign: "center",
                          fontFamily: "var(--font-mono)",
                          minWidth: 40,
                        }}>
                          {r.scoreRank}
                        </div>

                        {/* Fund Name + AMC */}
                        <Link
                          href={`/fund/${r.fund_key}`}
                          style={{
                            textDecoration: "none",
                            minWidth: 0,
                          }}
                        >
                          <div style={{
                            fontSize: 15,
                            fontWeight: 700,
                            color: "var(--text-primary)",
                            marginBottom: 4,
                            overflow: "hidden",
                            textOverflow: "ellipsis",
                            display: "-webkit-box",
                            WebkitLineClamp: 2,
                            WebkitBoxOrient: "vertical",
                            lineHeight: 1.3,
                          }}>
                            {cleanFundName(r.scheme_name)}
                          </div>
                          <div style={{
                            fontSize: 12,
                            color: "var(--text-muted)",
                            fontWeight: 500,
                          }}>
                            {r.amc}
                          </div>
                        </Link>

                        {/* Right: Metric Value */}
                        {mobileMetric === "overall_score" ? (
                          <div style={{
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                            minWidth: 70,
                            minHeight: 70,
                            padding: "12px 16px",
                            borderRadius: 12,
                            backgroundColor: "var(--accent-primary)",
                            flexShrink: 0,
                          }}>
                            <div style={{
                              display: "flex",
                              flexDirection: "column",
                              alignItems: "center",
                            }}>
                              <div style={{
                                fontSize: 26,
                                fontWeight: 800,
                                color: "#FFFFFF",
                                lineHeight: 1,
                                fontFamily: "var(--font-mono)",
                              }}>
                                {metricData.formatter(metricData.value)}
                              </div>
                              <div style={{
                                fontSize: 9,
                                color: "rgba(255, 255, 255, 0.8)",
                                marginTop: 4,
                                textTransform: "uppercase",
                                letterSpacing: "0.05em",
                                fontWeight: 600,
                              }}>
                                SCORE
                              </div>
                            </div>
                          </div>
                        ) : (
                          <div style={{
                            fontSize: 18,
                            fontWeight: 700,
                            color: metricData.color,
                            fontFamily: "var(--font-mono)",
                            textAlign: "center",
                            minWidth: 80,
                          }}>
                            {metricData.formatter(metricData.value)}
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {/* Desktop Table View */}
            <div className="desktop-table" style={{
              backgroundColor: "var(--bg-card)",
              border: "1px solid var(--border-default)",
              borderRadius: 16,
              overflow: "hidden",
              boxShadow: "0 4px 6px rgba(0, 0, 0, 0.3)",
            }}>
              <div style={{ overflowX: "auto" }}>
                <table style={{
                  width: "100%",
                  borderCollapse: "collapse",
                  fontSize: 13,
                  fontFamily: "Inter, system-ui, sans-serif",
                }}>
                  <thead>
                    <tr style={{ backgroundColor: "var(--bg-card)" }}>
                      <th style={{
                        padding: "10px 12px",
                        textAlign: "center",
                        fontSize: 9,
                        fontWeight: 700,
                        color: "var(--text-muted)",
                        borderBottom: "1px solid var(--border-default)",
                        position: "sticky",
                        left: 0,
                        backgroundColor: "var(--bg-page)",
                        zIndex: 10,
                        width: 50,
                        textTransform: "uppercase",
                        letterSpacing: "0.05em",
                        height: "45px",
                        verticalAlign: "middle",
                      }}>
                        #
                      </th>
                      <th style={{
                        padding: "10px 16px",
                        textAlign: "left",
                        fontSize: 9,
                        fontWeight: 700,
                        color: "var(--text-muted)",
                        borderBottom: "1px solid var(--border-default)",
                        minWidth: 400,
                        maxWidth: 400,
                        position: "sticky",
                        left: 50,
                        backgroundColor: "var(--bg-page)",
                        zIndex: 10,
                        textTransform: "uppercase",
                        letterSpacing: "0.05em",
                        height: "45px",
                        verticalAlign: "middle",
                      }}>
                        FUND NAME
                      </th>
                      <th style={{
                        padding: "10px 12px",
                        textAlign: "left",
                        fontSize: 9,
                        fontWeight: 700,
                        color: "var(--text-muted)",
                        borderBottom: "1px solid var(--border-default)",
                        minWidth: 140,
                        textTransform: "uppercase",
                        letterSpacing: "0.05em",
                        height: "45px",
                        verticalAlign: "middle",
                      }}>
                        AMC
                      </th>
                      <SortableHeader field="overall_score" minWidth={70}>SCORE</SortableHeader>
                      <SortableHeader field="return_3m" minWidth={80}>3M RET</SortableHeader>
                      <SortableHeader field="return_6m" minWidth={80}>6M RET</SortableHeader>
                      <SortableHeader field="cagr_1y" minWidth={70}>1Y CAGR</SortableHeader>
                      <SortableHeader field="cagr_3y" minWidth={70}>3Y CAGR</SortableHeader>
                      <SortableHeader field="cagr_5y" minWidth={70}>5Y CAGR</SortableHeader>
                      <SortableHeader field="rolling_3y" minWidth={100}>ROLL 3Y</SortableHeader>
                      <SortableHeader field="rolling_5y" minWidth={100}>ROLL 5Y</SortableHeader>
                      <SortableHeader field="volatility" minWidth={90}>VOL</SortableHeader>
                      <SortableHeader field="up_beta" minWidth={80}>UP β</SortableHeader>
                      <SortableHeader field="down_beta" minWidth={90}>DN β</SortableHeader>
                      <SortableHeader field="sharpe" minWidth={70}>SHARPE</SortableHeader>
                      <SortableHeader field="sortino" minWidth={70}>SORTINO</SortableHeader>
                      <SortableHeader field="ir" minWidth={110}>IR</SortableHeader>
                      <SortableHeader field="aum" align="right" minWidth={80}>AUM (CR)</SortableHeader>
                      <SortableHeader field="ter" minWidth={60}>TER</SortableHeader>
                      <SortableHeader field="turnover" minWidth={100}>TURN</SortableHeader>
                    </tr>
                  </thead>
                  <tbody>
                    {sortedRows.map((r, i) => (
                      <TableRow key={`${r.scheme_code}-${i}`} r={r} i={i} />
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
