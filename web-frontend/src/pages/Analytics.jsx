import {
  Box,
  Card,
  CardContent,
  CircularProgress,
  Divider,
  Grid,
  Paper,
  Tab,
  Tabs,
  Typography,
  useTheme,
} from "@mui/material";
import { useEffect, useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Scatter,
  ScatterChart,
  Tooltip,
  XAxis,
  YAxis,
  ZAxis,
} from "recharts";

// Colors for charts
const COLORS = ["#4CAF50", "#2196F3", "#FFC107", "#9C27B0", "#F44336"];

const Analytics = () => {
  const theme = useTheme();
  const [tabValue, setTabValue] = useState(0);
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState({
    monthlyData: [],
    hourlyData: [],
    deviceData: [],
    temperatureData: [],
    seasonalData: [],
  });

  useEffect(() => {
    // Simulate data loading
    const loadData = async () => {
      await new Promise((resolve) => setTimeout(resolve, 1800));

      // Mock data for charts
      setData({
        monthlyData: [
          { name: "Jan", consumption: 4000 },
          { name: "Feb", consumption: 3500 },
          { name: "Mar", consumption: 4800 },
          { name: "Apr", consumption: 3800 },
          { name: "May", consumption: 4300 },
          { name: "Jun", consumption: 5000 },
          { name: "Jul", consumption: 5500 },
          { name: "Aug", consumption: 5200 },
          { name: "Sep", consumption: 4800 },
          { name: "Oct", consumption: 4200 },
          { name: "Nov", consumption: 3800 },
          { name: "Dec", consumption: 4100 },
        ],
        hourlyData: [
          { hour: "00:00", weekday: 120, weekend: 180 },
          { hour: "02:00", weekday: 100, weekend: 150 },
          { hour: "04:00", weekday: 90, weekend: 130 },
          { hour: "06:00", weekday: 150, weekend: 120 },
          { hour: "08:00", weekday: 220, weekend: 160 },
          { hour: "10:00", weekday: 250, weekend: 220 },
          { hour: "12:00", weekday: 280, weekend: 260 },
          { hour: "14:00", weekday: 270, weekend: 280 },
          { hour: "16:00", weekday: 260, weekend: 300 },
          { hour: "18:00", weekday: 300, weekend: 320 },
          { hour: "20:00", weekday: 280, weekend: 340 },
          { hour: "22:00", weekday: 200, weekend: 260 },
        ],
        deviceData: [
          { name: "HVAC", value: 40 },
          { name: "Lighting", value: 15 },
          { name: "Refrigeration", value: 20 },
          { name: "Electronics", value: 10 },
          { name: "Water Heating", value: 15 },
        ],
        temperatureData: [
          { temperature: 15, consumption: 200, time: "Morning", size: 200 },
          { temperature: 18, consumption: 240, time: "Morning", size: 200 },
          { temperature: 22, consumption: 280, time: "Afternoon", size: 200 },
          { temperature: 25, consumption: 320, time: "Afternoon", size: 200 },
          { temperature: 28, consumption: 380, time: "Afternoon", size: 200 },
          { temperature: 26, consumption: 350, time: "Evening", size: 200 },
          { temperature: 22, consumption: 300, time: "Evening", size: 200 },
          { temperature: 18, consumption: 240, time: "Night", size: 200 },
          { temperature: 16, consumption: 220, time: "Night", size: 200 },
        ],
        seasonalData: [
          { season: "Winter", heating: 300, cooling: 50, other: 150 },
          { season: "Spring", heating: 150, cooling: 100, other: 120 },
          { season: "Summer", heating: 30, cooling: 280, other: 130 },
          { season: "Fall", heating: 120, cooling: 120, other: 140 },
        ],
      });

      setLoading(false);
    };

    loadData();
  }, []);

  const handleTabChange = (_event, newValue) => {
    setTabValue(newValue);
  };

  // Skeleton loaders
  const ChartSkeleton = ({ height = 400 }) => (
    <Box
      sx={{
        height,
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
      }}
    >
      <CircularProgress />
    </Box>
  );

  return (
    <Box className="fade-in">
      <Typography variant="h4" fontWeight="bold" gutterBottom>
        Analytics
      </Typography>
      <Typography variant="subtitle1" color="text.secondary" sx={{ mb: 4 }}>
        Detailed analysis of energy consumption patterns
      </Typography>

      {/* Tabs */}
      <Paper sx={{ mb: 4 }}>
        <Tabs
          value={tabValue}
          onChange={handleTabChange}
          indicatorColor="primary"
          textColor="primary"
          variant="fullWidth"
        >
          <Tab label="Consumption Trends" />
          <Tab label="Pattern Analysis" />
          <Tab label="Correlations" />
        </Tabs>
      </Paper>

      {/* Tab Content */}
      <Box sx={{ display: tabValue === 0 ? "block" : "none" }}>
        <Grid container spacing={3}>
          {/* Monthly Consumption */}
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Monthly Energy Consumption
                </Typography>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Total energy consumption by month (kWh)
                </Typography>
                <Divider sx={{ my: 2 }} />

                {loading ? (
                  <ChartSkeleton />
                ) : (
                  <Box sx={{ height: 400 }}>
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart
                        data={data.monthlyData}
                        margin={{
                          top: 20,
                          right: 30,
                          left: 20,
                          bottom: 5,
                        }}
                      >
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="name" />
                        <YAxis />
                        <Tooltip />
                        <Legend />
                        <Bar
                          dataKey="consumption"
                          name="Consumption (kWh)"
                          fill={theme.palette.primary.main}
                        />
                      </BarChart>
                    </ResponsiveContainer>
                  </Box>
                )}
              </CardContent>
            </Card>
          </Grid>

          {/* Hourly Patterns */}
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Hourly Consumption Patterns
                </Typography>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Comparison of weekday vs weekend consumption
                </Typography>
                <Divider sx={{ my: 2 }} />

                {loading ? (
                  <ChartSkeleton />
                ) : (
                  <Box sx={{ height: 400 }}>
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart
                        data={data.hourlyData}
                        margin={{
                          top: 20,
                          right: 30,
                          left: 20,
                          bottom: 5,
                        }}
                      >
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="hour" />
                        <YAxis />
                        <Tooltip />
                        <Legend />
                        <Line
                          type="monotone"
                          dataKey="weekday"
                          name="Weekday"
                          stroke={theme.palette.primary.main}
                          strokeWidth={2}
                          activeDot={{ r: 8 }}
                        />
                        <Line
                          type="monotone"
                          dataKey="weekend"
                          name="Weekend"
                          stroke={theme.palette.secondary.main}
                          strokeWidth={2}
                          activeDot={{ r: 8 }}
                        />
                      </LineChart>
                    </ResponsiveContainer>
                  </Box>
                )}
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Box>

      <Box sx={{ display: tabValue === 1 ? "block" : "none" }}>
        <Grid container spacing={3}>
          {/* Device Breakdown */}
          <Grid item xs={12} md={6}>
            <Card sx={{ height: "100%" }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Consumption by Device Type
                </Typography>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Percentage breakdown of energy usage
                </Typography>
                <Divider sx={{ my: 2 }} />

                {loading ? (
                  <ChartSkeleton />
                ) : (
                  <Box
                    sx={{
                      height: 400,
                      display: "flex",
                      justifyContent: "center",
                      alignItems: "center",
                    }}
                  >
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <Pie
                          data={data.deviceData}
                          cx="50%"
                          cy="50%"
                          labelLine={false}
                          outerRadius={120}
                          fill="#8884d8"
                          dataKey="value"
                          label={({ name, percent }) =>
                            `${name} ${(percent * 100).toFixed(0)}%`
                          }
                        >
                          {data.deviceData.map((_entry, index) => (
                            <Cell
                              key={`cell-${index}`}
                              fill={COLORS[index % COLORS.length]}
                            />
                          ))}
                        </Pie>
                        <Tooltip />
                      </PieChart>
                    </ResponsiveContainer>
                  </Box>
                )}
              </CardContent>
            </Card>
          </Grid>

          {/* Seasonal Patterns */}
          <Grid item xs={12} md={6}>
            <Card sx={{ height: "100%" }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Seasonal Consumption Patterns
                </Typography>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Energy usage across different seasons
                </Typography>
                <Divider sx={{ my: 2 }} />

                {loading ? (
                  <ChartSkeleton />
                ) : (
                  <Box sx={{ height: 400 }}>
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart
                        data={data.seasonalData}
                        margin={{
                          top: 20,
                          right: 30,
                          left: 20,
                          bottom: 5,
                        }}
                      >
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="season" />
                        <YAxis />
                        <Tooltip />
                        <Legend />
                        <Bar
                          dataKey="heating"
                          name="Heating"
                          stackId="a"
                          fill={theme.palette.error.main}
                        />
                        <Bar
                          dataKey="cooling"
                          name="Cooling"
                          stackId="a"
                          fill={theme.palette.info.main}
                        />
                        <Bar
                          dataKey="other"
                          name="Other"
                          stackId="a"
                          fill={theme.palette.success.main}
                        />
                      </BarChart>
                    </ResponsiveContainer>
                  </Box>
                )}
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Box>

      <Box sx={{ display: tabValue === 2 ? "block" : "none" }}>
        <Grid container spacing={3}>
          {/* Temperature Correlation */}
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Temperature vs. Energy Consumption
                </Typography>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Correlation between temperature and energy usage
                </Typography>
                <Divider sx={{ my: 2 }} />

                {loading ? (
                  <ChartSkeleton />
                ) : (
                  <Box sx={{ height: 400 }}>
                    <ResponsiveContainer width="100%" height="100%">
                      <ScatterChart
                        margin={{
                          top: 20,
                          right: 20,
                          bottom: 20,
                          left: 20,
                        }}
                      >
                        <CartesianGrid />
                        <XAxis
                          type="number"
                          dataKey="temperature"
                          name="Temperature"
                          unit="°C"
                          label={{
                            value: "Temperature (°C)",
                            position: "insideBottomRight",
                            offset: -10,
                          }}
                        />
                        <YAxis
                          type="number"
                          dataKey="consumption"
                          name="Consumption"
                          unit=" kWh"
                          label={{
                            value: "Energy Consumption (kWh)",
                            angle: -90,
                            position: "insideLeft",
                          }}
                        />
                        <ZAxis
                          type="number"
                          dataKey="size"
                          range={[100, 500]}
                        />
                        <Tooltip cursor={{ strokeDasharray: "3 3" }} />
                        <Legend />
                        <Scatter
                          name="Energy Usage"
                          data={data.temperatureData}
                          fill={theme.palette.primary.main}
                          shape="circle"
                        />
                      </ScatterChart>
                    </ResponsiveContainer>
                  </Box>
                )}
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Box>
    </Box>
  );
};

export default Analytics;
