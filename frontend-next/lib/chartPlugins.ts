// Chart.js plugin to force dark background
export const darkBackgroundPlugin = {
  id: "darkBackground",
  beforeDraw: (chart: any) => {
    const ctx = chart.ctx;
    ctx.save();
    ctx.globalCompositeOperation = "destination-over";
    ctx.fillStyle = "#0F172A"; // var(--bg-elevated)
    ctx.fillRect(0, 0, chart.width, chart.height);
    ctx.restore();
  },
};

// Common chart options for dark theme
export const darkChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      labels: {
        color: "#9CA3AF", // var(--text-secondary)
      },
    },
  },
  scales: {
    x: {
      ticks: {
        color: "#9CA3AF", // var(--text-secondary)
      },
      grid: {
        color: "rgba(255,255,255,0.05)",
      },
    },
    y: {
      ticks: {
        color: "#9CA3AF", // var(--text-secondary)
      },
      grid: {
        color: "rgba(255,255,255,0.05)",
      },
    },
  },
};
