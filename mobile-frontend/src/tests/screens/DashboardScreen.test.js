import { fireEvent, render, waitFor } from "@testing-library/react-native";
import { Provider as PaperProvider } from "react-native-paper";
import * as api from "../../api/api";
import DashboardScreen from "../../screens/DashboardScreen";

// Mock the API module
jest.mock("../../api/api");

const mockNavigation = {
  navigate: jest.fn(),
  openDrawer: jest.fn(),
};

const mockHealthData = {
  status: "healthy",
};

const mockSummaryData = {
  totalPredictions: 125,
  averageAccuracy: 0.92,
  lastPredictionTime: "10:30:45 AM",
};

describe("DashboardScreen", () => {
  beforeEach(() => {
    jest.clearAllMocks();
    api.getHealth.mockResolvedValue(mockHealthData);
    api.getSummary.mockResolvedValue(mockSummaryData);
  });

  const renderComponent = () => {
    return render(
      <PaperProvider>
        <DashboardScreen navigation={mockNavigation} />
      </PaperProvider>,
    );
  };

  it("renders correctly", async () => {
    const { getByText } = renderComponent();

    await waitFor(() => {
      expect(getByText("Fluxora Dashboard")).toBeTruthy();
    });
  });

  it("displays health status after loading", async () => {
    const { getByText } = renderComponent();

    await waitFor(() => {
      expect(getByText("HEALTHY")).toBeTruthy();
    });
  });

  it("displays summary data", async () => {
    const { getByText } = renderComponent();

    await waitFor(() => {
      expect(getByText(/Total Predictions Made:/)).toBeTruthy();
      expect(getByText(/125/)).toBeTruthy();
    });
  });

  it("handles navigation to Predictions screen", async () => {
    const { getByText } = renderComponent();

    await waitFor(() => {
      expect(getByText("Predictions")).toBeTruthy();
    });

    fireEvent.press(getByText("Predictions"));
    expect(mockNavigation.navigate).toHaveBeenCalledWith("Predictions");
  });

  it("handles navigation to Analytics screen", async () => {
    const { getByText } = renderComponent();

    await waitFor(() => {
      expect(getByText("Analytics")).toBeTruthy();
    });

    fireEvent.press(getByText("Analytics"));
    expect(mockNavigation.navigate).toHaveBeenCalledWith("Analytics");
  });

  it("shows error dialog when API fails", async () => {
    api.getHealth.mockRejectedValue(new Error("API Error"));

    const { getByText } = renderComponent();

    await waitFor(() => {
      expect(getByText(/Failed to connect to the backend/)).toBeTruthy();
    });
  });

  it("handles failed summary fetch gracefully", async () => {
    api.getSummary.mockResolvedValue(null);

    const { getByText } = renderComponent();

    await waitFor(() => {
      expect(getByText(/Summary data unavailable/)).toBeTruthy();
    });
  });
});
