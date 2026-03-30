import { useEffect, useState } from "react";
import {
  Dimensions,
  RefreshControl,
  ScrollView,
  StyleSheet,
  View,
} from "react-native";
import { BarChart, LineChart } from "react-native-chart-kit";
import {
  ActivityIndicator,
  Appbar,
  Card,
  DataTable,
  Paragraph,
  Text,
  Title,
  useTheme,
} from "react-native-paper";
import { getHistoricalData, getModelMetrics } from "../api/api";

const screenWidth = Dimensions.get("window").width;

const AnalyticsScreen = ({ navigation }) => {
  const theme = useTheme();
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState(null);
  const [historicalData, setHistoricalData] = useState(null);
  const [metrics, setMetrics] = useState(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);

      const [data, metricsData] = await Promise.all([
        getHistoricalData(),
        getModelMetrics(),
      ]);

      setHistoricalData(data);
      setMetrics(metricsData);
    } catch (err) {
      console.error("Failed to load analytics data:", err);
      setError("Failed to load analytics data. Please try again.");
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

  const chartConfig = {
    backgroundColor: theme.colors.surface,
    backgroundGradientFrom: theme.colors.surface,
    backgroundGradientTo: theme.colors.backdrop,
    decimalPlaces: 2,
    color: (opacity = 1) =>
      `rgba(${theme.dark ? "255, 255, 255" : "0, 0, 0"}, ${opacity})`,
    labelColor: (opacity = 1) =>
      `rgba(${theme.dark ? "255, 255, 255" : "0, 0, 0"}, ${opacity})`,
    style: {
      borderRadius: 16,
    },
    propsForDots: {
      r: "6",
      strokeWidth: "2",
      stroke: theme.colors.primary,
    },
  };

  if (loading && !refreshing) {
    return (
      <View style={styles.container}>
        <Appbar.Header>
          <Appbar.Content title="Analytics" />
        </Appbar.Header>
        <View style={styles.centerContent}>
          <ActivityIndicator
            animating={true}
            size="large"
            color={theme.colors.primary}
          />
          <Text style={styles.loadingText}>Loading analytics...</Text>
        </View>
      </View>
    );
  }

  if (error && !historicalData) {
    return (
      <View style={styles.container}>
        <Appbar.Header>
          <Appbar.Content title="Analytics" />
        </Appbar.Header>
        <View style={styles.centerContent}>
          <Card style={styles.card}>
            <Card.Content>
              <Paragraph style={styles.errorText}>{error}</Paragraph>
            </Card.Content>
          </Card>
        </View>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <Appbar.Header>
        <Appbar.Content title="Analytics" />
      </Appbar.Header>

      <ScrollView
        style={styles.content}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
      >
        {/* Energy Consumption Trend */}
        <Card style={styles.card}>
          <Card.Content>
            <Title>Energy Consumption Trend (Monthly)</Title>
            <Paragraph style={styles.subtitle}>
              Historical consumption patterns over the last 6 months
            </Paragraph>
            {historicalData?.lineData && (
              <LineChart
                data={historicalData.lineData}
                width={screenWidth - 60}
                height={220}
                chartConfig={chartConfig}
                bezier
                style={styles.chart}
              />
            )}
          </Card.Content>
        </Card>

        {/* Peak Usage Times */}
        <Card style={styles.card}>
          <Card.Content>
            <Title>Peak Usage Times (Weekly)</Title>
            <Paragraph style={styles.subtitle}>
              Peak energy consumption by day of week
            </Paragraph>
            {historicalData?.barData && (
              <BarChart
                data={historicalData.barData}
                width={screenWidth - 60}
                height={220}
                yAxisLabel="kWh "
                chartConfig={chartConfig}
                verticalLabelRotation={30}
                style={styles.chart}
              />
            )}
          </Card.Content>
        </Card>

        {/* Model Performance Metrics */}
        <Card style={styles.card}>
          <Card.Content>
            <Title>Model Performance Metrics</Title>
            <Paragraph style={styles.subtitle}>
              Current prediction model accuracy indicators
            </Paragraph>

            {metrics ? (
              <DataTable>
                <DataTable.Header>
                  <DataTable.Title>Metric</DataTable.Title>
                  <DataTable.Title numeric>Value</DataTable.Title>
                  <DataTable.Title numeric>Status</DataTable.Title>
                </DataTable.Header>

                <DataTable.Row>
                  <DataTable.Cell>Mean Absolute Error (MAE)</DataTable.Cell>
                  <DataTable.Cell numeric>
                    {metrics.mae?.toFixed(4)}
                  </DataTable.Cell>
                  <DataTable.Cell numeric>
                    <Text
                      style={{ color: metrics.mae < 0.2 ? "green" : "orange" }}
                    >
                      {metrics.mae < 0.2 ? "Good" : "Fair"}
                    </Text>
                  </DataTable.Cell>
                </DataTable.Row>

                <DataTable.Row>
                  <DataTable.Cell>Root Mean Square Error (RMSE)</DataTable.Cell>
                  <DataTable.Cell numeric>
                    {metrics.rmse?.toFixed(4)}
                  </DataTable.Cell>
                  <DataTable.Cell numeric>
                    <Text
                      style={{
                        color: metrics.rmse < 0.25 ? "green" : "orange",
                      }}
                    >
                      {metrics.rmse < 0.25 ? "Good" : "Fair"}
                    </Text>
                  </DataTable.Cell>
                </DataTable.Row>

                <DataTable.Row>
                  <DataTable.Cell>R² Score</DataTable.Cell>
                  <DataTable.Cell numeric>
                    {metrics.r2_score?.toFixed(4)}
                  </DataTable.Cell>
                  <DataTable.Cell numeric>
                    <Text
                      style={{
                        color: metrics.r2_score > 0.85 ? "green" : "orange",
                      }}
                    >
                      {metrics.r2_score > 0.85 ? "Excellent" : "Good"}
                    </Text>
                  </DataTable.Cell>
                </DataTable.Row>
              </DataTable>
            ) : (
              <Paragraph style={styles.placeholderText}>
                Metrics data not available
              </Paragraph>
            )}

            <View style={styles.metricsInfo}>
              <Paragraph style={styles.infoText}>
                <Text style={styles.bold}>MAE:</Text> Average absolute
                difference between predictions and actual values
              </Paragraph>
              <Paragraph style={styles.infoText}>
                <Text style={styles.bold}>RMSE:</Text> Square root of average
                squared differences
              </Paragraph>
              <Paragraph style={styles.infoText}>
                <Text style={styles.bold}>R² Score:</Text> Proportion of
                variance explained by the model (0-1)
              </Paragraph>
            </View>
          </Card.Content>
        </Card>

        {/* Energy Insights */}
        <Card style={styles.card}>
          <Card.Content>
            <Title>Energy Insights</Title>
            <View style={styles.insightItem}>
              <Text style={styles.insightLabel}>🔋 Average Daily Usage:</Text>
              <Text style={styles.insightValue}>42.5 kWh</Text>
            </View>
            <View style={styles.insightItem}>
              <Text style={styles.insightLabel}>📊 Weekly Trend:</Text>
              <Text style={[styles.insightValue, { color: "green" }]}>
                ↓ 5.2% decrease
              </Text>
            </View>
            <View style={styles.insightItem}>
              <Text style={styles.insightLabel}>⚡ Peak Hour:</Text>
              <Text style={styles.insightValue}>18:00 - 20:00</Text>
            </View>
            <View style={styles.insightItem}>
              <Text style={styles.insightLabel}>💰 Estimated Savings:</Text>
              <Text style={[styles.insightValue, { color: "green" }]}>
                $24.50/month
              </Text>
            </View>
          </Card.Content>
        </Card>
      </ScrollView>
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
  centerContent: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    padding: 20,
  },
  card: {
    marginBottom: 15,
    elevation: 3,
  },
  chart: {
    marginVertical: 8,
    borderRadius: 16,
  },
  subtitle: {
    fontSize: 12,
    color: "#666",
    marginBottom: 10,
  },
  loadingText: {
    marginTop: 10,
    fontSize: 16,
    color: "#666",
  },
  errorText: {
    color: "red",
    textAlign: "center",
    fontSize: 16,
  },
  placeholderText: {
    fontSize: 14,
    color: "#666",
    textAlign: "center",
    marginTop: 10,
    fontStyle: "italic",
  },
  metricsInfo: {
    marginTop: 15,
    padding: 10,
    backgroundColor: "#f9f9f9",
    borderRadius: 8,
  },
  infoText: {
    fontSize: 12,
    color: "#555",
    marginBottom: 5,
  },
  bold: {
    fontWeight: "bold",
  },
  insightItem: {
    flexDirection: "row",
    justifyContent: "space-between",
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: "#eee",
  },
  insightLabel: {
    fontSize: 14,
    color: "#555",
  },
  insightValue: {
    fontSize: 14,
    fontWeight: "bold",
    color: "#333",
  },
});

export default AnalyticsScreen;
