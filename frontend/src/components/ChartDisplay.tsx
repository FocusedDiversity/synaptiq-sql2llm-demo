import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from "chart.js";
import { Bar, Line, Pie } from "react-chartjs-2";
import type { VisualizationConfig } from "../types";
import {
  buildBarChartConfig,
  buildLineChartConfig,
  buildPieChartConfig,
} from "../utils/chartConfig";

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

interface ChartDisplayProps {
  columns: string[];
  rows: (string | number | boolean | null)[][];
  visualization: VisualizationConfig;
}

export default function ChartDisplay({ columns, rows, visualization }: ChartDisplayProps) {
  if (visualization.type === "bar") {
    const { data, options } = buildBarChartConfig(columns, rows, visualization);
    return (
      <div className="h-80">
        <Bar data={data} options={options} />
      </div>
    );
  }

  if (visualization.type === "line") {
    const { data, options } = buildLineChartConfig(columns, rows, visualization);
    return (
      <div className="h-80">
        <Line data={data} options={options} />
      </div>
    );
  }

  if (visualization.type === "pie") {
    const { data, options } = buildPieChartConfig(columns, rows, visualization);
    return (
      <div className="h-80">
        <Pie data={data} options={options} />
      </div>
    );
  }

  return null;
}
