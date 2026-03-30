import {
  CalendarToday as CalendarIcon,
  Send as SendIcon,
  Timeline as TimelineIcon,
} from "@mui/icons-material";
import {
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Divider,
  FormControl,
  Grid,
  InputLabel,
  MenuItem,
  Paper,
  Select,
  Skeleton,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  Typography,
  useTheme,
} from "@mui/material";
import { useEffect, useState } from "react";
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { useDataService } from "../utils/dataService";

const Predictions = () => {
  const theme = useTheme();
  const { getPredictionData } = useDataService();
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [predictionData, setPredictionData] = useState([]);
  const [meterIds, _setMeterIds] = useState(["meter_001", "meter_002"]);
  const [selectedMeters, setSelectedMeters] = useState(["meter_001"]);
  const [dateRange, setDateRange] = useState({
    start: "2023-04-14",
    end: "2023-04-15",
  });

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Simulate API call delay
        await new Promise((resolve) => setTimeout(resolve, 1500));

        // Get prediction data
        const data = getPredictionData(24);
        setPredictionData(data);
        setLoading(false);
      } catch (error) {
        console.error("Error fetching prediction data:", error);
        setLoading(false);
      }
    };

    fetchData();
  }, [getPredictionData]);

  const handleMeterChange = (event) => {
    setSelectedMeters(event.target.value);
  };

  const handleDateChange = (event) => {
    setDateRange({
      ...dateRange,
      [event.target.name]: event.target.value,
    });
  };

  const handleSubmit = () => {
    setSubmitting(true);
    // Simulate API call
    setTimeout(() => {
      const newData = getPredictionData(24);
      setPredictionData(newData);
      setSubmitting(false);
    }, 1500);
  };

  // Format data for chart
  const chartData = predictionData.map((item) => ({
    name: item.timestamp.split(" ")[1],
    prediction: item.prediction,
    lower: item.lower,
    upper: item.upper,
  }));

  // Skeleton loader for prediction form
  const FormSkeleton = () => (
    <Card sx={{ mb: 4 }}>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Generate New Prediction
        </Typography>
        <Divider sx={{ mb: 3 }} />

        <Grid container spacing={3}>
          <Grid item xs={12} md={4}>
            <Skeleton variant="rectangular" height={56} />
          </Grid>
          <Grid item xs={12} md={3}>
            <Skeleton variant="rectangular" height={56} />
          </Grid>
          <Grid item xs={12} md={3}>
            <Skeleton variant="rectangular" height={56} />
          </Grid>
          <Grid item xs={12} md={2}>
            <Skeleton variant="rectangular" height={56} />
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  );

  // Skeleton loader for results
  const ResultsSkeleton = () => (
    <Card>
      <CardContent>
        <Box
          sx={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            mb: 2,
          }}
        >
          <Box>
            <Skeleton variant="text" width={150} height={32} />
            <Skeleton variant="text" width={200} />
          </Box>
          <Skeleton variant="rectangular" width={120} height={36} />
        </Box>

        <Divider sx={{ mb: 3 }} />

        <Box
          sx={{
            height: 400,
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
        Energy Predictions
      </Typography>
      <Typography variant="subtitle1" color="text.secondary" sx={{ mb: 4 }}>
        Generate and view energy consumption predictions
      </Typography>

      {/* Prediction Form */}
      {loading ? (
        <FormSkeleton />
      ) : (
        <Card sx={{ mb: 4 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Generate New Prediction
            </Typography>
            <Divider sx={{ mb: 3 }} />

            <Grid container spacing={3}>
              <Grid item xs={12} md={4}>
                <FormControl fullWidth>
                  <InputLabel id="meter-select-label">Select Meters</InputLabel>
                  <Select
                    labelId="meter-select-label"
                    id="meter-select"
                    multiple
                    value={selectedMeters}
                    onChange={handleMeterChange}
                    renderValue={(selected) => (
                      <Box sx={{ display: "flex", flexWrap: "wrap", gap: 0.5 }}>
                        {selected.map((value) => (
                          <Chip key={value} label={value} size="small" />
                        ))}
                      </Box>
                    )}
                  >
                    {meterIds.map((meter) => (
                      <MenuItem key={meter} value={meter}>
                        {meter}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>

              <Grid item xs={12} md={3}>
                <TextField
                  fullWidth
                  id="start-date"
                  name="start"
                  label="Start Date"
                  type="date"
                  value={dateRange.start}
                  onChange={handleDateChange}
                  InputLabelProps={{
                    shrink: true,
                  }}
                />
              </Grid>

              <Grid item xs={12} md={3}>
                <TextField
                  fullWidth
                  id="end-date"
                  name="end"
                  label="End Date"
                  type="date"
                  value={dateRange.end}
                  onChange={handleDateChange}
                  InputLabelProps={{
                    shrink: true,
                  }}
                />
              </Grid>

              <Grid
                item
                xs={12}
                md={2}
                sx={{ display: "flex", alignItems: "center" }}
              >
                <Button
                  variant="contained"
                  fullWidth
                  startIcon={
                    submitting ? (
                      <CircularProgress size={20} color="inherit" />
                    ) : (
                      <SendIcon />
                    )
                  }
                  onClick={handleSubmit}
                  disabled={submitting}
                >
                  {submitting ? "Generating..." : "Generate"}
                </Button>
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      )}

      {/* Prediction Results */}
      {loading ? (
        <ResultsSkeleton />
      ) : (
        <Card>
          <CardContent>
            <Box
              sx={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                mb: 2,
              }}
            >
              <Box>
                <Typography variant="h6" gutterBottom>
                  Prediction Results
                </Typography>
                <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                  <CalendarIcon fontSize="small" color="action" />
                  <Typography variant="body2" color="text.secondary">
                    {dateRange.start} to {dateRange.end}
                  </Typography>
                  <Chip
                    label={selectedMeters.join(", ")}
                    size="small"
                    sx={{
                      backgroundColor: `${theme.palette.primary.light}20`,
                      color: theme.palette.primary.main,
                    }}
                  />
                </Box>
              </Box>
              <Button variant="outlined" startIcon={<TimelineIcon />}>
                Export Data
              </Button>
            </Box>

            <Divider sx={{ mb: 3 }} />

            {/* Prediction Chart */}
            <Box sx={{ height: 400, mb: 4 }}>
              <ResponsiveContainer width="100%" height="100%">
                <LineChart
                  data={chartData}
                  margin={{
                    top: 20,
                    right: 30,
                    left: 20,
                    bottom: 10,
                  }}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey="prediction"
                    name="Prediction"
                    stroke={theme.palette.primary.main}
                    strokeWidth={2}
                    dot={{ r: 4 }}
                    activeDot={{ r: 6 }}
                  />
                  <Line
                    type="monotone"
                    dataKey="upper"
                    name="Upper Bound"
                    stroke={theme.palette.grey[400]}
                    strokeDasharray="3 3"
                    dot={false}
                  />
                  <Line
                    type="monotone"
                    dataKey="lower"
                    name="Lower Bound"
                    stroke={theme.palette.grey[400]}
                    strokeDasharray="3 3"
                    dot={false}
                  />
                </LineChart>
              </ResponsiveContainer>
            </Box>

            {/* Prediction Table */}
            <TableContainer
              component={Paper}
              sx={{
                boxShadow: "none",
                border: `1px solid ${theme.palette.divider}`,
              }}
            >
              <Table sx={{ minWidth: 650 }} aria-label="prediction table">
                <TableHead>
                  <TableRow>
                    <TableCell>Timestamp</TableCell>
                    <TableCell align="right">Prediction (kWh)</TableCell>
                    <TableCell align="right">Lower Bound</TableCell>
                    <TableCell align="right">Upper Bound</TableCell>
                    <TableCell align="right">Confidence</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {predictionData.map((row) => (
                    <TableRow
                      key={row.timestamp}
                      sx={{ "&:last-child td, &:last-child th": { border: 0 } }}
                    >
                      <TableCell component="th" scope="row">
                        {row.timestamp}
                      </TableCell>
                      <TableCell align="right">
                        {row.prediction.toFixed(1)}
                      </TableCell>
                      <TableCell align="right">
                        {row.lower.toFixed(1)}
                      </TableCell>
                      <TableCell align="right">
                        {row.upper.toFixed(1)}
                      </TableCell>
                      <TableCell align="right">
                        <Chip
                          label="95%"
                          size="small"
                          sx={{
                            backgroundColor: `${theme.palette.success.light}20`,
                            color: theme.palette.success.main,
                          }}
                        />
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </CardContent>
        </Card>
      )}
    </Box>
  );
};

export default Predictions;
