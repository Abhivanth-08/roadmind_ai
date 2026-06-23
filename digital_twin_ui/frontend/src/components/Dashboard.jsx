import React, { useState } from "react";
import ForecastChart from "./ForecastChart";
import DigitalTwinMap from "./DigitalTwinMap";
import InterventionConsole from "./InterventionConsole";
import urbanMemory from "../data/urban_memory_logs.json";

const Dashboard = () => {
  const [forecastData, setForecastData] = useState(urbanMemory.forecast);

  return (
    <div className="min-h-screen bg-[#09090B] text-white px-8 py-6">

      {/* Header */}
      <div className="mb-10">
        <h1 className="text-5xl font-bold bg-gradient-to-r from-cyan-400 via-purple-400 to-pink-500 bg-clip-text text-transparent">
          RoadMind-X
        </h1>

        <p className="text-zinc-400 mt-2 text-lg">
          Cognitive Intelligence Command Center
        </p>
      </div>

      {/* Top Metrics */}
      <div className="grid md:grid-cols-3 gap-6 mb-8">

        <div className="bg-zinc-900 rounded-3xl p-6 border border-zinc-800">
          <p className="text-zinc-400">Spread Risk</p>

          <h1 className="text-red-400 text-4xl font-bold mt-3">
            {urbanMemory.spread_risk.level}
          </h1>

          <p className="text-zinc-500 mt-2">
            Affecting {urbanMemory.spread_risk.count} roads
          </p>
        </div>

        <div className="bg-zinc-900 rounded-3xl p-6 border border-zinc-800">
          <p className="text-zinc-400">Active Violations</p>

          <h1 className="text-cyan-400 text-4xl font-bold mt-3">
            {urbanMemory.current_violations}
          </h1>
        </div>

        <div className="bg-zinc-900 rounded-3xl p-6 border border-zinc-800">
          <p className="text-zinc-400">Forecast Peak</p>

          <h1 className="text-yellow-400 text-4xl font-bold mt-3">
            {forecastData[forecastData.length - 1].violations}
          </h1>
        </div>

      </div>

      {/* VFE + BDT */}
      <div className="grid xl:grid-cols-2 gap-8 mb-8">

        <ForecastChart forecastData={forecastData} />

        <DigitalTwinMap hotspots={urbanMemory.hotspots} />

      </div>

      {/* VCE */}
      <div className="bg-zinc-900 rounded-3xl p-8 border border-zinc-800 mb-8">

        <h2 className="text-2xl font-bold mb-6">
          Violation Contagion Engine
        </h2>

        <div className="flex justify-center items-center gap-4 text-xl flex-wrap">

          <div className="bg-purple-500/20 px-5 py-3 rounded-xl">
            Festival
          </div>

          ↓

          <div className="bg-red-500/20 px-5 py-3 rounded-xl">
            Parking Overflow
          </div>

          ↓

          <div className="bg-orange-500/20 px-5 py-3 rounded-xl">
            5th Avenue
          </div>

          ↓

          <div className="bg-yellow-500/20 px-5 py-3 rounded-xl">
            School Road
          </div>

          ↓

          <div className="bg-green-500/20 px-5 py-3 rounded-xl">
            Hospital Lane
          </div>

        </div>

      </div>

      {/* TIE */}
      <InterventionConsole setForecastData={setForecastData} />

      {/* AI Recommendation */}
      <div className="bg-zinc-900 rounded-3xl border border-zinc-800 mt-8 p-8">

        <h2 className="text-2xl font-bold mb-5 text-cyan-400">
          Strategist AI
        </h2>

        <div className="space-y-4 text-zinc-300">

          <div>
            ✓ Increase parking spaces near festival area.
          </div>

          <div>
            ✓ Deploy traffic officers from 6 PM - 8 PM.
          </div>

          <div>
            ✓ Enable dynamic signboards.
          </div>

          <div className="text-green-400 font-bold mt-4">
            Confidence : 92%
          </div>

        </div>

      </div>

    </div>
  );
};

export default Dashboard;