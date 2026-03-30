import AsyncStorage from "@react-native-async-storage/async-storage";
import { createContext, useContext, useEffect, useState } from "react";

const AuthContext = createContext(null);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [token, setToken] = useState(null);

  // Load user from storage on mount
  useEffect(() => {
    loadUser();
  }, [loadUser]);

  const loadUser = async () => {
    try {
      const storedUser = await AsyncStorage.getItem("user");
      const storedToken = await AsyncStorage.getItem("token");
      if (storedUser && storedToken) {
        setUser(JSON.parse(storedUser));
        setToken(storedToken);
      }
    } catch (error) {
      console.error("Failed to load user:", error);
    } finally {
      setLoading(false);
    }
  };

  const login = async (username, _password) => {
    try {
      // In a real app, this would call the backend API
      // For now, we'll simulate a successful login
      const mockUser = {
        id: "1",
        username: username,
        email: `${username}@example.com`,
      };
      const mockToken = `mock-jwt-token-${Date.now()}`;

      await AsyncStorage.setItem("user", JSON.stringify(mockUser));
      await AsyncStorage.setItem("token", mockToken);

      setUser(mockUser);
      setToken(mockToken);

      return { success: true };
    } catch (error) {
      console.error("Login failed:", error);
      return { success: false, error: error.message };
    }
  };

  const logout = async () => {
    try {
      await AsyncStorage.removeItem("user");
      await AsyncStorage.removeItem("token");
      setUser(null);
      setToken(null);
    } catch (error) {
      console.error("Logout failed:", error);
      throw error;
    }
  };

  const register = async (username, email, _password) => {
    try {
      // In a real app, this would call the backend API
      const mockUser = {
        id: Date.now().toString(),
        username,
        email,
      };
      const mockToken = `mock-jwt-token-${Date.now()}`;

      await AsyncStorage.setItem("user", JSON.stringify(mockUser));
      await AsyncStorage.setItem("token", mockToken);

      setUser(mockUser);
      setToken(mockToken);

      return { success: true };
    } catch (error) {
      console.error("Registration failed:", error);
      return { success: false, error: error.message };
    }
  };

  const value = {
    user,
    token,
    loading,
    login,
    logout,
    register,
    isAuthenticated: !!user,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export default AuthContext;
