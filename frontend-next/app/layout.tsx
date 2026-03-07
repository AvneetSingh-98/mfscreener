import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: {
    default: "MF Screener - Best Mutual Fund Screener India 2026",
    template: "%s | MF Screener"
  },
  description: "India's most comprehensive mutual fund screener. Compare and analyze 1000+ equity mutual funds with advanced metrics, scoring, and filtering. Find the best mutual funds for your portfolio.",
  keywords: [
    "mutual fund screener India",
    "best mutual funds 2026",
    "mutual fund comparison",
    "equity mutual funds India",
    "mutual fund analysis",
    "fund screener",
    "mutual fund ranking",
    "SIP calculator",
    "large cap funds",
    "mid cap funds"
  ],
  authors: [{ name: "MF Screener" }],
  creator: "MF Screener",
  publisher: "MF Screener",
  metadataBase: new URL("https://mfscreener.co.in"),
  alternates: {
    canonical: "/"
  },
  openGraph: {
    type: "website",
    locale: "en_IN",
    url: "https://mfscreener.co.in",
    title: "MF Screener - Best Mutual Fund Screener India 2026",
    description: "India's most comprehensive mutual fund screener. Compare and analyze 1000+ equity mutual funds with advanced metrics and scoring.",
    siteName: "MF Screener"
  },
  twitter: {
    card: "summary_large_image",
    title: "MF Screener - Best Mutual Fund Screener India 2026",
    description: "India's most comprehensive mutual fund screener. Compare and analyze 1000+ equity mutual funds."
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      "max-video-preview": -1,
      "max-image-preview": "large",
      "max-snippet": -1
    }
  }
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body style={{ margin: 0, padding: 0, fontFamily: "system-ui, -apple-system, sans-serif", backgroundColor: "var(--bg-page)" }}>
        {children}
      </body>
    </html>
  );
}

