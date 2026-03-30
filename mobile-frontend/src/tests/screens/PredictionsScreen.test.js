import { fireEvent, render, waitFor } from "@testing-library/react-native";
import { Provider as PaperProvider } from "react-native-paper";
import * as api from "../../api/api";
import PredictionsScreen from "../../screens/PredictionsScreen";

jest.mock("../../api/api");

const mockNavigation = {
  navigate: jest.fn(),
  goBack: jest.fn(),
};

const mockPredictionResponse = {
  predictions: [0.8234, 0.7891],
  confidence_intervals: [
    [0.7234, 0.9234],
    [0.6891, 0.8891],
  ],
  model_version: "0.1.0",
};

describe("PredictionsScreen", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  const renderComponent = () => {
    return render(
      <PaperProvider>
        <PredictionsScreen navigation={mockNavigation} />
      </PaperProvider>,
    );
  };

  it("renders correctly", () => {
    const { getByText } = renderComponent();
    expect(getByText("Energy Predictions")).toBeTruthy();
    expect(getByText("Input Parameters")).toBeTruthy();
  });

  it("validates required fields", async () => {
    const { getByText } = renderComponent();

    const predictButton = getByText("Get Predictions");
    fireEvent.press(predictButton);

    await waitFor(() => {
      expect(getByText(/required/i)).toBeTruthy();
    });
  });

  it("validates JSON context format", async () => {
    const { getByLabelText, getByText } = renderComponent();

    const contextInput = getByLabelText("Context Features (JSON)");
    fireEvent.changeText(contextInput, "invalid json");

    await waitFor(() => {
      expect(getByText("Invalid JSON format")).toBeTruthy();
    });
  });

  it("submits prediction request successfully", async () => {
    api.postPredictions.mockResolvedValue(mockPredictionResponse);

    const { getByLabelText, getByText } = renderComponent();

    const timestampInput = getByLabelText("Timestamp (ISO Format)");
    const meterIdInput = getByLabelText("Meter ID");
    const contextInput = getByLabelText("Context Features (JSON)");

    fireEvent.changeText(timestampInput, "2024-01-01T12:00:00");
    fireEvent.changeText(meterIdInput, "meter_123");
    fireEvent.changeText(contextInput, '{"temperature": 25}');

    const predictButton = getByText("Get Predictions");
    fireEvent.press(predictButton);

    await waitFor(() => {
      expect(getByText("Prediction Results")).toBeTruthy();
    });
  });

  it("displays prediction results with confidence intervals", async () => {
    api.postPredictions.mockResolvedValue(mockPredictionResponse);

    const { getByLabelText, getByText } = renderComponent();

    fireEvent.changeText(
      getByLabelText("Timestamp (ISO Format)"),
      "2024-01-01T12:00:00",
    );
    fireEvent.changeText(getByLabelText("Meter ID"), "meter_123");
    fireEvent.changeText(getByLabelText("Context Features (JSON)"), "{}");

    fireEvent.press(getByText("Get Predictions"));

    await waitFor(() => {
      expect(getByText(/0.8234/)).toBeTruthy();
      expect(getByText(/95% CI:/)).toBeTruthy();
    });
  });

  it("handles prediction API error", async () => {
    api.postPredictions.mockRejectedValue(new Error("API Error"));

    const { getByLabelText, getByText } = renderComponent();

    fireEvent.changeText(
      getByLabelText("Timestamp (ISO Format)"),
      "2024-01-01T12:00:00",
    );
    fireEvent.changeText(getByLabelText("Meter ID"), "meter_123");
    fireEvent.changeText(getByLabelText("Context Features (JSON)"), "{}");

    fireEvent.press(getByText("Get Predictions"));

    await waitFor(() => {
      expect(getByText(/Prediction failed/)).toBeTruthy();
    });
  });
});
