"use client";

import { useState } from "react";

export interface FAQItem {
  question: string;
  answer: string;
}

interface FAQProps {
  items: FAQItem[];
  title?: string;
}

export default function FAQ({ items, title = "Frequently Asked Questions" }: FAQProps) {
  const [openIndex, setOpenIndex] = useState<number | null>(null);

  const toggleFAQ = (index: number) => {
    setOpenIndex(openIndex === index ? null : index);
  };

  return (
    <div style={{
      backgroundColor: "var(--bg-card)",
      border: "1px solid var(--border-default)",
      borderRadius: 16,
      padding: "32px 24px",
      boxShadow: "0 4px 6px rgba(0, 0, 0, 0.3)",
      fontFamily: "Inter, system-ui, sans-serif"
    }}>
      <h2 style={{
        fontSize: 28,
        fontWeight: 700,
        color: "var(--text-primary)",
        marginBottom: 24,
        letterSpacing: "-0.02em"
      }}>
        {title}
      </h2>

      <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
        {items.map((item, index) => (
          <div
            key={index}
            style={{
              border: "1px solid var(--border-default)",
              borderRadius: 12,
              overflow: "hidden",
              transition: "all 0.2s ease"
            }}
          >
            <button
              onClick={() => toggleFAQ(index)}
              style={{
                width: "100%",
                padding: "16px 20px",
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                backgroundColor: openIndex === index ? "var(--bg-elevated)" : "transparent",
                border: "none",
                cursor: "pointer",
                textAlign: "left",
                transition: "background-color 0.2s ease"
              }}
              onMouseEnter={(e) => {
                if (openIndex !== index) {
                  e.currentTarget.style.backgroundColor = "var(--bg-elevated)";
                }
              }}
              onMouseLeave={(e) => {
                if (openIndex !== index) {
                  e.currentTarget.style.backgroundColor = "transparent";
                }
              }}
            >
              <span style={{
                fontSize: 16,
                fontWeight: 600,
                color: "var(--text-primary)",
                lineHeight: 1.4,
                paddingRight: 16
              }}>
                {item.question}
              </span>
              <span style={{
                fontSize: 20,
                color: "var(--text-muted)",
                transition: "transform 0.2s ease",
                transform: openIndex === index ? "rotate(180deg)" : "rotate(0deg)",
                flexShrink: 0
              }}>
                ▼
              </span>
            </button>

            {openIndex === index && (
              <div style={{
                padding: "0 20px 20px 20px",
                fontSize: 15,
                lineHeight: 1.6,
                color: "var(--text-secondary)",
                backgroundColor: "var(--bg-elevated)"
              }}>
                {item.answer}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
