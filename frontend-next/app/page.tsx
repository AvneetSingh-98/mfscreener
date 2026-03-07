"use client";

import Link from "next/link";
import FAQ from "@/Components/FAQ";
import { homepageFAQs } from "@/lib/faqData";
import Footer from "@/Components/Footer";

export default function HomePage() {
  return (
    <div style={{ 
      backgroundColor: "var(--bg-page)", 
      minHeight: "100vh", 
      padding: "40px 20px",
      fontFamily: "Inter, system-ui, sans-serif" 
    }}>
      <div style={{ maxWidth: 1200, margin: "0 auto" }}>
        {/* Hero Section */}
        <div style={{ textAlign: "center", marginBottom: 60 }}>
          <h1 style={{ 
            fontSize: 48, 
            fontWeight: 800, 
            color: "var(--text-primary)",
            marginBottom: 16,
            letterSpacing: "-0.02em"
          }}>
            India's Best Mutual Fund Screener
          </h1>
          <p style={{ 
            fontSize: 20, 
            color: "var(--text-secondary)",
            marginBottom: 32,
            lineHeight: 1.6
          }}>
            Compare and analyze 1000+ equity mutual funds with advanced metrics and scoring
          </p>
          <Link 
            href="/category/large-cap"
            style={{
              display: "inline-block",
              padding: "16px 32px",
              fontSize: 18,
              fontWeight: 600,
              backgroundColor: "var(--accent-primary)",
              color: "#FFFFFF",
              borderRadius: 12,
              textDecoration: "none",
              transition: "transform 0.2s ease, box-shadow 0.2s ease",
              boxShadow: "0 4px 12px rgba(59, 130, 246, 0.3)"
            }}
          >
            Start Screening Funds →
          </Link>
        </div>

        {/* Categories Grid */}
        <div style={{ marginBottom: 60 }}>
          <h2 style={{ 
            fontSize: 32, 
            fontWeight: 700, 
            color: "var(--text-primary)",
            marginBottom: 24,
            textAlign: "center"
          }}>
            Browse by Category
          </h2>
          <div style={{ 
            display: "grid", 
            gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))",
            gap: 20
          }}>
            {[
              { name: "Large Cap", slug: "large-cap", desc: "Top 100 companies" },
              { name: "Mid Cap", slug: "mid-cap", desc: "Companies 101-250" },
              { name: "Small Cap", slug: "small-cap", desc: "Companies 251+" },
              { name: "Flexi Cap", slug: "flexi-cap", desc: "Flexible allocation" },
              { name: "Multi Cap", slug: "multi-cap", desc: "All market caps" },
              { name: "Large & Mid Cap", slug: "large-mid-cap", desc: "Blend of large & mid" }
            ].map((cat) => (
              <Link
                key={cat.slug}
                href={`/category/${cat.slug}`}
                style={{
                  padding: 24,
                  backgroundColor: "var(--bg-card)",
                  border: "1px solid var(--border-default)",
                  borderRadius: 16,
                  textDecoration: "none",
                  transition: "all 0.2s ease",
                  boxShadow: "0 4px 6px rgba(0, 0, 0, 0.3)"
                }}
              >
                <h3 style={{ 
                  fontSize: 20, 
                  fontWeight: 700, 
                  color: "var(--text-primary)",
                  marginBottom: 8
                }}>
                  {cat.name}
                </h3>
                <p style={{ 
                  fontSize: 14, 
                  color: "var(--text-muted)",
                  margin: 0
                }}>
                  {cat.desc}
                </p>
              </Link>
            ))}
          </div>
        </div>

        {/* FAQ Section */}
        <FAQ items={homepageFAQs} />
      </div>

      {/* Footer */}
      <Footer />
    </div>
  );
}

