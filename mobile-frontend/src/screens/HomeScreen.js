import { useEffect, useState } from "react";
import {
  RefreshControl,
  TextInput as RNTextInput,
  ScrollView,
  StyleSheet,
  View,
} from "react-native";
import {
  ActivityIndicator,
  Appbar,
  Button,
  Card,
  Dialog,
  Paragraph,
  Portal,
  Surface,
  Text,
  Title,
  useTheme,
} from "react-native-paper";
import { getHealth, getSummary } from "../api/api";
import { useAuth } from "../contexts/AuthContext";

export const HomeScreen = ({ navigation }) => {
  const { user, logout } = useAuth();
  const theme = useTheme();
  const [healthStatus, setHealthStatus] = useState("checking...");
  const [summaryData, setSummaryData] = useState(null);
  const [tasks, setTasks] = useState([
    {
      id: "1",
      title: "Review Energy Data",
      description: "Check yesterday's consumption",
      completed: false,
    },
    {
      id: "2",
      title: "Analyze Predictions",
      description: "Review weekly forecast accuracy",
      completed: false,
    },
  ]);
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState(null);
  const [errorVisible, setErrorVisible] = useState(false);
  const [showAddTask, setShowAddTask] = useState(false);
  const [newTaskTitle, setNewTaskTitle] = useState("");
  const [newTaskDescription, setNewTaskDescription] = useState("");
  const [validationError, setValidationError] = useState({});

  const hideErrorDialog = () => setErrorVisible(false);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);

      const [health, summary] = await Promise.all([getHealth(), getSummary()]);

      setHealthStatus(health.status || "unknown");
      setSummaryData(summary);
    } catch (err) {
      console.error("HomeScreen data fetch failed:", err);
      setError("Failed to load data. Please check your connection.");
      setErrorVisible(true);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const onRefresh = () => {
    setRefreshing(true);
    fetchData();
  };

  const handleLogout = async () => {
    try {
      await logout();
      navigation.navigate("Login");
    } catch (_err) {
      setError("Failed to logout. Please try again.");
      setErrorVisible(true);
    }
  };

  const handleTaskComplete = (taskId) => {
    setTasks(
      tasks.map((task) =>
        task.id === taskId ? { ...task, completed: !task.completed } : task,
      ),
    );
  };

  const handleAddTask = () => {
    const errors = {};
    if (!newTaskTitle.trim()) errors.title = "Title is required";
    if (!newTaskDescription.trim())
      errors.description = "Description is required";

    if (Object.keys(errors).length > 0) {
      setValidationError(errors);
      return;
    }

    const newTask = {
      id: Date.now().toString(),
      title: newTaskTitle,
      description: newTaskDescription,
      completed: false,
    };

    setTasks([...tasks, newTask]);
    setNewTaskTitle("");
    setNewTaskDescription("");
    setShowAddTask(false);
    setValidationError({});
  };

  return (
    <View style={styles.container}>
      <Appbar.Header>
        <Appbar.Content title="Home" />
      </Appbar.Header>

      <ScrollView
        style={styles.content}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
      >
        <Card style={styles.card}>
          <Card.Content>
            <Title>Welcome, {user?.username || "Guest"}</Title>
            <Paragraph>{user?.email || "Please log in"}</Paragraph>
            <View style={styles.statusContainer}>
              <Text>Backend Status: </Text>
              {loading ? (
                <ActivityIndicator size="small" />
              ) : (
                <Text
                  style={{
                    color: healthStatus === "healthy" ? "green" : "red",
                  }}
                >
                  {healthStatus.toUpperCase()}
                </Text>
              )}
            </View>
          </Card.Content>
          <Card.Actions>
            <Button
              icon="account-circle"
              onPress={() => navigation.navigate("Profile")}
              testID="profile-button"
            >
              Profile
            </Button>
            <Button icon="logout" onPress={handleLogout} testID="logout-button">
              Logout
            </Button>
          </Card.Actions>
        </Card>

        <Card style={styles.card}>
          <Card.Title title="Quick Stats" />
          <Card.Content>
            {summaryData ? (
              <>
                <Paragraph>
                  Total Predictions: {summaryData.totalPredictions || "N/A"}
                </Paragraph>
                <Paragraph>
                  Average Accuracy:{" "}
                  {summaryData.averageAccuracy
                    ? `${(summaryData.averageAccuracy * 100).toFixed(1)}%`
                    : "N/A"}
                </Paragraph>
                <Paragraph>
                  Last Update: {summaryData.lastPredictionTime || "N/A"}
                </Paragraph>
              </>
            ) : (
              <Paragraph>Loading stats...</Paragraph>
            )}
          </Card.Content>
        </Card>

        <Card style={styles.card}>
          <Card.Title title="Tasks" />
          <Card.Content>
            <View testID="task-list">
              {tasks.length === 0 ? (
                <Text>No tasks available</Text>
              ) : (
                tasks.map((task) => (
                  <Surface
                    key={task.id}
                    style={[
                      styles.taskItem,
                      {
                        backgroundColor: task.completed
                          ? "#4CAF50"
                          : theme.colors.surface,
                      },
                    ]}
                    testID={`task-${task.title}`}
                  >
                    <View style={styles.taskContent}>
                      <View style={styles.taskInfo}>
                        <Text style={styles.taskTitle}>{task.title}</Text>
                        <Text style={styles.taskDescription}>
                          {task.description}
                        </Text>
                      </View>
                      <Button
                        testID={`task-checkbox-${task.id}`}
                        onPress={() => handleTaskComplete(task.id)}
                        icon={
                          task.completed
                            ? "check-circle"
                            : "checkbox-blank-circle-outline"
                        }
                      >
                        {task.completed ? "Done" : "Mark Done"}
                      </Button>
                    </View>
                  </Surface>
                ))
              )}
            </View>
          </Card.Content>
          <Card.Actions>
            <Button
              icon="plus"
              onPress={() => setShowAddTask(true)}
              testID="add-task-button"
            >
              Add Task
            </Button>
          </Card.Actions>
        </Card>
      </ScrollView>

      <Portal>
        <Dialog visible={errorVisible} onDismiss={hideErrorDialog}>
          <Dialog.Title>Error</Dialog.Title>
          <Dialog.Content>
            <Paragraph>{error}</Paragraph>
          </Dialog.Content>
          <Dialog.Actions>
            <Button onPress={hideErrorDialog}>OK</Button>
          </Dialog.Actions>
        </Dialog>

        <Dialog visible={showAddTask} onDismiss={() => setShowAddTask(false)}>
          <Dialog.Title>Add New Task</Dialog.Title>
          <Dialog.Content>
            <RNTextInput
              placeholder="Task title"
              value={newTaskTitle}
              onChangeText={(text) => {
                setNewTaskTitle(text);
                if (validationError.title) {
                  setValidationError({ ...validationError, title: null });
                }
              }}
              style={styles.input}
            />
            {validationError.title && (
              <Text style={styles.errorText}>{validationError.title}</Text>
            )}
            <RNTextInput
              placeholder="Task description"
              value={newTaskDescription}
              onChangeText={(text) => {
                setNewTaskDescription(text);
                if (validationError.description) {
                  setValidationError({ ...validationError, description: null });
                }
              }}
              multiline
              style={[styles.input, styles.multilineInput]}
            />
            {validationError.description && (
              <Text style={styles.errorText}>
                {validationError.description}
              </Text>
            )}
          </Dialog.Content>
          <Dialog.Actions>
            <Button onPress={() => setShowAddTask(false)}>Cancel</Button>
            <Button onPress={handleAddTask} testID="submit-task-button">
              Add
            </Button>
          </Dialog.Actions>
        </Dialog>
      </Portal>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#f5f5f5",
  },
  content: {
    flex: 1,
    padding: 15,
  },
  card: {
    marginBottom: 15,
    elevation: 3,
  },
  statusContainer: {
    flexDirection: "row",
    alignItems: "center",
    marginTop: 10,
  },
  taskItem: {
    padding: 12,
    marginBottom: 10,
    borderRadius: 8,
    elevation: 2,
  },
  taskContent: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
  },
  taskInfo: {
    flex: 1,
  },
  taskTitle: {
    fontSize: 16,
    fontWeight: "bold",
    marginBottom: 4,
  },
  taskDescription: {
    fontSize: 14,
    color: "#666",
  },
  input: {
    borderWidth: 1,
    borderColor: "#ddd",
    borderRadius: 4,
    padding: 10,
    marginBottom: 10,
  },
  multilineInput: {
    minHeight: 80,
    textAlignVertical: "top",
  },
  errorText: {
    color: "red",
    fontSize: 12,
    marginTop: -8,
    marginBottom: 10,
  },
});

export default HomeScreen;
