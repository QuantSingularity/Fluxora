import { useEffect, useState } from "react";
import { StyleSheet, View } from "react-native";
import {
  ActivityIndicator,
  Appbar,
  Button,
  Card,
  Dialog,
  Paragraph,
  Portal,
  Subheading,
  Text,
  useTheme,
} from "react-native-paper";
import { getHealth, getSummary } from "../api/api"; // Import getSummary

const DashboardScreen = ({ navigation }) => {
  const [healthStatus, setHealthStatus] = useState("checking...");
  const [summaryData, setSummaryData] = useState(null);
  const [loadingHealth, setLoadingHealth] = useState(true);
  const [loadingSummary, setLoadingSummary] = useState(true);
  const [error, setError] = useState(null);
  const [errorVisible, setErrorVisible] = useState(false);
  const theme = useTheme();

  const hideErrorDialog = () => setErrorVisible(false);

  useEffect(() => {
    const checkApiHealth = async () => {
      try {
        setLoadingHealth(true);
        const data = await getHealth();
        setHealthStatus(data.status || "unknown");
      } catch (err) {
        console.error("Dashboard API Health Check Failed:", err);
        setError(
          "Failed to connect to the backend API. Please ensure it is running.",
        );
        setErrorVisible(true);
        setHealthStatus("error");
      } finally {
        setLoadingHealth(false);
      }
    };

    const fetchSummary = async () => {
      try {
        setLoadingSummary(true);
        const data = await getSummary();
        setSummaryData(data);
      } catch (err) {
        console.error("Dashboard Fetch Summary Failed:", err);
        // Don't show a blocking error for summary, maybe just log or show inline
        setSummaryData(null); // Indicate failure or use placeholder
      } finally {
        setLoadingSummary(false);
      }
    };

    checkApiHealth();
    fetchSummary();
  }, []);

  return (
    <View style={styles.container}>
      <Appbar.Header>
        <Appbar.Content title="Fluxora Dashboard" />
        {/* <Appbar.Action icon="menu" onPress={() => navigation.openDrawer()} /> */}
      </Appbar.Header>

      <View style={styles.content}>
        <Card style={styles.card}>
          <Card.Title title="System Overview" />
          <Card.Content>
            <View style={styles.statusContainer}>
              <Text style={styles.statusLabel}>Backend API Status:</Text>
              {loadingHealth ? (
                <ActivityIndicator
                  animating={true}
                  size="small"
                  color={theme.colors.primary}
                />
              ) : (
                <Text
                  style={[
                    styles.statusValue,
                    {
                      color:
                        healthStatus === "healthy"
                          ? "green"
                          : theme.colors.error,
                    },
                  ]}
                >
                  {healthStatus.toUpperCase()}
                </Text>
              )}
            </View>
            {loadingSummary ? (
              <ActivityIndicator
                animating={true}
                size="small"
                style={{ marginVertical: 10 }}
              />
            ) : summaryData ? (
              <View style={styles.summaryDetails}>
                <Subheading>Key Metrics</Subheading>
                <Paragraph>
                  Total Predictions Made:{" "}
                  {summaryData.totalPredictions ?? "N/A"}
                </Paragraph>
                <Paragraph>
                  Average Model Accuracy:{" "}
                  {summaryData.averageAccuracy
                    ? `${(summaryData.averageAccuracy * 100).toFixed(1)}%`
                    : "N/A"}
                </Paragraph>
                <Paragraph>
                  Last Prediction At: {summaryData.lastPredictionTime ?? "N/A"}
                </Paragraph>
              </View>
            ) : (
              <Paragraph
                style={{ fontStyle: "italic", color: theme.colors.disabled }}
              >
                Summary data unavailable.
              </Paragraph>
            )}
          </Card.Content>
        </Card>

        <Card style={styles.card}>
          <Card.Title title="Quick Actions" />
          <Card.Actions style={styles.actionsContainer}>
            <Button
              icon="chart-line"
              mode="contained"
              onPress={() => navigation.navigate("Predictions")}
              style={styles.button}
            >
              Predictions
            </Button>
            <Button
              icon="google-analytics"
              mode="contained"
              onPress={() => navigation.navigate("Analytics")}
              style={styles.button}
            >
              Analytics
            </Button>
          </Card.Actions>
        </Card>

        <Text style={styles.infoText}>
          Welcome to the Fluxora mobile application.
        </Text>
      </View>

      <Portal>
        <Dialog visible={errorVisible} onDismiss={hideErrorDialog}>
          <Dialog.Title>Connection Error</Dialog.Title>
          <Dialog.Content>
            <Paragraph>{error}</Paragraph>
          </Dialog.Content>
          <Dialog.Actions>
            <Button onPress={hideErrorDialog}>OK</Button>
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
    marginBottom: 10, // Space before summary
  },
  statusLabel: {
    fontSize: 16,
    marginRight: 10,
    color: "#555",
  },
  statusValue: {
    fontSize: 16,
    fontWeight: "bold",
  },
  summaryDetails: {
    marginTop: 10,
    paddingTop: 10,
    borderTopWidth: 1,
    borderTopColor: "#eee",
  },
  actionsContainer: {
    justifyContent: "space-around",
    paddingBottom: 10,
  },
  button: {
    marginHorizontal: 5,
  },
  infoText: {
    fontSize: 16,
    color: "#666",
    textAlign: "center",
    marginTop: "auto",
    paddingBottom: 20,
  },
});

export default DashboardScreen;
