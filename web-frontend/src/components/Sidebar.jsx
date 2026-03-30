import {
  BarChart as BarChartIcon,
  Dashboard as DashboardIcon,
  BoltOutlined as EnergyIcon,
  Settings as SettingsIcon,
  Timeline as TimelineIcon,
} from "@mui/icons-material";
import {
  Box,
  Divider,
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Toolbar,
  Typography,
  useTheme,
} from "@mui/material";
import { useLocation, useNavigate } from "react-router-dom";

const drawerWidth = 240;

const menuItems = [
  { text: "Dashboard", icon: <DashboardIcon />, path: "/" },
  { text: "Predictions", icon: <TimelineIcon />, path: "/predictions" },
  { text: "Analytics", icon: <BarChartIcon />, path: "/analytics" },
  { text: "Settings", icon: <SettingsIcon />, path: "/settings" },
];

const Sidebar = ({ mobileOpen, handleDrawerToggle, isMobile }) => {
  const theme = useTheme();
  const location = useLocation();
  const navigate = useNavigate();

  const drawer = (
    <>
      <Toolbar
        sx={{
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          backgroundColor: theme.palette.primary.main,
          color: "white",
        }}
      >
        <EnergyIcon sx={{ mr: 1 }} />
        <Typography variant="h6" noWrap component="div" fontWeight="bold">
          FLUXORA
        </Typography>
      </Toolbar>
      <Divider />
      <List sx={{ mt: 2 }}>
        {menuItems.map((item) => (
          <ListItem
            button
            key={item.text}
            onClick={() => navigate(item.path)}
            sx={{
              mb: 1,
              mx: 1,
              borderRadius: 2,
              backgroundColor:
                location.pathname === item.path
                  ? `${theme.palette.primary.light}20`
                  : "transparent",
              color:
                location.pathname === item.path
                  ? theme.palette.primary.main
                  : theme.palette.text.primary,
              "&:hover": {
                backgroundColor: `${theme.palette.primary.light}10`,
              },
            }}
          >
            <ListItemIcon
              sx={{
                color:
                  location.pathname === item.path
                    ? theme.palette.primary.main
                    : theme.palette.text.primary,
              }}
            >
              {item.icon}
            </ListItemIcon>
            <ListItemText primary={item.text} />
          </ListItem>
        ))}
      </List>
      <Box sx={{ flexGrow: 1 }} />
      <Box sx={{ p: 2, mt: "auto" }}>
        <Typography variant="caption" color="text.secondary">
          Fluxora v1.0.0
        </Typography>
      </Box>
    </>
  );

  return (
    <Box
      component="nav"
      sx={{ width: { sm: drawerWidth }, flexShrink: { sm: 0 } }}
    >
      {/* Mobile drawer */}
      <Drawer
        variant="temporary"
        open={mobileOpen}
        onClose={handleDrawerToggle}
        ModalProps={{
          keepMounted: true, // Better open performance on mobile
        }}
        sx={{
          display: { xs: "block", sm: "none" },
          "& .MuiDrawer-paper": {
            boxSizing: "border-box",
            width: drawerWidth,
            boxShadow: 3,
          },
        }}
      >
        {drawer}
      </Drawer>

      {/* Desktop drawer */}
      <Drawer
        variant="permanent"
        sx={{
          display: { xs: "none", sm: "block" },
          "& .MuiDrawer-paper": {
            boxSizing: "border-box",
            width: drawerWidth,
            boxShadow: 3,
            border: "none",
          },
        }}
        open
      >
        {drawer}
      </Drawer>
    </Box>
  );
};

export default Sidebar;
