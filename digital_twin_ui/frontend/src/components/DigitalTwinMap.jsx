import React from "react";

const severityColors = {
  HIGH: "bg-red-500 animate-pulse",
  MEDIUM: "bg-yellow-400 animate-pulse",
  LOW: "bg-green-500 animate-pulse"
};

const DigitalTwinMap = ({ hotspots }) => {
  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-3xl p-6 shadow-xl h-full">

      {/* Header */}
      <div className="flex items-center justify-between mb-5">
        <div>
          <h2 className="text-white text-xl font-bold">
            Behavioral Digital Twin
          </h2>

          <p className="text-zinc-400 text-sm mt-1">
            Live City Simulation Environment
          </p>
        </div>

        <div className="bg-cyan-500/10 px-4 py-2 rounded-xl">
          <span className="text-cyan-400 font-semibold">
            BDT Active
          </span>
        </div>
      </div>

      {/* Map Container */}
      <div className="relative overflow-hidden rounded-3xl border border-zinc-700">

        <img
          src="/city_map.png"
          alt="City Map"
          className="w-full h-[450px] object-cover"
        />

        {/* Hotspots */}
        {hotspots.map((spot, index) => (
          <div
            key={index}
            className="absolute"
            style={{
              top: spot.top,
              left: spot.left
            }}
          >
            {/* Marker */}
            <div
              className={`w-5 h-5 rounded-full ${severityColors[spot.severity]}`}
            />

            {/* Label */}
            <div className="absolute top-7 left-0 bg-zinc-950/90 px-3 py-2 rounded-xl border border-zinc-700 whitespace-nowrap">
              <p className="text-white text-sm font-semibold">
                {spot.name}
              </p>

              <p
                className={`text-xs mt-1 ${
                  spot.severity === "HIGH"
                    ? "text-red-400"
                    : spot.severity === "MEDIUM"
                    ? "text-yellow-400"
                    : "text-green-400"
                }`}
              >
                {spot.severity} RISK
              </p>
            </div>
          </div>
        ))}
      </div>

      {/* Summary */}
      <div className="grid grid-cols-3 gap-4 mt-6">

        <div className="bg-zinc-800 rounded-2xl p-4">
          <p className="text-zinc-400 text-sm">
            Hotspots
          </p>

          <h3 className="text-white text-2xl font-bold mt-2">
            {hotspots.length}
          </h3>
        </div>

        <div className="bg-zinc-800 rounded-2xl p-4">
          <p className="text-zinc-400 text-sm">
            Highest Risk
          </p>

          <h3 className="text-red-400 text-2xl font-bold mt-2">
            HIGH
          </h3>
        </div>

        <div className="bg-zinc-800 rounded-2xl p-4">
          <p className="text-zinc-400 text-sm">
            Status
          </p>

          <h3 className="text-cyan-400 text-2xl font-bold mt-2">
            Simulating
          </h3>
        </div>

      </div>

    </div>
  );
};

export default DigitalTwinMap;