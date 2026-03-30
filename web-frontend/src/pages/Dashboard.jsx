import {
  Bolt as BoltIcon,
  MoreVert as MoreVertIcon,
  Speed as SpeedIcon,
  Thermostat as ThermostatIcon,
  TrendingDown as TrendingDownIcon,
  TrendingUp as TrendingUpIcon,
  WaterDrop as WaterIcon,
} from "@mui/icons-material";
import {
  Box,
  Card,
  CardContent,
  CardHeader,
  Chip,
  CircularProgress,
  Divider,
  Grid,
  IconButton,
  Skeleton,
  Typography,
  useTheme,
} from "@mui/material";
import { useEffect, useState } from "react";
import {
  Area,
  AreaChart,
  CartesianGrid,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { useDataService } from "../utils/dataService";

// Energy source data
const sourceData = [
  { name: "Solar", value: 35 },
  { name: "Wind", value: 25 },
  { name: "Hydro", value: 20 },
  { name: "Natural Gas", value: 15 },
  { name: "Coal", value: 5 },
];

const COLORS = ["#4CAF50", "#2196F3", "#00BCD4", "#FFC107", "#F44336"];

const Dashboard = () => {
  const theme = useTheme();
  const { apiStatus, getEnergyData, getCurrentStats } = useDataService();
  const [loading, setLoading] = useState(true);
  const [energyData, setEnergyData] = useState([]);
  const [stats, setStats] = useState({
    currentConsumption: 0,
    predictedPeak: 0,
    temperature: 0,
    humidity: 0,
  });

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Simulate API call delay
        await new Promise((resolve) => setTimeout(resolve, 1000));

        // Get energy data and current stats
        const energyData = getEnergyData(24);
        const currentStats = getCurrentStats();

        setEnergyData(energyData);
        setStats(currentStats);
        setLoading(false);
      } catch (error) {
        console.error("Error fetching dashboard data:", error);
        setLoading(false);
      }
    };

    fetchData();
  }, [getEnergyData, getCurrentStats]);

  // Skeleton loader for stats cards
  const StatCardSkeleton = () => (
    <Card sx={{ height: "100%" }}>
      <CardContent>
        <Box
          sx={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            mb: 2,
          }}
        >
          <Skeleton variant="text" width={120} />
          <Skeleton variant="circular" width={40} height={40} />
        </Box>
        <Skeleton variant="text" width={80} height={40} />
        <Box sx={{ display: "flex", alignItems: "center", mt: 1 }}>
          <Skeleton variant="text" width={150} />
        </Box>
      </CardContent>
    </Card>
  );

  // Skeleton loader for charts
  const ChartSkeleton = () => (
    <Card sx={{ height: "100%" }}>
      <CardHeader
        title={<Skeleton variant="text" width={200} />}
        subheader={<Skeleton variant="text" width={150} />}
        action={
          <IconButton disabled>
            <MoreVertIcon />
          </IconButton>
        }
      />
      <Divider />
      <CardContent>
        <Box
          sx={{
            height: 300,
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
          }}
        >
          <CircularProgress />
        </Box>
      </CardContent>
    </Card>
  );

  return (
    <Box className="fade-in">
      <Typography variant="h4" fontWeight="bold" gutterBottom>
        Dashboard
      </Typography>
      <Typography variant="subtitle1" color="text.secondary" sx={{ mb: 4 }}>
        Overview of energy consumption and predictions
        {apiStatus.status === "healthy" && (
          <Chip
            label={`API v${apiStatus.version}`}
            size="small"
            color="success"
            sx={{ ml: 2 }}
          />
        )}
      </Typography>

      {/* Stats Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          {loading ? (
            <StatCardSkeleton />
          ) : (
            <Card sx={{ height: "100%" }}>
              <CardContent>
                <Box
                  sx={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                    mb: 2,
                  }}
                >
                  <Typography color="text.secondary" variant="subtitle2">
                    Current Consumption
                  </Typography>
                  <Box
                    sx={{
                      backgroundColor: `${theme.palette.primary.light}20`,
                      borderRadius: "50%",
                      width: 40,
                      height: 40,
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                    }}
                  >
                    <BoltIcon sx={{ color: theme.palette.primary.main }} />
                  </Box>
                </Box>
                <Typography variant="h4" fontWeight="bold">
                  {stats.currentConsumption} kWh
                </Typography>
                <Box sx={{ display: "flex", alignItems: "center", mt: 1 }}>
                  <TrendingUpIcon
                    sx={{
                      color: theme.palette.success.main,
                      fontSize: 16,
                      mr: 0.5,
                    }}
                  />
                  <Typography variant="body2" color="success.main">
                    +5.2% from yesterday
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          )}
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          {loading ? (
            <StatCardSkeleton />
          ) : (
            <Card sx={{ height: "100%" }}>
              <CardContent>
                <Box
                  sx={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                    mb: 2,
                  }}
                >
                  <Typography color="text.secondary" variant="subtitle2">
                    Predicted Peak
                  </Typography>
                  <Box
                    sx={{
                      backgroundColor: `${theme.palette.secondary.light}20`,
                      borderRadius: "50%",
                      width: 40,
                      height: 40,
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                    }}
                  >
                    <SpeedIcon sx={{ color: theme.palette.secondary.main }} />
                  </Box>
                </Box>
                <Typography variant="h4" fontWeight="bold">
                  {stats.predictedPeak} kWh
                </Typography>
                <Box sx={{ display: "flex", alignItems: "center", mt: 1 }}>
                  <Typography variant="body2" color="text.secondary">
                    Expected at 18:00
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          )}
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          {loading ? (
            <StatCardSkeleton />
          ) : (
            <Card sx={{ height: "100%" }}>
              <CardContent>
                <Box
                  sx={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                    mb: 2,
                  }}
                >
                  <Typography color="text.secondary" variant="subtitle2">
                    Temperature
                  </Typography>
                  <Box
                    sx={{
                      backgroundColor: `${theme.palette.warning.light}20`,
                      borderRadius: "50%",
                      width: 40,
                      height: 40,
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                    }}
                  >
                    <ThermostatIcon
                      sx={{ color: theme.palette.warning.main }}
                    />
                  </Box>
                </Box>
                <Typography variant="h4" fontWeight="bold">
                  {stats.temperature}°C
                </Typography>
                <Box sx={{ display: "flex", alignItems: "center", mt: 1 }}>
                  <TrendingDownIcon
                    sx={{
                      color: theme.palette.info.main,
                      fontSize: 16,
                      mr: 0.5,
                    }}
                  />
                  <Typography variant="body2" color="info.main">
                    -2°C from yesterday
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          )}
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          {loading ? (
            <StatCardSkeleton />
          ) : (
            <Card sx={{ height: "100%" }}>
              <CardContent>
                <Box
                  sx={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                    mb: 2,
                  }}
                >
                  <Typography color="text.secondary" variant="subtitle2">
                    Humidity
                  </Typography>
                  <Box
                    sx={{
                      backgroundColor: `${theme.palette.info.light}20`,
                      borderRadius: "50%",
                      width: 40,
                      height: 40,
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                    }}
                  >
                    <WaterIcon sx={{ color: theme.palette.info.main }} />
                  </Box>
                </Box>
                <Typography variant="h4" fontWeight="bold">
                  {stats.humidity}%
                </Typography>
                <Box sx={{ display: "flex", alignItems: "center", mt: 1 }}>
                  <TrendingUpIcon
                    sx={{
                      color: theme.palette.success.main,
                      fontSize: 16,
                      mr: 0.5,
                    }}
                  />
                  <Typography variant="body2" color="success.main">
                    +5% from yesterday
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          )}
        </Grid>
      </Grid>

      {/* Charts */}
      <Grid container spacing={3}>
        {/* Energy Consumption Chart */}
        <Grid item xs={12} md={8}>
          {loading ? (
            <ChartSkeleton />
          ) : (
            <Card sx={{ height: "100%" }}>
              <CardHeader
                title="Today's Energy Consumption"
                subheader="Hourly consumption in kWh"
                action={
                  <IconButton aria-label="settings">
                    <MoreVertIcon />
                  </IconButton>
                }
              />
              <Divider />
              <CardContent>
                <Box sx={{ height: 300 }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart
                      data={energyData}
                      margin={{
                        top: 10,
                        right: 30,
                        left: 0,
                        bottom: 0,
                      }}
                    >
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="name" />
                      <YAxis />
                      <Tooltip />
                      <Area
                        type="monotone"
                        dataKey="consumption"
                        stroke={theme.palette.primary.main}
                        fill={theme.palette.primary.main}
                        fillOpacity={0.2}
                      />
                    </AreaChart>
                  </ResponsiveContainer>
                </Box>
              </CardContent>
            </Card>
          )}
        </Grid>

        {/* Energy Sources Chart */}
        <Grid item xs={12} md={4}>
          {loading ? (
            <ChartSkeleton />
          ) : (
            <Card sx={{ height: "100%" }}>
              <CardHeader
                title="Energy Sources"
                subheader="Distribution by source type"
                action={
                  <IconButton aria-label="settings">
                    <MoreVertIcon />
                  </IconButton>
                }
              />
              <Divider />
              <CardContent>
                <Box
                  sx={{
                    height: 300,
                    display: "flex",
                    justifyContent: "center",
                  }}
                >
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={sourceData}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        outerRadius={80}
                        fill="#8884d8"
                        dataKey="value"
                        label={({ name, percent }) =>
                          `${name} ${(percent * 100).toFixed(0)}%`
                        }
                      >
                        {sourceData.map((_entry, index) => (
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
              </CardContent>
            </Card>
          )}
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;
