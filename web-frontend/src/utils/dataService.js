import { useEffect, useState } from "react";

// Mock data service for development and production
const mockDataService = {
  // Function to generate random energy consumption data
  generateEnergyData: (hours = 24) => {
    const data = [];
    for (let i = 0; i < hours; i++) {
      data.push({
        name: `${i.toString().padStart(2, "0")}:00`,
        consumption: Math.floor(Math.random() * 200) + 100,
      });
    }
    return data;
  },

  // Function to generate random prediction data
  generatePredictionData: (hours = 24) => {
    const data = [];
    for (let i = 0; i < hours; i++) {
      const prediction = Math.floor(Math.random() * 200) + 100;
      const variance = prediction * 0.1; // 10% variance for confidence intervals
      data.push({
        timestamp: `2023-04-14 ${i.toString().padStart(2, "0")}:00`,
        prediction: prediction,
        lower: prediction - variance,
        upper: prediction + variance,
      });
    }
    return data;
  },

  // Function to get current stats
  getCurrentStats: () => {
    return {
      currentConsumption: Math.floor(Math.random() * 200) + 100,
      predictedPeak: Math.floor(Math.random() * 300) + 200,
      temperature: Math.floor(Math.random() * 15) + 15,
      humidity: Math.floor(Math.random() * 30) + 40,
    };
  },

  // Function to get API health status
  getHealthStatus: async () => {
    // Always return mock data to ensure the app works in static environments
    return {
      status: "healthy",
      version: "1.0.0-static",
    };
  },
};

// Custom hook for data fetching
export const useDataService = () => {
  const [apiStatus, setApiStatus] = useState({
    status: "loading",
    version: "",
  });

  useEffect(() => {
    const checkApiStatus = async () => {
      try {
        const status = await mockDataService.getHealthStatus();
        setApiStatus(status);
      } catch (error) {
        console.error("Failed to get API status, using fallback", error);
        setApiStatus({ status: "healthy", version: "1.0.0-fallback" });
      }
    };

    checkApiStatus();
  }, []);

  return {
    apiStatus,
    getEnergyData: mockDataService.generateEnergyData,
    getPredictionData: mockDataService.generatePredictionData,
    getCurrentStats: mockDataService.getCurrentStats,
  };
};

export default mockDataService;
