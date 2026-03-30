import {
  Delete as DeleteIcon,
  Language as LanguageIcon,
  Notifications as NotificationsIcon,
  Refresh as RefreshIcon,
  Save as SaveIcon,
  Security as SecurityIcon,
  Storage as StorageIcon,
  ColorLens as ThemeIcon,
} from "@mui/icons-material";
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Divider,
  Grid,
  IconButton,
  List,
  ListItem,
  ListItemIcon,
  ListItemSecondaryAction,
  ListItemText,
  Skeleton,
  Snackbar,
  Switch,
  TextField,
  Typography,
  useTheme,
} from "@mui/material";
import { useEffect, useState } from "react";

const Settings = () => {
  const _theme = useTheme();
  const [loading, setLoading] = useState(true);
  const [settings, setSettings] = useState({
    notifications: true,
    darkMode: false,
    dataRetention: 90,
    apiKey: "sk_test_51HG7LkKF5YG78D6H2QsJgYbIhaeEDq",
    language: "en",
    autoRefresh: true,
  });
  const [snackbar, setSnackbar] = useState({
    open: false,
    message: "",
    severity: "success",
  });

  useEffect(() => {
    // Simulate loading settings from API
    const loadSettings = async () => {
      await new Promise((resolve) => setTimeout(resolve, 1200));
      setLoading(false);
    };

    loadSettings();
  }, []);

  const handleSettingChange = (setting, value) => {
    setSettings({
      ...settings,
      [setting]: value,
    });
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    handleSettingChange(name, value);
  };

  const handleSwitchChange = (e) => {
    const { name, checked } = e.target;
    handleSettingChange(name, checked);
  };

  const handleSaveSettings = () => {
    // Simulate saving settings to API
    setSnackbar({
      open: true,
      message: "Settings saved successfully!",
      severity: "success",
    });
  };

  const handleCloseSnackbar = () => {
    setSnackbar({
      ...snackbar,
      open: false,
    });
  };

  const handleResetApiKey = () => {
    handleSettingChange(
      "apiKey",
      `sk_test_${Math.random().toString(36).substring(2, 15)}`,
    );
    setSnackbar({
      open: true,
      message: "API key regenerated successfully!",
      severity: "info",
    });
  };

  // Skeleton loader for settings
  const SettingsSkeleton = () => (
    <List>
      <ListItem>
        <ListItemIcon>
          <Skeleton variant="circular" width={24} height={24} />
        </ListItemIcon>
        <ListItemText
          primary={<Skeleton variant="text" width={120} />}
          secondary={<Skeleton variant="text" width={200} />}
        />
        <ListItemSecondaryAction>
          <Skeleton variant="rectangular" width={40} height={24} />
        </ListItemSecondaryAction>
      </ListItem>
      <ListItem>
        <ListItemIcon>
          <Skeleton variant="circular" width={24} height={24} />
        </ListItemIcon>
        <ListItemText
          primary={<Skeleton variant="text" width={100} />}
          secondary={<Skeleton variant="text" width={180} />}
        />
        <ListItemSecondaryAction>
          <Skeleton variant="rectangular" width={40} height={24} />
        </ListItemSecondaryAction>
      </ListItem>
      <ListItem>
        <ListItemIcon>
          <Skeleton variant="circular" width={24} height={24} />
        </ListItemIcon>
        <ListItemText
          primary={<Skeleton variant="text" width={80} />}
          secondary={<Skeleton variant="text" width={160} />}
        />
        <ListItemSecondaryAction>
          <Skeleton variant="rectangular" width={100} height={40} />
        </ListItemSecondaryAction>
      </ListItem>
    </List>
  );

  return (
    <Box className="fade-in">
      <Typography variant="h4" fontWeight="bold" gutterBottom>
        Settings
      </Typography>
      <Typography variant="subtitle1" color="text.secondary" sx={{ mb: 4 }}>
        Configure application preferences and account settings
      </Typography>

      <Grid container spacing={3}>
        {/* General Settings */}
        <Grid item xs={12} md={6}>
          <Card sx={{ height: "100%" }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                General Settings
              </Typography>
              <Divider sx={{ mb: 3 }} />

              {loading ? (
                <SettingsSkeleton />
              ) : (
                <List>
                  <ListItem>
                    <ListItemIcon>
                      <NotificationsIcon />
                    </ListItemIcon>
                    <ListItemText
                      primary="Notifications"
                      secondary="Enable push notifications for alerts and updates"
                    />
                    <ListItemSecondaryAction>
                      <Switch
                        edge="end"
                        name="notifications"
                        checked={settings.notifications}
                        onChange={handleSwitchChange}
                      />
                    </ListItemSecondaryAction>
                  </ListItem>

                  <ListItem>
                    <ListItemIcon>
                      <ThemeIcon />
                    </ListItemIcon>
                    <ListItemText
                      primary="Dark Mode"
                      secondary="Switch between light and dark theme"
                    />
                    <ListItemSecondaryAction>
                      <Switch
                        edge="end"
                        name="darkMode"
                        checked={settings.darkMode}
                        onChange={handleSwitchChange}
                      />
                    </ListItemSecondaryAction>
                  </ListItem>

                  <ListItem>
                    <ListItemIcon>
                      <LanguageIcon />
                    </ListItemIcon>
                    <ListItemText
                      primary="Language"
                      secondary="Select your preferred language"
                    />
                    <ListItemSecondaryAction>
                      <TextField
                        select
                        name="language"
                        value={settings.language}
                        onChange={handleInputChange}
                        SelectProps={{
                          native: true,
                        }}
                        variant="outlined"
                        size="small"
                        sx={{ width: 100 }}
                      >
                        <option value="en">English</option>
                        <option value="es">Spanish</option>
                        <option value="fr">French</option>
                        <option value="de">German</option>
                      </TextField>
                    </ListItemSecondaryAction>
                  </ListItem>

                  <ListItem>
                    <ListItemIcon>
                      <RefreshIcon />
                    </ListItemIcon>
                    <ListItemText
                      primary="Auto Refresh"
                      secondary="Automatically refresh data every minute"
                    />
                    <ListItemSecondaryAction>
                      <Switch
                        edge="end"
                        name="autoRefresh"
                        checked={settings.autoRefresh}
                        onChange={handleSwitchChange}
                      />
                    </ListItemSecondaryAction>
                  </ListItem>
                </List>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Data & Security */}
        <Grid item xs={12} md={6}>
          <Card sx={{ height: "100%" }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Data & Security
              </Typography>
              <Divider sx={{ mb: 3 }} />

              {loading ? (
                <SettingsSkeleton />
              ) : (
                <>
                  <List>
                    <ListItem>
                      <ListItemIcon>
                        <StorageIcon />
                      </ListItemIcon>
                      <ListItemText
                        primary="Data Retention"
                        secondary="Number of days to keep historical data"
                      />
                      <ListItemSecondaryAction>
                        <TextField
                          name="dataRetention"
                          value={settings.dataRetention}
                          onChange={handleInputChange}
                          type="number"
                          variant="outlined"
                          size="small"
                          sx={{ width: 100 }}
                          InputProps={{
                            endAdornment: (
                              <Typography variant="caption">days</Typography>
                            ),
                          }}
                        />
                      </ListItemSecondaryAction>
                    </ListItem>

                    <ListItem>
                      <ListItemIcon>
                        <SecurityIcon />
                      </ListItemIcon>
                      <ListItemText
                        primary="API Key"
                        secondary="Your secret API key for accessing the Fluxora API"
                      />
                      <ListItemSecondaryAction>
                        <IconButton
                          edge="end"
                          aria-label="regenerate"
                          onClick={handleResetApiKey}
                          color="primary"
                        >
                          <RefreshIcon />
                        </IconButton>
                      </ListItemSecondaryAction>
                    </ListItem>

                    <ListItem>
                      <TextField
                        fullWidth
                        name="apiKey"
                        value={settings.apiKey}
                        onChange={handleInputChange}
                        variant="outlined"
                        size="small"
                        type="password"
                        InputProps={{
                          readOnly: true,
                        }}
                      />
                    </ListItem>

                    <ListItem>
                      <Alert severity="warning" sx={{ width: "100%" }}>
                        Regenerating your API key will invalidate the previous
                        key immediately.
                      </Alert>
                    </ListItem>
                  </List>

                  <Box sx={{ mt: 3 }}>
                    <Button
                      variant="outlined"
                      color="error"
                      startIcon={<DeleteIcon />}
                      sx={{ mr: 2 }}
                    >
                      Clear All Data
                    </Button>

                    <Button
                      variant="contained"
                      color="primary"
                      startIcon={<SaveIcon />}
                      onClick={handleSaveSettings}
                    >
                      Save Settings
                    </Button>
                  </Box>
                </>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
        anchorOrigin={{ vertical: "bottom", horizontal: "right" }}
      >
        <Alert
          onClose={handleCloseSnackbar}
          severity={snackbar.severity}
          sx={{ width: "100%" }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default Settings;
