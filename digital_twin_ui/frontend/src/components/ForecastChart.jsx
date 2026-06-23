import React from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
  Area,
  AreaChart
} from "recharts";

const ForecastChart = ({ forecastData }) => {
  return (
    <div className="bg-zinc-900 rounded-3xl border border-zinc-800 shadow-xl p-6 h-full">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-xl font-bold text-white">
            Violation Forecast Engine
          </h2>
          <p className="text-zinc-400 text-sm mt-1">
            Predicted Violations - Next 72 Hours
          </p>
        </div>

        <div className="bg-red-500/10 px-4 py-2 rounded-xl">
          <span className="text-red-400 font-semibold">
            VFE Active
          </span>
        </div>
      </div>

      <ResponsiveContainer width="100%" height={350}>
        <AreaChart data={forecastData}>
          <defs>
            <linearGradient id="colorViolation" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#ef4444" stopOpacity={0.8} />
              <stop offset="95%" stopColor="#ef4444" stopOpacity={0.05} />
            </linearGradient>
          </defs>

          <CartesianGrid
            strokeDasharray="3 3"
            stroke="#27272a"
          />

          <XAxis
            dataKey="hour"
            tick={{ fill: "#a1a1aa" }}
            label={{
              value: "Hours",
              position: "insideBottom",
              fill: "#71717a"
            }}
          />

          <YAxis
            tick={{ fill: "#a1a1aa" }}
            label={{
              value: "Violations",
              angle: -90,
              position: "insideLeft",
              fill: "#71717a"
            }}
          />

          <Tooltip
            contentStyle={{
              backgroundColor: "#18181b",
              border: "1px solid #3f3f46",
              borderRadius: "12px",
              color: "white"
            }}
          />

          <Area
            type="monotone"
            dataKey="violations"
            stroke="#ef4444"
            fillOpacity={1}
            fill="url(#colorViolation)"
          />

          <Line
            type="monotone"
            dataKey="violations"
            stroke="#f87171"
            strokeWidth={4}
            dot={{
              r: 5,
              fill: "#f87171"
            }}
            activeDot={{
              r: 8
            }}
            animationDuration={1500}
          />
        </AreaChart>
      </ResponsiveContainer>

      <div className="grid grid-cols-3 gap-4 mt-8">

        <div className="bg-zinc-800 rounded-2xl p-4">
          <h3 className="text-zinc-400 text-sm">
            Current
          </h3>

          <p className="text-white text-2xl font-bold mt-2">
            {forecastData[0]?.violations}
          </p>
        </div>

        <div className="bg-zinc-800 rounded-2xl p-4">
          <h3 className="text-zinc-400 text-sm">
            Peak (72h)
          </h3>

          <p className="text-red-400 text-2xl font-bold mt-2">
            {forecastData[forecastData.length - 1]?.violations}
          </p>
        </div>

        <div className="bg-zinc-800 rounded-2xl p-4">
          <h3 className="text-zinc-400 text-sm">
            Trend
          </h3>

          <p className="text-yellow-400 text-2xl font-bold mt-2">
            Rising
          </p>
        </div>

      </div>
    </div>
  );
};

export default ForecastChart;