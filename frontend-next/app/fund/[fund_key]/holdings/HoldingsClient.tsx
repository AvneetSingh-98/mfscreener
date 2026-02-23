"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { getAllocationColor } from "@/lib/colorUtils";

interface HoldingsClientProps {
  fundDetail: any;
}

export default function HoldingsClient({ fundDetail }: HoldingsClientProps) {
  const [isMobile, setIsMobile] = useState(false);

  // Detect mobile viewport
  useEffect(() => {
    const checkMobile = () => setIsMobile(window.innerWidth < 768);
    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  const { fund_info, portfolio } = fundDetail;

  if (!portfolio || !portfolio.holdings || portfolio.holdings.length === 0) {
    return (
      <div style={{ 
        padding: isMobile ? 16 : 24, 
        maxWidth: 1400, 
        margin: "0 auto",
        backgroundColor: "var(--bg-page)",
        minHeight: "100vh"
      }}>
        <p style={{ color: "var(--text-secondary)" }}>No holdings data available</p>
      </div>
    );
  }

  // Group holdings by section (equity, debt, others)
  const equityHoldings = portfolio.holdings.filter((h: any) => h.section === "equity");
  const debtHoldings = portfolio.holdings.filter((h: any) => h.section === "debt");
  const otherHoldings = portfolio.holdings.filter((h: any) => 
    h.section !== "equity" && h.section !== "debt"
  );
  
  // Calculate percentages
  const equityPercentage = equityHoldings.reduce((sum: number, h: any) => sum + (h.weight || 0), 0);
  const debtPercentage = debtHoldings.reduce((sum: number, h: any) => sum + (h.weight || 0), 0);
  const othersPercentage = otherHoldings.reduce((sum: number, h: any) => sum + (h.weight || 0), 0);

  // Render holdings as cards on mobile
  const renderHoldingsCards = (holdings: any[], sectionColor: string) => (
    <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
      {holdings.map((holding: any, idx: number) => {
        const weight = holding.weight || 0;
        const weightColor = getAllocationColor(weight);
        
        return (
          <div
            key={idx}
            style={{
              padding: 16,
              backgroundColor: "var(--bg-card)",
              borderRadius: 16,
              border: "1px solid var(--border-default)",
              boxShadow: "0 4px 6px rgba(0, 0, 0, 0.3)",
              transition: "all 0.2s ease",
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.boxShadow = "0 10px 15px rgba(0, 0, 0, 0.4)";
              e.currentTarget.style.transform = "translateY(-2px)";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.boxShadow = "0 4px 6px rgba(0, 0, 0, 0.3)";
              e.currentTarget.style.transform = "translateY(0)";
            }}
          >
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
              <div style={{ flex: 1 }}>
                <div style={{ fontSize: 12, color: "var(--text-muted)", marginBottom: 4 }}>
                  #{idx + 1}
                </div>
                <div style={{ fontSize: 15, fontWeight: 600, color: "var(--text-primary)", marginBottom: 8 }}>
                  {holding.company || holding.name || "Unknown"}
                </div>
              </div>
              <div style={{ textAlign: "right" }}>
                <div style={{ fontSize: 20, fontWeight: 700, color: weightColor }}>
                  {weight.toFixed(2)}%
                </div>
                <div style={{ fontSize: 11, color: "var(--text-muted)", marginTop: 2 }}>
                  Weight
                </div>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );

  // Render holdings as table on desktop
  const renderHoldingsTable = (holdings: any[]) => (
    <table style={{ width: "100%", borderCollapse: "collapse" }}>
      <thead>
        <tr style={{ borderBottom: "2px solid var(--border-default)" }}>
          <th style={{ textAlign: "left", padding: "8px 0", fontSize: 13, color: "var(--text-secondary)" }}>#</th>
          <th style={{ textAlign: "left", padding: "8px 0", fontSize: 13, color: "var(--text-secondary)" }}>Company</th>
          <th style={{ textAlign: "right", padding: "8px 0", fontSize: 13, color: "var(--text-secondary)" }}>Weight %</th>
        </tr>
      </thead>
      <tbody>
        {holdings.map((holding: any, idx: number) => {
          const weight = holding.weight || 0;
          const weightColor = getAllocationColor(weight);
          
          return (
            <tr key={idx} style={{ 
              borderBottom: "1px solid var(--border-default)",
              transition: "background-color 0.2s ease",
            }}
            onMouseEnter={(e) => e.currentTarget.style.backgroundColor = "var(--bg-card-hover)"}
            onMouseLeave={(e) => e.currentTarget.style.backgroundColor = "transparent"}
            >
              <td style={{ padding: "12px 0", fontSize: 14, color: "var(--text-secondary)" }}>{idx + 1}</td>
              <td style={{ padding: "12px 0", fontSize: 14, fontWeight: 600, color: "var(--text-primary)" }}>
                {holding.company || holding.name || "Unknown"}
              </td>
              <td style={{ padding: "12px 0", fontSize: 14, fontWeight: 600, textAlign: "right", color: weightColor }}>
                {weight.toFixed(2)}%
              </td>
            </tr>
          );
        })}
      </tbody>
    </table>
  );

  return (
    <div style={{ 
      padding: isMobile ? 16 : 24, 
      maxWidth: 1400, 
      margin: "0 auto",
      backgroundColor: "var(--bg-page)",
      minHeight: "100vh"
    }}>
      {/* Header */}
      <div style={{ marginBottom: 24 }}>
        <Link 
          href={`/fund/${fund_info.fund_key}`}
          style={{ 
            color: "var(--positive)", 
            textDecoration: "none", 
            fontSize: isMobile ? 13 : 14,
            display: "inline-block",
            minHeight: isMobile ? 40 : "auto",
            lineHeight: isMobile ? "40px" : "normal"
          }}
        >
          ← Back to Fund Details
        </Link>
        <h1 style={{ 
          fontSize: isMobile ? 22 : 28, 
          fontWeight: 700, 
          margin: "12px 0 8px 0",
          color: "var(--text-primary)"
        }}>
          All Holdings
        </h1>
        <div style={{ fontSize: isMobile ? 14 : 16, color: "var(--text-secondary)" }}>
          {fund_info.scheme_name}
        </div>
      </div>

      {/* Equity/Debt/Others Split */}
      <div style={{
        display: "grid",
        gridTemplateColumns: isMobile ? "1fr" : "1fr 1fr 1fr",
        gap: isMobile ? 12 : 24,
        marginBottom: 24
      }}>
        <div style={{
          padding: isMobile ? 16 : 20,
          backgroundColor: "var(--bg-card)",
          borderRadius: isMobile ? 12 : 8,
          border: "1px solid var(--border-default)",
          boxShadow: "0 4px 6px rgba(0, 0, 0, 0.3)"
        }}>
          <div style={{ fontSize: isMobile ? 13 : 14, color: "var(--text-secondary)", marginBottom: 4 }}>Equity Holdings</div>
          <div style={{ fontSize: isMobile ? 28 : 32, fontWeight: 700, color: "var(--positive)" }}>
            {equityPercentage.toFixed(2)}%
          </div>
          <div style={{ fontSize: isMobile ? 12 : 13, color: "var(--text-muted)", marginTop: 4 }}>
            {equityHoldings.length} stocks
          </div>
        </div>

        <div style={{
          padding: isMobile ? 16 : 20,
          backgroundColor: "var(--bg-card)",
          borderRadius: isMobile ? 12 : 8,
          border: "1px solid var(--border-default)",
          boxShadow: "0 4px 6px rgba(0, 0, 0, 0.3)"
        }}>
          <div style={{ fontSize: isMobile ? 13 : 14, color: "var(--text-secondary)", marginBottom: 4 }}>Debt Holdings</div>
          <div style={{ fontSize: isMobile ? 28 : 32, fontWeight: 700, color: "var(--warning)" }}>
            {debtPercentage.toFixed(2)}%
          </div>
          <div style={{ fontSize: isMobile ? 12 : 13, color: "var(--text-muted)", marginTop: 4 }}>
            {debtHoldings.length} holdings
          </div>
        </div>

        <div style={{
          padding: isMobile ? 16 : 20,
          backgroundColor: "var(--bg-card)",
          borderRadius: isMobile ? 12 : 8,
          border: "1px solid var(--border-default)",
          boxShadow: "0 4px 6px rgba(0, 0, 0, 0.3)"
        }}>
          <div style={{ fontSize: isMobile ? 13 : 14, color: "var(--text-secondary)", marginBottom: 4 }}>Others</div>
          <div style={{ fontSize: isMobile ? 28 : 32, fontWeight: 700, color: "var(--accent-purple)" }}>
            {othersPercentage.toFixed(2)}%
          </div>
          <div style={{ fontSize: isMobile ? 12 : 13, color: "var(--text-muted)", marginTop: 4 }}>
            {otherHoldings.length} holdings
          </div>
        </div>
      </div>

      {/* Equity Holdings Section */}
      {equityHoldings.length > 0 && (
        <div style={{
          padding: isMobile ? 16 : 20,
          backgroundColor: "var(--bg-card)",
          borderRadius: isMobile ? 16 : 16,
          border: "1px solid var(--border-default)",
          boxShadow: "0 4px 6px rgba(0, 0, 0, 0.3)",
          marginBottom: 24,
          transition: "all 0.2s ease",
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.boxShadow = "0 10px 15px rgba(0, 0, 0, 0.4)";
          e.currentTarget.style.transform = "translateY(-2px)";
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.boxShadow = "0 4px 6px rgba(0, 0, 0, 0.3)";
          e.currentTarget.style.transform = "translateY(0)";
        }}
        >
          <h2 style={{ 
            fontSize: isMobile ? 16 : 18, 
            fontWeight: 600, 
            marginBottom: 16, 
            color: "var(--positive)" 
          }}>
            Equity Holdings ({equityHoldings.length})
          </h2>
          {isMobile ? renderHoldingsCards(equityHoldings, "#10b981") : renderHoldingsTable(equityHoldings)}
        </div>
      )}

      {/* Debt Holdings Section */}
      {debtHoldings.length > 0 && (
        <div style={{
          padding: isMobile ? 16 : 20,
          backgroundColor: "var(--bg-card)",
          borderRadius: isMobile ? 16 : 16,
          border: "1px solid var(--border-default)",
          boxShadow: "0 4px 6px rgba(0, 0, 0, 0.3)",
          marginBottom: 24,
          transition: "all 0.2s ease",
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.boxShadow = "0 10px 15px rgba(0, 0, 0, 0.4)";
          e.currentTarget.style.transform = "translateY(-2px)";
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.boxShadow = "0 4px 6px rgba(0, 0, 0, 0.3)";
          e.currentTarget.style.transform = "translateY(0)";
        }}
        >
          <h2 style={{ 
            fontSize: isMobile ? 16 : 18, 
            fontWeight: 600, 
            marginBottom: 16, 
            color: "var(--warning)" 
          }}>
            Debt Holdings ({debtHoldings.length})
          </h2>
          {isMobile ? renderHoldingsCards(debtHoldings, "#f59e0b") : renderHoldingsTable(debtHoldings)}
        </div>
      )}

      {/* Others Holdings Section */}
      {otherHoldings.length > 0 && (
        <div style={{
          padding: isMobile ? 16 : 20,
          backgroundColor: "var(--bg-card)",
          borderRadius: isMobile ? 16 : 16,
          border: "1px solid var(--border-default)",
          boxShadow: "0 4px 6px rgba(0, 0, 0, 0.3)",
          transition: "all 0.2s ease",
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.boxShadow = "0 10px 15px rgba(0, 0, 0, 0.4)";
          e.currentTarget.style.transform = "translateY(-2px)";
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.boxShadow = "0 4px 6px rgba(0, 0, 0, 0.3)";
          e.currentTarget.style.transform = "translateY(0)";
        }}
        >
          <h2 style={{ 
            fontSize: isMobile ? 16 : 18, 
            fontWeight: 600, 
            marginBottom: 16, 
            color: "var(--accent-purple)" 
          }}>
            Other Holdings ({otherHoldings.length})
          </h2>
          {isMobile ? renderHoldingsCards(otherHoldings, "#8b5cf6") : renderHoldingsTable(otherHoldings)}
        </div>
      )}
    </div>
  );
}
