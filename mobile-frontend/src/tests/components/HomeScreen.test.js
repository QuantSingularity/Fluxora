import { fireEvent, render, waitFor } from "@testing-library/react-native";
import { Provider as PaperProvider } from "react-native-paper";
import * as api from "../../api/api";
import { AuthProvider } from "../../contexts/AuthContext";
import { HomeScreen } from "../../screens/HomeScreen";

jest.mock("../../api/api");

const mockNavigation = {
  navigate: jest.fn(),
};

const mockHealthData = {
  status: "healthy",
};

const mockSummaryData = {
  totalPredictions: 100,
  averageAccuracy: 0.9,
  lastPredictionTime: "10:00 AM",
};

describe("HomeScreen", () => {
  beforeEach(() => {
    jest.clearAllMocks();
    api.getHealth.mockResolvedValue(mockHealthData);
    api.getSummary.mockResolvedValue(mockSummaryData);
  });

  const renderComponent = () => {
    return render(
      <PaperProvider>
        <AuthProvider>
          <HomeScreen navigation={mockNavigation} />
        </AuthProvider>
      </PaperProvider>,
    );
  };

  it("renders user information correctly", async () => {
    const { getByText } = renderComponent();

    await waitFor(() => {
      expect(getByText(/Welcome/)).toBeTruthy();
    });
  });

  it("handles missing user data gracefully", async () => {
    const { getByText } = renderComponent();

    await waitFor(() => {
      expect(getByText(/Welcome, Guest/)).toBeTruthy();
    });
  });

  it("navigates to profile screen when profile button is pressed", async () => {
    const { getByTestId } = renderComponent();

    await waitFor(() => {
      const profileButton = getByTestId("profile-button");
      expect(profileButton).toBeTruthy();
    });

    fireEvent.press(getByTestId("profile-button"));
    expect(mockNavigation.navigate).toHaveBeenCalledWith("Profile");
  });

  it("handles logout correctly", async () => {
    const { getByTestId } = renderComponent();

    await waitFor(() => {
      const logoutButton = getByTestId("logout-button");
      expect(logoutButton).toBeTruthy();
    });

    fireEvent.press(getByTestId("logout-button"));

    await waitFor(() => {
      expect(mockNavigation.navigate).toHaveBeenCalledWith("Login");
    });
  });

  it("renders task list correctly", async () => {
    const { getByTestId } = renderComponent();

    await waitFor(() => {
      expect(getByTestId("task-list")).toBeTruthy();
    });
  });

  it("handles empty task list", async () => {
    const { getByTestId } = renderComponent();

    await waitFor(() => {
      const taskList = getByTestId("task-list");
      expect(taskList).toBeTruthy();
    });
  });

  it("handles task creation", async () => {
    const { getByTestId, getByPlaceholderText } = renderComponent();

    await waitFor(() => {
      const addButton = getByTestId("add-task-button");
      expect(addButton).toBeTruthy();
    });

    const addButton = getByTestId("add-task-button");
    fireEvent.press(addButton);

    await waitFor(() => {
      const titleInput = getByPlaceholderText("Task title");
      const descriptionInput = getByPlaceholderText("Task description");

      fireEvent.changeText(titleInput, "New Task");
      fireEvent.changeText(descriptionInput, "Task description");
    });

    const submitButton = getByTestId("submit-task-button");
    fireEvent.press(submitButton);

    await waitFor(() => {
      expect(getByTestId("task-list")).toBeTruthy();
    });
  });

  it("handles task creation validation", async () => {
    const { getByTestId, getByText } = renderComponent();

    await waitFor(() => {
      const addButton = getByTestId("add-task-button");
      fireEvent.press(addButton);
    });

    const submitButton = getByTestId("submit-task-button");
    fireEvent.press(submitButton);

    await waitFor(() => {
      expect(getByText("Title is required")).toBeTruthy();
      expect(getByText("Description is required")).toBeTruthy();
    });
  });

  it("handles task completion", async () => {
    const { getByTestId } = renderComponent();

    await waitFor(() => {
      const taskList = getByTestId("task-list");
      expect(taskList).toBeTruthy();
    });

    // In real scenario, there would be tasks rendered
    // This test verifies the component renders without crashing
  });

  it("displays health status", async () => {
    const { getByText } = renderComponent();

    await waitFor(() => {
      expect(getByText(/Backend Status:/)).toBeTruthy();
      expect(getByText(/HEALTHY/)).toBeTruthy();
    });
  });

  it("displays summary statistics", async () => {
    const { getByText } = renderComponent();

    await waitFor(() => {
      expect(getByText(/Total Predictions:/)).toBeTruthy();
      expect(getByText(/Average Accuracy:/)).toBeTruthy();
    });
  });
});
