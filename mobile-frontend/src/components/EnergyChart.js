import { Dimensions, StyleSheet, TouchableOpacity, View } from "react-native";
import {
  BarChart as RNBarChart,
  LineChart as RNLineChart,
} from "react-native-chart-kit";
import { Card, Text, Title, useTheme } from "react-native-paper";

const screenWidth = Dimensions.get("window").width;

/**
 * EnergyChart Component
 * Displays energy consumption and production data in chart format
 */
export const EnergyChart = ({
  data,
  type = "line",
  title = "Energy Chart",
  onRefresh,
  onExport,
}) => {
  const theme = useTheme();

  if (!data?.consumption || data.consumption.length === 0) {
    return (
      <Card style={styles.card}>
        <Card.Content>
          <Title>{title}</Title>
          <Text style={styles.noDataText}>No data available</Text>
        </Card.Content>
      </Card>
    );
  }

  const chartConfig = {
    backgroundColor: theme.colors.surface,
    backgroundGradientFrom: theme.colors.surface,
    backgroundGradientTo: theme.colors.backdrop,
    decimalPlaces: 1,
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

  const chartData = {
    labels: data.timestamps || [],
    datasets: [
      {
        data: data.consumption,
        color: (opacity = 1) => `rgba(255, 99, 132, ${opacity})`,
        strokeWidth: 2,
      },
    ],
  };

  if (data.production && data.production.length > 0) {
    chartData.datasets.push({
      data: data.production,
      color: (opacity = 1) => `rgba(75, 192, 192, ${opacity})`,
      strokeWidth: 2,
    });
  }

  return (
    <Card style={styles.card} testID="energy-chart">
      <Card.Content>
        <View style={styles.header}>
          <Title>{title}</Title>
          <View style={styles.actions}>
            {onRefresh && (
              <TouchableOpacity onPress={onRefresh} testID="refresh-button">
                <Text style={styles.actionButton}>⟳</Text>
              </TouchableOpacity>
            )}
            {onExport && (
              <TouchableOpacity onPress={onExport} testID="export-button">
                <Text style={styles.actionButton}>⤓</Text>
              </TouchableOpacity>
            )}
          </View>
        </View>

        {/* Legend */}
        <View style={styles.legend}>
          <View style={styles.legendItem} testID="consumption-legend">
            <View
              style={[
                styles.legendColor,
                { backgroundColor: "rgba(255, 99, 132, 1)" },
              ]}
            />
            <Text style={styles.legendText}>Energy Consumption</Text>
          </View>
          {data.production && data.production.length > 0 && (
            <View style={styles.legendItem} testID="production-legend">
              <View
                style={[
                  styles.legendColor,
                  { backgroundColor: "rgba(75, 192, 192, 1)" },
                ]}
              />
              <Text style={styles.legendText}>Energy Production</Text>
            </View>
          )}
        </View>

        {/* Chart */}
        {type === "line" ? (
          <RNLineChart
            data={chartData}
            width={screenWidth - 80}
            height={220}
            chartConfig={chartConfig}
            bezier
            style={styles.chart}
            testID="line-chart"
          />
        ) : (
          <RNBarChart
            data={chartData}
            width={screenWidth - 80}
            height={220}
            chartConfig={chartConfig}
            style={styles.chart}
            testID="bar-chart"
          />
        )}

        {/* Time Range Display */}
        {data.timestamps && data.timestamps.length > 0 && (
          <View style={styles.timeRange}>
            <Text style={styles.timeText}>{data.timestamps[0]}</Text>
            <Text style={styles.timeText}>
              {data.timestamps[data.timestamps.length - 1]}
            </Text>
          </View>
        )}
      </Card.Content>
    </Card>
  );
};

const styles = StyleSheet.create({
  card: {
    marginVertical: 10,
    elevation: 3,
  },
  header: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 10,
  },
  actions: {
    flexDirection: "row",
    gap: 10,
  },
  actionButton: {
    fontSize: 24,
    padding: 5,
  },
  legend: {
    flexDirection: "row",
    justifyContent: "center",
    flexWrap: "wrap",
    marginBottom: 15,
    gap: 15,
  },
  legendItem: {
    flexDirection: "row",
    alignItems: "center",
  },
  legendColor: {
    width: 16,
    height: 16,
    marginRight: 8,
    borderRadius: 8,
  },
  legendText: {
    fontSize: 12,
  },
  chart: {
    marginVertical: 8,
    borderRadius: 16,
  },
  timeRange: {
    flexDirection: "row",
    justifyContent: "space-between",
    marginTop: 10,
  },
  timeText: {
    fontSize: 10,
    color: "#666",
  },
  noDataText: {
    textAlign: "center",
    marginTop: 20,
    fontSize: 16,
    color: "#999",
  },
});

export default EnergyChart;
