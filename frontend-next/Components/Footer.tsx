"use client";

import Link from "next/link";

export default function Footer() {
  return (
    <footer style={{
      backgroundColor: "var(--bg-card)",
      borderTop: "1px solid var(--border-default)",
      padding: "40px 20px",
      marginTop: "60px",
      fontFamily: "Inter, system-ui, sans-serif"
    }}>
      <div style={{ maxWidth: 1200, margin: "0 auto" }}>
        <div style={{ 
          display: "grid", 
          gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
          gap: 40,
          marginBottom: 32
        }}>
          {/* About */}
          <div>
            <h3 style={{ 
              fontSize: 16, 
              fontWeight: 700, 
              color: "var(--text-primary)",
              marginBottom: 16
            }}>
              MF Screener
            </h3>
            <p style={{ 
              fontSize: 14, 
              color: "var(--text-secondary)",
              lineHeight: 1.6,
              margin: 0
            }}>
              India's most comprehensive mutual fund analysis platform. Compare and analyze 1000+ funds with advanced metrics.
            </p>
          </div>

          {/* Quick Links */}
          <div>
            <h4 style={{ 
              fontSize: 14, 
              fontWeight: 600, 
              color: "var(--text-primary)",
              marginBottom: 16,
              textTransform: "uppercase",
              letterSpacing: "0.05em"
            }}>
              Quick Links
            </h4>
            <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
              <Link href="/" style={{ 
                fontSize: 14, 
                color: "var(--text-secondary)",
                textDecoration: "none",
                transition: "color 0.2s"
              }}>
                Home
              </Link>
              <Link href="/category/large-cap" style={{ 
                fontSize: 14, 
                color: "var(--text-secondary)",
                textDecoration: "none",
                transition: "color 0.2s"
              }}>
                Large Cap Funds
              </Link>
              <Link href="/category/mid-cap" style={{ 
                fontSize: 14, 
                color: "var(--text-secondary)",
                textDecoration: "none",
                transition: "color 0.2s"
              }}>
                Mid Cap Funds
              </Link>
              <Link href="/category/small-cap" style={{ 
                fontSize: 14, 
                color: "var(--text-secondary)",
                textDecoration: "none",
                transition: "color 0.2s"
              }}>
                Small Cap Funds
              </Link>
            </div>
          </div>

          {/* Resources */}
          <div>
            <h4 style={{ 
              fontSize: 14, 
              fontWeight: 600, 
              color: "var(--text-primary)",
              marginBottom: 16,
              textTransform: "uppercase",
              letterSpacing: "0.05em"
            }}>
              Resources
            </h4>
            <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
              <Link href="/faq" style={{ 
                fontSize: 14, 
                color: "var(--accent-primary)",
                textDecoration: "none",
                fontWeight: 600,
                transition: "color 0.2s"
              }}>
                FAQ
              </Link>
            </div>
          </div>
        </div>

        {/* Bottom Bar */}
        <div style={{
          paddingTop: 24,
          borderTop: "1px solid var(--border-default)"
        }}>
          {/* Disclaimer */}
          <div style={{
            padding: "16px 20px",
            backgroundColor: "var(--bg-elevated)",
            borderRadius: 8,
            marginBottom: 16,
            border: "1px solid var(--border-default)"
          }}>
            <p style={{ 
              fontSize: 12, 
              color: "var(--text-muted)",
              margin: 0,
              lineHeight: 1.6
            }}>
              <strong style={{ color: "var(--text-secondary)" }}>Disclaimer:</strong> All fund data on MF Screener is sourced directly from AMFI (Association of Mutual Funds in India), NSE, and BSE. Our scores and metrics are independent analytical computations. We are not a SEBI Registered Investment Adviser and do not provide personalised investment advice. Scores and rankings are for informational purposes only.
            </p>
          </div>

          {/* Copyright */}
          <div style={{ textAlign: "center" }}>
            <p style={{ 
              fontSize: 13, 
              color: "var(--text-muted)",
              margin: 0
            }}>
              © {new Date().getFullYear()} MF Screener. All rights reserved.
            </p>
          </div>
        </div>
      </div>
    </footer>
  );
}
