import React from "react";
import { HashRouter, Navigate, Route, Routes } from "react-router-dom";
import Layout from "./components/Layout";
import Analytics from "./pages/Analytics";
import Dashboard from "./pages/Dashboard";
import Predictions from "./pages/Predictions";
import Settings from "./pages/Settings";

const App = () => {
  const [isLoading, setIsLoading] = React.useState(true);

  React.useEffect(() => {
    // Simulate initial loading
    const timer = setTimeout(() => {
      setIsLoading(false);
    }, 1000);

    return () => clearTimeout(timer);
  }, []);

  // Loading screen
  if (isLoading) {
    return (
      <div className="loading-screen">
        <div className="loading-content">
          <h1>Fluxora</h1>
          <p>Energy Prediction System</p>
          <div className="loading-spinner"></div>
        </div>
      </div>
    );
  }

  return (
    // Using HashRouter instead of BrowserRouter for better compatibility with static hosting
    <HashRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Dashboard />} />
          <Route path="predictions" element={<Predictions />} />
          <Route path="analytics" element={<Analytics />} />
          <Route path="settings" element={<Settings />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </HashRouter>
  );
};

export default App;
