import type { ChartData, ChartOptions } from "chart.js";
import type { VisualizationConfig } from "../types";

const PALETTE = [
  "#3B82F6", // blue
  "#10B981", // emerald
  "#F59E0B", // amber
  "#EF4444", // red
  "#8B5CF6", // violet
  "#EC4899", // pink
  "#06B6D4", // cyan
  "#F97316", // orange
  "#14B8A6", // teal
  "#6366F1", // indigo
  "#84CC16", // lime
  "#E11D48", // rose
];

function getColumnIndex(columns: string[], name: string | null): number {
  if (name === null) return -1;
  const idx = columns.indexOf(name);
  return idx >= 0 ? idx : 0;
}

function extractLabels(
  rows: (string | number | boolean | null)[][],
  colIndex: number
): string[] {
  return rows.map((row) => String(row[colIndex] ?? ""));
}

function extractValues(
  rows: (string | number | boolean | null)[][],
  colIndex: number
): number[] {
  return rows.map((row) => {
    const val = row[colIndex];
    if (typeof val === "number") return val;
    if (typeof val === "string") {
      const num = parseFloat(val);
      return isNaN(num) ? 0 : num;
    }
    return 0;
  });
}

export function buildBarChartConfig(
  columns: string[],
  rows: (string | number | boolean | null)[][],
  viz: VisualizationConfig
): { data: ChartData<"bar">; options: ChartOptions<"bar"> } {
  const xIdx = getColumnIndex(columns, viz.x_column);
  const yIdx = getColumnIndex(columns, viz.y_column);
  const labels = extractLabels(rows, xIdx >= 0 ? xIdx : 0);
  const values = extractValues(rows, yIdx >= 0 ? yIdx : Math.min(1, columns.length - 1));

  return {
    data: {
      labels,
      datasets: [
        {
          label: columns[yIdx >= 0 ? yIdx : Math.min(1, columns.length - 1)] ?? "Value",
          data: values,
          backgroundColor: PALETTE.slice(0, values.length).concat(
            Array(Math.max(0, values.length - PALETTE.length)).fill(PALETTE[0])
          ),
          borderColor: "transparent",
          borderRadius: 4,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        title: {
          display: !!viz.title,
          text: viz.title ?? "",
          color: "#E2E8F0",
          font: { size: 16, weight: "bold" },
        },
        legend: { display: false },
      },
      scales: {
        x: {
          ticks: { color: "#94A3B8", maxRotation: 45 },
          grid: { color: "#2A2D3A" },
        },
        y: {
          ticks: { color: "#94A3B8" },
          grid: { color: "#2A2D3A" },
        },
      },
    },
  };
}

export function buildLineChartConfig(
  columns: string[],
  rows: (string | number | boolean | null)[][],
  viz: VisualizationConfig
): { data: ChartData<"line">; options: ChartOptions<"line"> } {
  const xIdx = getColumnIndex(columns, viz.x_column);
  const yIdx = getColumnIndex(columns, viz.y_column);
  const labels = extractLabels(rows, xIdx >= 0 ? xIdx : 0);
  const values = extractValues(rows, yIdx >= 0 ? yIdx : Math.min(1, columns.length - 1));

  return {
    data: {
      labels,
      datasets: [
        {
          label: columns[yIdx >= 0 ? yIdx : Math.min(1, columns.length - 1)] ?? "Value",
          data: values,
          borderColor: PALETTE[0],
          backgroundColor: `${PALETTE[0]}33`,
          fill: true,
          tension: 0.3,
          pointBackgroundColor: PALETTE[0],
          pointBorderColor: "#1A1D27",
          pointBorderWidth: 2,
          pointRadius: 4,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        title: {
          display: !!viz.title,
          text: viz.title ?? "",
          color: "#E2E8F0",
          font: { size: 16, weight: "bold" },
        },
        legend: { display: false },
      },
      scales: {
        x: {
          ticks: { color: "#94A3B8", maxRotation: 45 },
          grid: { color: "#2A2D3A" },
        },
        y: {
          ticks: { color: "#94A3B8" },
          grid: { color: "#2A2D3A" },
        },
      },
    },
  };
}

export function buildPieChartConfig(
  columns: string[],
  rows: (string | number | boolean | null)[][],
  viz: VisualizationConfig
): { data: ChartData<"pie">; options: ChartOptions<"pie"> } {
  const xIdx = getColumnIndex(columns, viz.x_column);
  const yIdx = getColumnIndex(columns, viz.y_column);
  const labels = extractLabels(rows, xIdx >= 0 ? xIdx : 0);
  const values = extractValues(rows, yIdx >= 0 ? yIdx : Math.min(1, columns.length - 1));

  return {
    data: {
      labels,
      datasets: [
        {
          data: values,
          backgroundColor: PALETTE.slice(0, values.length).concat(
            Array(Math.max(0, values.length - PALETTE.length)).fill(PALETTE[0])
          ),
          borderColor: "#1A1D27",
          borderWidth: 2,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        title: {
          display: !!viz.title,
          text: viz.title ?? "",
          color: "#E2E8F0",
          font: { size: 16, weight: "bold" },
        },
        legend: {
          position: "right",
          labels: { color: "#E2E8F0", padding: 12, usePointStyle: true },
        },
      },
    },
  };
}
