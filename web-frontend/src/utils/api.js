import axios from "axios";
import mockDataService from "./dataService";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
const API_TIMEOUT = import.meta.env.VITE_API_TIMEOUT || 30000;
const USE_MOCK_DATA = import.meta.env.VITE_ENABLE_MOCK_DATA !== "false";

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: API_TIMEOUT,
  headers: {
    "Content-Type": "application/json",
  },
});

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error("API Error:", error);
    if (USE_MOCK_DATA) {
      console.log("Falling back to mock data");
      return Promise.resolve({ data: null, usedMockData: true });
    }
    return Promise.reject(error);
  },
);

const api = {
  getHealthStatus: async () => {
    if (USE_MOCK_DATA) {
      return mockDataService.getHealthStatus();
    }
    try {
      const response = await apiClient.get("/health");
      return response.data;
    } catch (_error) {
      console.error("Health check failed, using mock data");
      return mockDataService.getHealthStatus();
    }
  },

  getPredictions: async (params = {}) => {
    if (USE_MOCK_DATA) {
      return mockDataService.generatePredictionData(24);
    }
    try {
      const response = await apiClient.post("/api/v1/predict", params);
      return response.data;
    } catch (_error) {
      console.error("Predictions API failed, using mock data");
      return mockDataService.generatePredictionData(24);
    }
  },

  getHistoricalData: async (startDate, endDate, meterId) => {
    if (USE_MOCK_DATA) {
      return mockDataService.generateEnergyData(24);
    }
    try {
      const response = await apiClient.get("/api/v1/data/consumption", {
        params: { start_date: startDate, end_date: endDate, meter_id: meterId },
      });
      return response.data;
    } catch (_error) {
      console.error("Historical data API failed, using mock data");
      return mockDataService.generateEnergyData(24);
    }
  },

  getAnalytics: async (params = {}) => {
    if (USE_MOCK_DATA) {
      return {
        monthly: mockDataService.generateEnergyData(12),
        hourly: mockDataService.generateEnergyData(24),
      };
    }
    try {
      const response = await apiClient.get("/api/v1/analytics", { params });
      return response.data;
    } catch (_error) {
      console.error("Analytics API failed, using mock data");
      return {
        monthly: mockDataService.generateEnergyData(12),
        hourly: mockDataService.generateEnergyData(24),
      };
    }
  },
};

export const getHealthStatus = api.getHealthStatus;
export const getPredictions = api.getPredictions;
export const getHistoricalData = api.getHistoricalData;
export const getAnalytics = api.getAnalytics;

export default api;
