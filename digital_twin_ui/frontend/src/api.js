import axios from "axios";

const API_BASE_URL = "http://127.0.0.1:8000";

// Axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// ----------------------
// Health Check
// ----------------------
export const checkServer = async () => {
  try {
    const response = await api.get("/");
    return response.data;
  } catch (error) {
    console.error("Server connection failed:", error);
    throw error;
  }
};

// ----------------------
// Run Digital Twin Simulation
// ----------------------
export const runSimulation = async (intervention) => {
  try {
    const response = await api.post("/simulate", {
      intervention,
    });

    return response.data;

  } catch (error) {
    console.error("Simulation failed:", error);
    throw error;
  }
};

export default api;