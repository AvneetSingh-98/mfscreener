"use client";

import { useState, useEffect, useRef } from "react";
import { Line } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from "chart.js";

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

interface NAVChartProps {
  navData: {
    fund_nav: Array<{ date: string; nav: number }>;
    benchmark_nav: Array<{ date: string; nav: number }>;
    scheme_name: string;
    benchmark_name?: string;
  };
}

type TimePeriod = "3M" | "6M" | "1Y" | "3Y" | "5Y" | "ALL";

export default function NAVChart({ navData }: NAVChartProps) {
  const [selectedPeriod, setSelectedPeriod] = useState<TimePeriod>("1Y");
  const [isMobile, setIsMobile] = useState(false);
  const [chartHeight, setChartHeight] = useState(400);
  const chartRef = useRef<HTMLDivElement>(null);

  // Detect mobile viewport and calculate dynamic height - client-side only
  useEffect(() => {
    const checkMobile = () => {
      const width = window.innerWidth;
      setIsMobile(width < 768);
      
      // Calculate dynamic height
      if (width < 480) setChartHeight(280);
      else if (width < 768) setChartHeight(320);
      else if (width < 1024) setChartHeight(360);
      else setChartHeight(400);
    };
    
    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);
  
  // Filter data based on selected time period
  const filteredData = (() => {
    if (!navData || !navData.fund_nav || navData.fund_nav.length === 0) {
      return null;
    }

    const now = new Date();
    let cutoffDate: Date;

    switch (selectedPeriod) {
      case "3M":
        cutoffDate = new Date(now.setMonth(now.getMonth() - 3));
        break;
      case "6M":
        cutoffDate = new Date(now.setMonth(now.getMonth() - 6));
        break;
      case "1Y":
        cutoffDate = new Date(now.setFullYear(now.getFullYear() - 1));
        break;
      case "3Y":
        cutoffDate = new Date(now.setFullYear(now.getFullYear() - 3));
        break;
      case "5Y":
        cutoffDate = new Date(now.setFullYear(now.getFullYear() - 5));
        break;
      case "ALL":
        cutoffDate = new Date(0); // Beginning of time
        break;
      default:
        cutoffDate = new Date(now.setFullYear(now.getFullYear() - 1));
    }

    const filteredFundNav = navData.fund_nav.filter(
      (d) => new Date(d.date) >= cutoffDate
    );

    const filteredBenchmarkNav = navData.benchmark_nav
      ? navData.benchmark_nav.filter((d) => new Date(d.date) >= cutoffDate)
      : [];

    return {
      fundNav: filteredFundNav,
      benchmarkNav: filteredBenchmarkNav,
    };
  })();

  if (!filteredData) {
    return (
      <div style={{ padding: 40, textAlign: "center", backgroundColor: "var(--bg-card)", borderRadius: 8 }}>
        <p style={{ color: "var(--text-secondary)", fontSize: 14 }}>No NAV data available</p>
      </div>
    );
  }

  // Prepare data - show actual NAV values
  const fundDates = filteredData.fundNav.map((d) =>
    new Date(d.date).toLocaleDateString("en-IN", {
      day: "2-digit",
      month: "short",
      year: "numeric",
    })
  );
  const fundValues = filteredData.fundNav.map((d) => d.nav);

  // Prepare benchmark data if available
  let benchmarkValues: number[] = [];
  if (filteredData.benchmarkNav && filteredData.benchmarkNav.length > 0) {
    benchmarkValues = filteredData.benchmarkNav.map((d) => d.nav);
  }

  const data = {
    labels: fundDates,
    datasets: [
      {
        label: navData.scheme_name || "Fund NAV",
        data: fundValues,
        borderColor: "#3B82F6",
        backgroundColor: "rgba(59, 130, 246, 0.2)",
        borderWidth: 3,
        pointRadius: 0,
        pointHoverRadius: 6,
        pointHoverBackgroundColor: "#3B82F6",
        pointHoverBorderColor: "#FFFFFF",
        pointHoverBorderWidth: 2,
        fill: true,
        tension: 0.3,
        yAxisID: "y",
      },
      ...(benchmarkValues.length > 0
        ? [
            {
              label: navData.benchmark_name || "Benchmark",
              data: benchmarkValues,
              borderColor: "#F59E0B",
              backgroundColor: "rgba(245, 158, 11, 0.1)",
              borderWidth: 2.5,
              pointRadius: 0,
              pointHoverRadius: 6,
              pointHoverBackgroundColor: "#F59E0B",
              pointHoverBorderColor: "#FFFFFF",
              pointHoverBorderWidth: 2,
              fill: false,
              tension: 0.3,
              yAxisID: "y",
              borderDash: [5, 5],
            },
          ]
        : []),
    ],
  };

  const options: any = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: "top" as const,
        labels: {
          usePointStyle: true,
          padding: isMobile ? 10 : 15,
          font: {
            size: isMobile ? 11 : 13,
            weight: 500,
          },
          color: '#E5E7EB',
        },
      },
      tooltip: {
        mode: "index" as const,
        intersect: false,
        enabled: true,
        backgroundColor: "rgba(0, 0, 0, 0.9)",
        padding: 12,
        cornerRadius: 8,
        titleFont: {
          size: isMobile ? 12 : 13,
          weight: 600,
        },
        bodyFont: {
          size: isMobile ? 11 : 12,
        },
        callbacks: {
          label: function (context: any) {
            let label = context.dataset.label || "";
            if (label) {
              label += ": ";
            }
            if (context.parsed.y !== null) {
              label += "₹" + context.parsed.y.toFixed(2);
            }
            return label;
          },
        },
      },
    },
    scales: {
      x: {
        display: true,
        grid: {
          display: false,
          color: 'rgba(255, 255, 255, 0.1)',
        },
        ticks: {
          color: '#9CA3AF',
          maxTicksLimit: isMobile ? 6 : 15,
          font: {
            size: isMobile ? 9 : 10,
          },
          maxRotation: isMobile ? 45 : 45,
          minRotation: isMobile ? 45 : 45,
          autoSkip: true,
          autoSkipPadding: isMobile ? 20 : 10,
        },
      },
      y: {
        type: "linear" as const,
        display: true,
        position: "left" as const,
        title: {
          display: !isMobile,
          text: "NAV (₹)",
          color: '#9CA3AF',
          font: {
            size: 12,
            weight: 600,
          },
        },
        grid: {
          color: 'rgba(255, 255, 255, 0.1)',
          lineWidth: 1,
        },
        ticks: {
          color: '#9CA3AF',
          callback: function (value: any) {
            return "₹" + value.toFixed(0);
          },
          font: {
            size: isMobile ? 10 : 11,
          },
          maxTicksLimit: isMobile ? 6 : 8,
        },
      },
    },
    interaction: {
      mode: "nearest" as const,
      axis: "x" as const,
      intersect: false,
    },
  };

  const periods: TimePeriod[] = ["3M", "6M", "1Y", "3Y", "5Y", "ALL"];

  return (
    <div suppressHydrationWarning>
      {/* Time period buttons */}
      <div style={{ 
        display: "flex", 
        gap: isMobile ? 6 : 8, 
        marginBottom: 20, 
        justifyContent: "center",
        flexWrap: "wrap"
      }}
      role="group"
      aria-label="Time period selection"
      >
        {periods.map((period) => (
          <button
            key={period}
            onClick={() => setSelectedPeriod(period)}
            aria-label={`View ${period} performance`}
            aria-pressed={selectedPeriod === period}
            style={{
              padding: isMobile ? "8px 16px" : "10px 20px",
              borderRadius: 8,
              border: "1px solid var(--border-default)",
              backgroundColor: selectedPeriod === period ? "var(--accent-teal)" : "transparent",
              color: selectedPeriod === period ? "#000" : "var(--text-secondary)",
              fontSize: isMobile ? 12 : 14,
              fontWeight: 600,
              cursor: "pointer",
              transition: "all 0.2s ease",
              minHeight: isMobile ? 36 : 40,
            }}
            onMouseEnter={(e) => {
              if (selectedPeriod !== period) {
                e.currentTarget.style.backgroundColor = "rgba(255, 255, 255, 0.05)";
                e.currentTarget.style.color = "var(--text-primary)";
              }
            }}
            onMouseLeave={(e) => {
              if (selectedPeriod !== period) {
                e.currentTarget.style.backgroundColor = "transparent";
                e.currentTarget.style.color = "var(--text-secondary)";
              }
            }}
          >
            {period}
          </button>
        ))}
      </div>

      {/* Chart */}
      <div 
        ref={chartRef}
        style={{ 
          height: chartHeight, 
          position: "relative", 
          width: "100%",
          backgroundColor: "var(--bg-elevated)",
          border: "1px solid var(--border-default)",
          borderRadius: "16px",
          padding: "16px",
        }}
        role="img"
        aria-label={`NAV performance chart for ${navData.scheme_name || "fund"} showing ${filteredData.fundNav.length} data points over ${selectedPeriod} period`}
      >
        <Line data={data} options={options} />
      </div>

      {/* Data info */}
      <div style={{ 
        marginTop: 12, 
        fontSize: isMobile ? 11 : 12, 
        color: "var(--text-secondary)", 
        textAlign: "center" 
      }}
      aria-live="polite"
      >
        {filteredData.fundNav.length} data points
        {filteredData.benchmarkNav.length > 0 && ` • Benchmark: ${filteredData.benchmarkNav.length} points`}
      </div>
    </div>
  );
}
