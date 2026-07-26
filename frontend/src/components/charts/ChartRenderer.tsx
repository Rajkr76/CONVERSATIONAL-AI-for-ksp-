"use client";

import { motion } from "framer-motion";
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Cell,
} from "recharts";
import { ChartData } from "@/types";
import { BarChart3 } from "lucide-react";

interface ChartRendererProps {
  chart: ChartData;
}

const PIE_COLORS = [
  "#6366f1", "#f43f5e", "#22c55e", "#fb923c", "#a855f7",
  "#06b6d4", "#ec4899", "#eab308", "#3b82f6", "#10b981"
];

export function ChartRenderer({ chart }: ChartRendererProps) {
  if (!chart || !chart.labels || chart.labels.length === 0) return null;

  // Format data for Recharts
  const formattedData = chart.labels.map((label, idx) => {
    const row: Record<string, any> = { label };
    chart.datasets.forEach((ds) => {
      row[ds.label] = ds.data[idx] ?? 0;
    });
    return row;
  });

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.98 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.3 }}
      className="my-4 p-4 rounded-xl border border-indigo-500/20 bg-slate-900/80 backdrop-blur-md shadow-xl"
    >
      <div className="flex items-center gap-2 mb-4">
        <BarChart3 className="w-4 h-4 text-indigo-400" />
        <h4 className="text-sm font-semibold text-slate-200">{chart.title}</h4>
      </div>

      <div className="w-full h-64">
        <ResponsiveContainer width="100%" height="100%">
          {chart.chart_type === "line" ? (
            <LineChart data={formattedData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis dataKey="label" stroke="#94a3b8" tick={{ fontSize: 11 }} />
              <YAxis stroke="#94a3b8" tick={{ fontSize: 11 }} />
              <Tooltip contentStyle={{ backgroundColor: "#0f172a", borderColor: "#334155", color: "#f8fafc" }} />
              <Legend wrapperStyle={{ fontSize: 12, paddingTop: 10 }} />
              {chart.datasets.map((ds, idx) => (
                <Line
                  key={ds.label}
                  type="monotone"
                  dataKey={ds.label}
                  stroke={ds.borderColor || PIE_COLORS[idx % PIE_COLORS.length]}
                  strokeWidth={2.5}
                  dot={{ r: 4 }}
                />
              ))}
            </LineChart>
          ) : chart.chart_type === "area" ? (
            <AreaChart data={formattedData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis dataKey="label" stroke="#94a3b8" tick={{ fontSize: 11 }} />
              <YAxis stroke="#94a3b8" tick={{ fontSize: 11 }} />
              <Tooltip contentStyle={{ backgroundColor: "#0f172a", borderColor: "#334155", color: "#f8fafc" }} />
              <Legend wrapperStyle={{ fontSize: 12, paddingTop: 10 }} />
              {chart.datasets.map((ds, idx) => (
                <Area
                  key={ds.label}
                  type="monotone"
                  dataKey={ds.label}
                  stroke={ds.borderColor || PIE_COLORS[idx % PIE_COLORS.length]}
                  fill={ds.backgroundColor || PIE_COLORS[idx % PIE_COLORS.length]}
                  fillOpacity={0.4}
                />
              ))}
            </AreaChart>
          ) : chart.chart_type === "pie" ? (
            <PieChart>
              <Tooltip contentStyle={{ backgroundColor: "#0f172a", borderColor: "#334155", color: "#f8fafc" }} />
              <Legend wrapperStyle={{ fontSize: 12, paddingTop: 10 }} />
              <Pie
                data={formattedData}
                dataKey={chart.datasets[0]?.label || "data"}
                nameKey="label"
                cx="50%"
                cy="50%"
                outerRadius={80}
                label
              >
                {formattedData.map((_, index) => (
                  <Cell key={`cell-${index}`} fill={PIE_COLORS[index % PIE_COLORS.length]} />
                ))}
              </Pie>
            </PieChart>
          ) : (
            <BarChart data={formattedData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis dataKey="label" stroke="#94a3b8" tick={{ fontSize: 11 }} />
              <YAxis stroke="#94a3b8" tick={{ fontSize: 11 }} />
              <Tooltip contentStyle={{ backgroundColor: "#0f172a", borderColor: "#334155", color: "#f8fafc" }} />
              <Legend wrapperStyle={{ fontSize: 12, paddingTop: 10 }} />
              {chart.datasets.map((ds, idx) => (
                <Bar
                  key={ds.label}
                  dataKey={ds.label}
                  fill={ds.backgroundColor || PIE_COLORS[idx % PIE_COLORS.length]}
                  radius={[4, 4, 0, 0]}
                />
              ))}
            </BarChart>
          )}
        </ResponsiveContainer>
      </div>
    </motion.div>
  );
}
