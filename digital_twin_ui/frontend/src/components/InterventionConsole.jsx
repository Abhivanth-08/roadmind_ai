import React, { useState } from "react";
import axios from "axios";

const interventions = [
  "Add 20 Parking Spaces",
  "Deploy Traffic Police",
  "Signal Retiming",
  "Dynamic Signboards"
];

const InterventionConsole = ({ setForecastData }) => {
  const [selectedAction, setSelectedAction] = useState(interventions[0]);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const runSimulation = async () => {
    try {
      setLoading(true);

      const response = await axios.post(
        "http://127.0.0.1:8000/simulate",
        {
          intervention: selectedAction
        }
      );

      setForecastData(response.data.forecast);
      setResult(response.data);

      setTimeout(() => {
        setLoading(false);
      }, 1500);

    } catch (error) {
      console.log(error);
      setLoading(false);
    }
  };

  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-3xl p-6 shadow-xl">

      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-xl font-bold text-white">
            Traffic Intervention Engine
          </h2>

          <p className="text-zinc-400 text-sm mt-1">
            Test solutions inside the Digital Twin
          </p>
        </div>

        <div className="bg-green-500/10 px-4 py-2 rounded-xl">
          <span className="text-green-400 font-semibold">
            TIE Active
          </span>
        </div>
      </div>

      {/* Dropdown */}
      <div className="mb-5">

        <label className="block text-zinc-300 mb-2">
          Test Intervention
        </label>

        <select
          value={selectedAction}
          onChange={(e) => setSelectedAction(e.target.value)}
          className="w-full bg-zinc-800 text-white border border-zinc-700 rounded-xl px-4 py-3 outline-none"
        >
          {interventions.map((item) => (
            <option key={item}>
              {item}
            </option>
          ))}
        </select>

      </div>

      {/* Button */}
      <button
        onClick={runSimulation}
        disabled={loading}
        className="w-full bg-blue-600 hover:bg-blue-700 transition rounded-2xl py-4 font-semibold text-white"
      >
        {loading ? "Running Digital Twin..." : "Run Simulation"}
      </button>

      {/* Loader */}
      {loading && (
        <div className="mt-6 text-center">
          <div className="animate-pulse text-cyan-400 font-medium">
            Simulating Traffic Environment...
          </div>
        </div>
      )}

      {/* Results */}
      {result && !loading && (
        <div className="mt-8 grid grid-cols-3 gap-4">

          <div className="bg-zinc-800 rounded-2xl p-4">
            <p className="text-zinc-400 text-sm">
              Reduction
            </p>

            <h3 className="text-green-400 text-2xl font-bold mt-2">
              {result.reduction_percentage}%
            </h3>
          </div>

          <div className="bg-zinc-800 rounded-2xl p-4">
            <p className="text-zinc-400 text-sm">
              Risk Level
            </p>

            <h3 className="text-yellow-400 text-2xl font-bold mt-2">
              {result.risk}
            </h3>
          </div>

          <div className="bg-zinc-800 rounded-2xl p-4">
            <p className="text-zinc-400 text-sm">
              Predicted Violations
            </p>

            <h3 className="text-red-400 text-2xl font-bold mt-2">
              {result.predicted_violations}
            </h3>
          </div>

        </div>
      )}

    </div>
  );
};

export default InterventionConsole;