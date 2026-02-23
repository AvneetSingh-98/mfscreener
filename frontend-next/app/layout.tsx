import "./globals.css";

export const metadata = {
  title: "MF Screener",
  description: "Mutual Fund Screener - Rank and compare equity mutual funds",
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

