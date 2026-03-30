import axios from "axios";
import { API_CONFIG } from "../constants/config";

// Create axios instance with configuration
const apiClient = axios.create({
  baseURL: API_CONFIG.BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: API_CONFIG.TIMEOUT,
});

// Request interceptor for adding auth token
apiClient.interceptors.request.use(
  (config) => {
    // In a real app, get token from AsyncStorage or auth context
    // const token = await AsyncStorage.getItem('token');
    // if (token) {
    //   config.headers.Authorization = `Bearer ${token}`;
    // }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  },
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error("API call error:", error.response || error.message || error);

    // Handle specific error codes
    if (error.response) {
      switch (error.response.status) {
        case 401:
          // Handle unauthorized - maybe navigate to login
          console.warn("Unauthorized - Please login again");
          break;
        case 404:
          console.warn("Resource not found");
          break;
        case 500:
          console.error("Server error");
          break;
      }
    }

    return Promise.reject(error);
  },
);

/**
 * Health check endpoint
 * @returns {Promise<{status: string}>}
 */
export const getHealth = async () => {
  try {
    const response = await apiClient.get("/health");
    return response.data;
  } catch (error) {
    console.error("Error fetching health status:", error);
    throw new Error("Failed to fetch health status from backend.");
  }
};

/**
 * Get predictions from the backend
 * @param {Object} payload - Prediction request payload
 * @returns {Promise<{predictions: number[], confidence_intervals: Array<[number, number]>, model_version: string}>}
 */
export const postPredictions = async (payload) => {
  try {
    const response = await apiClient.post("/predict", payload);
    return response.data;
  } catch (error) {
    console.error("Error posting predictions:", error);

    if (error.response?.data?.detail) {
      throw new Error(
        `Prediction failed: ${JSON.stringify(error.response.data.detail)}`,
      );
    }
    throw new Error("Failed to get predictions from backend.");
  }
};

/**
 * Get summary statistics
 * @returns {Promise<{totalPredictions: number, averageAccuracy: number, lastPredictionTime: string}>}
 */
export const getSummary = async () => {
  try {
    const response = await apiClient.get("/summary");
    return response.data;
  } catch (error) {
    console.error("Error fetching summary data:", error);

    // Return mock data when endpoint is not available
    console.warn(
      "Using fallback summary data - /summary endpoint not available",
    );
    return {
      totalPredictions: 125,
      averageAccuracy: 0.92,
      lastPredictionTime: new Date().toLocaleTimeString(),
    };
  }
};

/**
 * Get historical energy data
 * @param {Object} params - Query parameters (e.g., { start_date, end_date, meter_id })
 * @returns {Promise<{lineData: Object, barData: Object}>}
 */
export const getHistoricalData = async (params) => {
  try {
    const response = await apiClient.get("/historical_data", { params });
    return response.data;
  } catch (error) {
    console.error("Error fetching historical data:", error);

    // Return mock data when endpoint is not available
    console.warn(
      "Using fallback historical data - /historical_data endpoint not available",
    );

    return {
      lineData: {
        labels: ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
        datasets: [{ data: [25, 40, 30, 55, 45, 60] }],
      },
      barData: {
        labels: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
        datasets: [{ data: [30, 50, 35, 70, 90, 50, 60] }],
      },
    };
  }
};

/**
 * Get model performance metrics
 * @returns {Promise<{mae: number, rmse: number, r2_score: number}>}
 */
export const getModelMetrics = async () => {
  try {
    const response = await apiClient.get("/metrics");
    return response.data;
  } catch (error) {
    console.error("Error fetching model metrics:", error);

    // Return mock data when endpoint is not available
    console.warn(
      "Using fallback metrics data - /metrics endpoint not available",
    );

    return {
      mae: 0.15,
      rmse: 0.22,
      r2_score: 0.89,
    };
  }
};

/**
 * Get user profile
 * @param {string} userId - User ID
 * @returns {Promise<Object>}
 */
export const getUserProfile = async (userId) => {
  try {
    const response = await apiClient.get(`/users/${userId}`);
    return response.data;
  } catch (error) {
    console.error("Error fetching user profile:", error);
    throw new Error("Failed to fetch user profile.");
  }
};

/**
 * Update user profile
 * @param {string} userId - User ID
 * @param {Object} data - Profile data to update
 * @returns {Promise<Object>}
 */
export const updateUserProfile = async (userId, data) => {
  try {
    const response = await apiClient.put(`/users/${userId}`, data);
    return response.data;
  } catch (error) {
    console.error("Error updating user profile:", error);
    throw new Error("Failed to update user profile.");
  }
};

/**
 * Get notifications
 * @returns {Promise<Array>}
 */
export const getNotifications = async () => {
  try {
    const response = await apiClient.get("/notifications");
    return response.data;
  } catch (error) {
    console.error("Error fetching notifications:", error);
    return []; // Return empty array on error
  }
};

export default apiClient;
