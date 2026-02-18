"use client";

import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { CATEGORIES } from "@/lib/categories";

export default function CategoryNav() {
  const pathname = usePathname();
  const [activeTab, setActiveTab] = useState<"equity" | "sector">("equity");

  // Split categories into Equity and Sector/Thematic
  const equityCategories = CATEGORIES.filter(cat => 
    ["large-cap", "mid-cap", "small-cap", "flexi-cap", "elss", "focused", "value", "contra", "multi-cap", "large-mid-cap"].includes(cat.slug)
  );

  const sectorCategories = CATEGORIES.filter(cat => 
    ["healthcare", "banking-financial-services", "technology", "quant", "infrastructure", "business-cycle", "esg", "consumption"].includes(cat.slug)
  );

  const displayCategories = activeTab === "equity" ? equityCategories : sectorCategories;

  return (
    <div className="sticky top-0 z-50" style={{ 
      backgroundColor: "var(--bg-page)",
      borderBottom: "1px solid var(--border-default)"
    }}>
      <style jsx>{`
        .title-responsive {
          font-size: 28px;
        }
        
        @media (min-width: 480px) {
          .title-responsive {
            font-size: 36px;
          }
        }
        
        @media (min-width: 768px) {
          .title-responsive {
            font-size: 52px;
          }
        }
        
        .mobile-scroll-wrapper {
          position: relative;
          display: block;
        }
        
        @media (min-width: 768px) {
          .mobile-scroll-wrapper {
            display: none;
          }
        }
        
        .mobile-scroll-wrapper::after {
          content: '';
          position: absolute;
          right: 0;
          top: 0;
          bottom: 0;
          width: 40px;
          background: linear-gradient(to right, transparent, var(--bg-page));
          pointer-events: none;
        }
        
        @media (min-width: 768px) {
          .mobile-scroll-wrapper::after {
            display: none;
          }
        }
        
        .scroll-container {
          display: flex;
          gap: 8px;
          overflow-x: auto;
          padding: 8px 0;
          scrollbar-width: none;
          -ms-overflow-style: none;
        }
        
        .scroll-container::-webkit-scrollbar {
          display: none;
        }
        
        .nav-pill {
          display: inline-flex;
          align-items: center;
          padding: 12px 20px;
          border-radius: 12px;
          border: 1px solid var(--border-default);
          font-size: 14px;
          font-weight: 500;
          text-decoration: none;
          transition: all 0.2s ease;
          white-space: nowrap;
          min-height: 44px;
        }
        
        .nav-pill:not(.active) {
          background-color: var(--bg-card);
          color: var(--text-secondary);
        }
        
        .nav-pill:not(.active):hover {
          background-color: var(--bg-card-hover);
          border-color: var(--border-subtle);
          color: var(--text-primary);
        }
        
        .nav-pill.active {
          background-color: var(--accent-primary);
          border-color: var(--accent-primary);
          color: #FFFFFF;
          font-weight: 600;
        }
        
        /* Desktop: Wrapped Grid with better spacing */
        .desktop-nav {
          display: none;
          flex-wrap: wrap;
          gap: 24px;
          row-gap: 16px;
          max-width: 100%;
          justify-content: flex-start;
        }
        
        @media (min-width: 768px) {
          .desktop-nav {
            display: flex;
          }
        }
        
        .desktop-nav .nav-pill {
          flex: 0 0 auto;
          min-width: 160px;
          justify-content: center;
        }
        
        .padding-responsive {
          padding: 16px;
        }
        
        @media (min-width: 768px) {
          .padding-responsive {
            padding: 24px 32px;
          }
        }
      `}</style>
      
      <div className="padding-responsive">
        <h2 className="title-responsive" style={{ fontWeight: 700, marginBottom: "20px", color: "var(--text-primary)" }}>
          MF Screener
        </h2>
        
        {/* Equity / Sector Toggle */}
        <div style={{ 
          display: "flex", 
          gap: "12px", 
          marginBottom: "16px",
          borderBottom: "2px solid var(--border-default)",
          paddingBottom: "8px"
        }}>
          <button
            onClick={() => setActiveTab("equity")}
            style={{
              padding: "8px 24px",
              fontSize: "16px",
              fontWeight: 600,
              color: activeTab === "equity" ? "var(--accent-primary)" : "var(--text-secondary)",
              background: "transparent",
              border: "none",
              borderBottom: activeTab === "equity" ? "3px solid var(--accent-primary)" : "3px solid transparent",
              cursor: "pointer",
              transition: "all 0.2s",
              minHeight: "44px",
            }}
          >
            Equity
          </button>
          <button
            onClick={() => setActiveTab("sector")}
            style={{
              padding: "8px 24px",
              fontSize: "16px",
              fontWeight: 600,
              color: activeTab === "sector" ? "var(--accent-primary)" : "var(--text-secondary)",
              background: "transparent",
              border: "none",
              borderBottom: activeTab === "sector" ? "3px solid var(--accent-primary)" : "3px solid transparent",
              cursor: "pointer",
              transition: "all 0.2s",
              minHeight: "44px",
            }}
          >
            Sector / Thematic
          </button>
        </div>
        
        {/* Mobile: Horizontal Scrollable Pills with gradient indicator */}
        <div className="mobile-scroll-wrapper">
          <nav className="scroll-container">
            {displayCategories.map((cat) => {
              const href = `/category/${cat.slug}`;
              const active = pathname === href;

              return (
                <Link
                  key={cat.slug}
                  href={href}
                  className={`nav-pill ${active ? 'active' : ''}`}
                >
                  {cat.label}
                </Link>
              );
            })}
          </nav>
        </div>
        
        {/* Desktop: Wrapped Grid with better spacing */}
        <nav className="desktop-nav">
          {displayCategories.map((cat) => {
            const href = `/category/${cat.slug}`;
            const active = pathname === href;

            return (
              <Link
                key={cat.slug}
                href={href}
                className={`nav-pill ${active ? 'active' : ''}`}
              >
                {cat.label}
              </Link>
            );
          })}
        </nav>
      </div>
    </div>
  );
}
