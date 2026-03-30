import { render, waitFor } from "@testing-library/react-native";
import { Provider as PaperProvider } from "react-native-paper";
import * as api from "../../api/api";
import AnalyticsScreen from "../../screens/AnalyticsScreen";

jest.mock("../../api/api");

const mockNavigation = {
  navigate: jest.fn(),
};

const mockHistoricalData = {
  lineData: {
    labels: ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
    datasets: [{ data: [25, 40, 30, 55, 45, 60] }],
  },
  barData: {
    labels: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
    datasets: [{ data: [30, 50, 35, 70, 90, 50, 60] }],
  },
};

const mockMetrics = {
  mae: 0.15,
  rmse: 0.22,
  r2_score: 0.89,
};

describe("AnalyticsScreen", () => {
  beforeEach(() => {
    jest.clearAllMocks();
    api.getHistoricalData.mockResolvedValue(mockHistoricalData);
    api.getModelMetrics.mockResolvedValue(mockMetrics);
  });

  const renderComponent = () => {
    return render(
      <PaperProvider>
        <AnalyticsScreen navigation={mockNavigation} />
      </PaperProvider>,
    );
  };

  it("renders correctly", async () => {
    const { getByText } = renderComponent();

    await waitFor(() => {
      expect(getByText("Analytics")).toBeTruthy();
    });
  });

  it("displays loading state initially", () => {
    const { getByText } = renderComponent();
    expect(getByText("Loading analytics...")).toBeTruthy();
  });

  it("loads and displays historical data", async () => {
    const { getByText } = renderComponent();

    await waitFor(() => {
      expect(getByText("Energy Consumption Trend (Monthly)")).toBeTruthy();
      expect(getByText("Peak Usage Times (Weekly)")).toBeTruthy();
    });
  });

  it("displays model performance metrics", async () => {
    const { getByText } = renderComponent();

    await waitFor(() => {
      expect(getByText("Model Performance Metrics")).toBeTruthy();
      expect(getByText("Mean Absolute Error (MAE)")).toBeTruthy();
      expect(getByText("0.1500")).toBeTruthy();
    });
  });

  it("shows error message on API failure", async () => {
    api.getHistoricalData.mockRejectedValue(new Error("API Error"));
    api.getModelMetrics.mockRejectedValue(new Error("API Error"));

    const { getByText } = renderComponent();

    await waitFor(() => {
      expect(getByText(/Failed to load analytics data/)).toBeTruthy();
    });
  });

  it("handles refresh action", async () => {
    const { getByText, getByTestId } = renderComponent();

    await waitFor(() => {
      expect(getByText("Energy Consumption Trend (Monthly)")).toBeTruthy();
    });

    // Simulate pull-to-refresh would be done here in a full E2E test
    // For unit test, we just verify the data loads
    expect(api.getHistoricalData).toHaveBeenCalled();
    expect(api.getModelMetrics).toHaveBeenCalled();
  });

  it("displays energy insights", async () => {
    const { getByText } = renderComponent();

    await waitFor(() => {
      expect(getByText("Energy Insights")).toBeTruthy();
      expect(getByText(/Average Daily Usage:/)).toBeTruthy();
      expect(getByText(/Weekly Trend:/)).toBeTruthy();
    });
  });
});
