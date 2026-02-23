"use client";

import { useMemo, useState, useEffect, useRef } from "react";
import { Doughnut } from "react-chartjs-2";
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from "chart.js";

// Register Chart.js components
ChartJS.register(ArcElement, Tooltip, Legend);

interface SectorPieChartProps {
  sectorWeights: Record<string, number>;
}

export default function SectorPieChart({ sectorWeights }: SectorPieChartProps) {
  const [isMobile, setIsMobile] = useState(false);
  const chartRef = useRef<HTMLDivElement>(null);

  // Detect mobile viewport
  useEffect(() => {
    const checkMobile = () => setIsMobile(window.innerWidth < 768);
    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  // Calculate dynamic height based on viewport
  const chartHeight = useMemo(() => {
    if (typeof window !== 'undefined') {
      const width = window.innerWidth;
      if (width < 480) return 320; // Small mobile
      if (width < 768) return 360; // Mobile
      if (width < 1024) return 380; // Tablet
      return 400; // Desktop
    }
    return 350;
  }, [isMobile]);

  if (!sectorWeights || Object.keys(sectorWeights).length === 0) {
    return (
      <div style={{ padding: 40, textAlign: "center", backgroundColor: "var(--bg-page)", borderRadius: 8 }}>
        <p style={{ color: "var(--text-secondary)", fontSize: 14 }}>No sector data available</p>
      </div>
    );
  }

  // Sort sectors by weight and take top 10
  const sortedSectors = Object.entries(sectorWeights)
    .sort(([, a], [, b]) => b - a)
    .slice(0, 10);

  const labels = sortedSectors.map(([sector]) =>
    sector
      .split("_")
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(" ")
  );

  const values = sortedSectors.map(([, weight]) => weight);

  // Color palette - brighter colors for better visibility
  const colors = [
    "#3B82F6", // Bright Blue
    "#EF4444", // Bright Red
    "#22C55E", // Bright Green
    "#F59E0B", // Bright Orange
    "#A855F7", // Bright Purple
    "#14B8A6", // Bright Teal
    "#F97316", // Bright Deep Orange
    "#EC4899", // Bright Pink
    "#84CC16", // Bright Lime
    "#8B5CF6", // Bright Violet
  ];

  const data = {
    labels,
    datasets: [
      {
        data: values,
        backgroundColor: colors,
        borderColor: "var(--bg-card)",
        borderWidth: 3,
        hoverOffset: 12,
      },
    ],
  };

  const legendPosition = isMobile ? ("bottom" as const) : ("right" as const);
  
  const options: any = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: legendPosition,
        labels: {
          usePointStyle: true,
          padding: isMobile ? 10 : 15,
          color: '#F9FAFB',
          font: {
            size: isMobile ? 11 : 13,
            weight: '500',
          },
          boxWidth: isMobile ? 10 : 12,
          boxHeight: isMobile ? 10 : 12,
          generateLabels: function (chart: any) {
            const data = chart.data;
            if (data.labels.length && data.datasets.length) {
              return data.labels.map((label: string, i: number) => {
                const value = data.datasets[0].data[i];
                return {
                  text: `${label}: ${value.toFixed(1)}%`,
                  fillStyle: data.datasets[0].backgroundColor[i],
                  hidden: false,
                  index: i,
                  fontColor: '#F9FAFB',
                };
              });
            }
            return [];
          },
        },
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
            const label = context.label || "";
            const value = context.parsed || 0;
            return `${label}: ${value.toFixed(2)}%`;
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
        backgroundColor: "transparent",
      }}
      role="img"
      aria-label={`Sector allocation pie chart showing top ${sortedSectors.length} sectors: ${sortedSectors.map(([sector, weight]) => `${sector.replace(/_/g, ' ')}: ${weight.toFixed(1)}%`).join(', ')}`}
    >
      <Doughnut data={data} options={options} />
    </div>
  );
}
