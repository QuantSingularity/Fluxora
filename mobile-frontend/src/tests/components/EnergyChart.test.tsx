import { describe, expect, it } from "@jest/globals";
import { render } from "@testing-library/react-native";
import { Provider as PaperProvider } from "react-native-paper";
import { EnergyChart } from "../../components/EnergyChart";

const mockData = {
  consumption: [100, 120, 110, 130],
  production: [80, 90, 85, 95],
  timestamps: ["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04"],
};

describe("EnergyChart Component", () => {
  const renderComponent = (props = {}) => {
    return render(
      <PaperProvider>
        <EnergyChart data={mockData} {...props} />
      </PaperProvider>,
    );
  };

  it("renders chart correctly", () => {
    const { getByTestId, getByText } = renderComponent();

    expect(getByTestId("energy-chart")).toBeTruthy();
    expect(getByText("Energy Consumption")).toBeTruthy();
    expect(getByText("Energy Production")).toBeTruthy();
  });

  it("handles empty data", () => {
    const emptyData = {
      consumption: [],
      production: [],
      timestamps: [],
    };

    const { getByText } = render(
      <PaperProvider>
        <EnergyChart data={emptyData} />
      </PaperProvider>,
    );

    expect(getByText("No data available")).toBeTruthy();
  });

  it("handles data updates", () => {
    const { rerender } = renderComponent();

    const newData = {
      consumption: [150, 160, 170],
      production: [100, 110, 120],
      timestamps: ["2024-01-05", "2024-01-06", "2024-01-07"],
    };

    rerender(
      <PaperProvider>
        <EnergyChart data={newData} />
      </PaperProvider>,
    );

    expect(
      renderComponent({ data: newData }).getByTestId("energy-chart"),
    ).toBeTruthy();
  });

  it("displays correct legend", () => {
    const { getByTestId } = renderComponent();

    expect(getByTestId("consumption-legend")).toBeTruthy();
    expect(getByTestId("production-legend")).toBeTruthy();
  });

  it("displays correct time range", () => {
    const { getByText } = renderComponent();

    expect(getByText("2024-01-01")).toBeTruthy();
    expect(getByText("2024-01-04")).toBeTruthy();
  });

  it("handles chart refresh callback", () => {
    const onRefresh = jest.fn();
    const { getByTestId } = renderComponent({ onRefresh });

    const refreshButton = getByTestId("refresh-button");
    expect(refreshButton).toBeTruthy();
  });

  it("handles chart export callback", () => {
    const onExport = jest.fn();
    const { getByTestId } = renderComponent({ onExport });

    const exportButton = getByTestId("export-button");
    expect(exportButton).toBeTruthy();
  });

  it("renders with custom title", () => {
    const { getByText } = renderComponent({ title: "Custom Chart Title" });
    expect(getByText("Custom Chart Title")).toBeTruthy();
  });

  it("renders bar chart when type is bar", () => {
    const { getByTestId } = renderComponent({ type: "bar" });
    expect(getByTestId("energy-chart")).toBeTruthy();
  });
});
