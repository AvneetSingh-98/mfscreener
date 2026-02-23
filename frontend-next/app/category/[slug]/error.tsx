'use client';

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <div style={{
      backgroundColor: "var(--bg-page)",
      minHeight: "100vh",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      padding: "20px",
    }}>
      <div style={{
        backgroundColor: "var(--bg-card)",
        border: "1px solid var(--border-default)",
        borderRadius: 16,
        padding: "40px",
        maxWidth: "600px",
        textAlign: "center",
        boxShadow: "0 10px 15px rgba(0, 0, 0, 0.4)",
      }}>
        <div style={{
          fontSize: 48,
          marginBottom: 20,
        }}>⚠️</div>
        <h2 style={{
          fontSize: 24,
          fontWeight: 700,
          color: "var(--text-primary)",
          marginBottom: 16,
        }}>
          Database Connection Error
        </h2>
        <p style={{
          fontSize: 16,
          color: "var(--text-secondary)",
          marginBottom: 24,
          lineHeight: 1.6,
        }}>
          Unable to connect to the database. Please ensure MongoDB is running on localhost:27017.
        </p>
        <div style={{
          backgroundColor: "var(--bg-elevated)",
          border: "1px solid var(--border-default)",
          borderRadius: 12,
          padding: 16,
          marginBottom: 24,
          textAlign: "left",
        }}>
          <p style={{
            fontSize: 14,
            color: "var(--text-muted)",
            marginBottom: 8,
            fontWeight: 600,
          }}>
            Error Details:
          </p>
          <p style={{
            fontSize: 13,
            color: "var(--negative)",
            fontFamily: "'SF Mono', 'Monaco', monospace",
            wordBreak: "break-word",
          }}>
            {error.message}
          </p>
        </div>
        <button
          onClick={reset}
          style={{
            padding: "12px 24px",
            fontSize: 14,
            fontWeight: 700,
            borderRadius: 12,
            border: "1px solid var(--positive)",
            backgroundColor: "var(--positive)",
            color: "var(--bg-page)",
            cursor: "pointer",
            transition: "all 0.2s ease",
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.backgroundColor = "#10B981";
            e.currentTarget.style.transform = "translateY(-1px)";
            e.currentTarget.style.boxShadow = "0 4px 6px rgba(34, 197, 94, 0.3)";
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.backgroundColor = "var(--positive)";
            e.currentTarget.style.transform = "translateY(0)";
            e.currentTarget.style.boxShadow = "none";
          }}
        >
          Try Again
        </button>
      </div>
    </div>
  );
}
