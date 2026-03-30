import {
  AccountCircle,
  ExitToApp as LogoutIcon,
  Menu as MenuIcon,
  Notifications as NotificationsIcon,
  Search as SearchIcon,
  Settings as SettingsIcon,
} from "@mui/icons-material";
import {
  AppBar,
  Avatar,
  alpha,
  Badge,
  Box,
  IconButton,
  InputBase,
  Menu,
  MenuItem,
  Toolbar,
  Tooltip,
  Typography,
  useTheme,
} from "@mui/material";
import { useState } from "react";

const Header = ({ handleDrawerToggle }) => {
  const theme = useTheme();
  const [anchorEl, setAnchorEl] = useState(null);
  const [notificationsAnchorEl, setNotificationsAnchorEl] = useState(null);

  const handleProfileMenuOpen = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleNotificationsMenuOpen = (event) => {
    setNotificationsAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleNotificationsMenuClose = () => {
    setNotificationsAnchorEl(null);
  };

  return (
    <AppBar
      position="fixed"
      sx={{
        zIndex: theme.zIndex.drawer + 1,
        backgroundColor: "background.paper",
        color: "text.primary",
        boxShadow: "0px 2px 10px rgba(0, 0, 0, 0.05)",
      }}
    >
      <Toolbar>
        <IconButton
          color="inherit"
          aria-label="open drawer"
          edge="start"
          onClick={handleDrawerToggle}
          sx={{ mr: 2, display: { sm: "none" } }}
        >
          <MenuIcon />
        </IconButton>

        <Box
          sx={{
            position: "relative",
            borderRadius: 2,
            backgroundColor: alpha(theme.palette.common.black, 0.04),
            "&:hover": {
              backgroundColor: alpha(theme.palette.common.black, 0.08),
            },
            marginRight: 2,
            marginLeft: 0,
            width: "100%",
            maxWidth: "400px",
            [theme.breakpoints.up("sm")]: {
              marginLeft: 3,
              width: "auto",
            },
          }}
        >
          <Box
            sx={{
              padding: theme.spacing(0, 2),
              height: "100%",
              position: "absolute",
              pointerEvents: "none",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            <SearchIcon />
          </Box>
          <InputBase
            placeholder="Search…"
            sx={{
              color: "inherit",
              padding: theme.spacing(1, 1, 1, 0),
              paddingLeft: `calc(1em + ${theme.spacing(4)})`,
              transition: theme.transitions.create("width"),
              width: "100%",
              [theme.breakpoints.up("md")]: {
                width: "20ch",
              },
            }}
          />
        </Box>

        <Box sx={{ flexGrow: 1 }} />

        <Box sx={{ display: "flex", alignItems: "center" }}>
          <Tooltip title="Notifications">
            <IconButton color="inherit" onClick={handleNotificationsMenuOpen}>
              <Badge badgeContent={4} color="error">
                <NotificationsIcon />
              </Badge>
            </IconButton>
          </Tooltip>

          <Tooltip title="Account">
            <IconButton
              edge="end"
              aria-label="account of current user"
              aria-haspopup="true"
              onClick={handleProfileMenuOpen}
              color="inherit"
              sx={{ ml: 1 }}
            >
              <Avatar
                sx={{
                  width: 32,
                  height: 32,
                  backgroundColor: theme.palette.primary.main,
                }}
              >
                <AccountCircle />
              </Avatar>
            </IconButton>
          </Tooltip>
        </Box>
      </Toolbar>

      {/* Profile Menu */}
      <Menu
        anchorEl={anchorEl}
        anchorOrigin={{
          vertical: "bottom",
          horizontal: "right",
        }}
        keepMounted
        transformOrigin={{
          vertical: "top",
          horizontal: "right",
        }}
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
      >
        <Box sx={{ px: 2, py: 1 }}>
          <Typography variant="subtitle1" fontWeight="bold">
            Admin User
          </Typography>
          <Typography variant="body2" color="text.secondary">
            admin@fluxora.com
          </Typography>
        </Box>
        <MenuItem onClick={handleMenuClose}>
          <SettingsIcon fontSize="small" sx={{ mr: 1 }} />
          Settings
        </MenuItem>
        <MenuItem onClick={handleMenuClose}>
          <LogoutIcon fontSize="small" sx={{ mr: 1 }} />
          Logout
        </MenuItem>
      </Menu>

      {/* Notifications Menu */}
      <Menu
        anchorEl={notificationsAnchorEl}
        anchorOrigin={{
          vertical: "bottom",
          horizontal: "right",
        }}
        keepMounted
        transformOrigin={{
          vertical: "top",
          horizontal: "right",
        }}
        open={Boolean(notificationsAnchorEl)}
        onClose={handleNotificationsMenuClose}
      >
        <Box sx={{ px: 2, py: 1 }}>
          <Typography variant="subtitle1" fontWeight="bold">
            Notifications
          </Typography>
        </Box>
        <MenuItem onClick={handleNotificationsMenuClose}>
          <Typography variant="body2">
            Energy consumption spike detected
          </Typography>
        </MenuItem>
        <MenuItem onClick={handleNotificationsMenuClose}>
          <Typography variant="body2">
            New prediction model available
          </Typography>
        </MenuItem>
        <MenuItem onClick={handleNotificationsMenuClose}>
          <Typography variant="body2">System update completed</Typography>
        </MenuItem>
        <MenuItem onClick={handleNotificationsMenuClose}>
          <Typography variant="body2">Weekly report generated</Typography>
        </MenuItem>
      </Menu>
    </AppBar>
  );
};

export default Header;
