"use client";

import { useState, useEffect, useRef } from "react";
import { Radar } from "react-chartjs-2";
import {
  Chart as ChartJS,
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend,
} from "chart.js";

// Register Chart.js components
ChartJS.register(RadialLinearScale, PointElement, LineElement, Filler, Tooltip, Legend);

interface ScoreRadarChartProps {
  mainScores: {
    consistency: number | null;
    recent_performance: number | null;
    risk: number | null;
    valuation: number | null;
    portfolio_quality: number | null;
  };
}

export default function ScoreRadarChart({ mainScores }: ScoreRadarChartProps) {
  const [isMobile, setIsMobile] = useState(false);
  const [chartHeight, setChartHeight] = useState(350);
  const chartRef = useRef<HTMLDivElement>(null);

  // Detect mobile viewport and calculate dynamic height - client-side only
  useEffect(() => {
    const checkMobile = () => {
      const width = window.innerWidth;
      setIsMobile(width < 768);
      
      // Calculate dynamic height
      if (width < 480) setChartHeight(280);
      else if (width < 768) setChartHeight(320);
      else if (width < 1024) setChartHeight(350);
      else setChartHeight(380);
    };
    
    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  const labels = [
    "Consistency",
    "Performance",
    "Risk",
    "Valuation",
    "Portfolio Quality",
  ];

  const values = [
    mainScores.consistency ?? 0,
    mainScores.recent_performance ?? 0,
    mainScores.risk ?? 0,
    mainScores.valuation ?? 0,
    mainScores.portfolio_quality ?? 0,
  ];

  const data = {
    labels,
    datasets: [
      {
        label: "Score",
        data: values,
        backgroundColor: "rgba(59, 130, 246, 0.25)",
        borderColor: "#3B82F6",
        borderWidth: 3,
        pointBackgroundColor: "#3B82F6",
        pointBorderColor: "#FFFFFF",
        pointHoverBackgroundColor: "#FFFFFF",
        pointHoverBorderColor: "#3B82F6",
        pointRadius: 5,
        pointHoverRadius: 7,
        pointBorderWidth: 2,
      },
    ],
  };

  const options: any = {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      r: {
        min: 0,
        max: 100,
        ticks: {
          display: false,
          backdropColor: "transparent",
        },
        pointLabels: {
          font: {
            size: isMobile ? 9 : 13,
            weight: 600,
          },
          color: '#E5E7EB',
          padding: isMobile ? 8 : 10,
        },
        grid: {
          color: 'rgba(255, 255, 255, 0.15)',
          lineWidth: 1,
        },
        angleLines: {
          color: 'rgba(255, 255, 255, 0.15)',
          lineWidth: 1,
        },
      },
    },
    plugins: {
      legend: {
        display: false,
      },
      tooltip: {
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
            return context.label + ": " + context.parsed.r.toFixed(1);
          },
        },
      },
    },
  };

  return (
    <div 
      ref={chartRef}
      suppressHydrationWarning
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
      aria-label={`Score breakdown radar chart showing Consistency: ${values[0].toFixed(1)}, Performance: ${values[1].toFixed(1)}, Risk: ${values[2].toFixed(1)}, Valuation: ${values[3].toFixed(1)}, Portfolio Quality: ${values[4].toFixed(1)}`}
    >
      <Radar data={data} options={options} />
    </div>
  );
}
