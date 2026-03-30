import { DarkTheme, DefaultTheme } from "react-native-paper";

/**
 * Light theme configuration
 */
export const lightTheme = {
  ...DefaultTheme,
  colors: {
    ...DefaultTheme.colors,
    primary: "#1976D2",
    accent: "#FFC107",
    background: "#F5F5F5",
    surface: "#FFFFFF",
    text: "#212121",
    error: "#D32F2F",
    success: "#388E3C",
    warning: "#F57C00",
    info: "#0288D1",
    disabled: "#9E9E9E",
    placeholder: "#757575",
    backdrop: "#00000080",
  },
  fonts: {
    ...DefaultTheme.fonts,
  },
  roundness: 8,
};

/**
 * Dark theme configuration
 */
export const darkTheme = {
  ...DarkTheme,
  colors: {
    ...DarkTheme.colors,
    primary: "#64B5F6",
    accent: "#FFD54F",
    background: "#121212",
    surface: "#1E1E1E",
    text: "#FFFFFF",
    error: "#EF5350",
    success: "#66BB6A",
    warning: "#FFA726",
    info: "#29B6F6",
    disabled: "#757575",
    placeholder: "#9E9E9E",
    backdrop: "#00000080",
  },
  fonts: {
    ...DarkTheme.fonts,
  },
  roundness: 8,
};

/**
 * Common spacing values
 */
export const spacing = {
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
  xxl: 48,
};

/**
 * Common font sizes
 */
export const fontSize = {
  xs: 10,
  sm: 12,
  md: 14,
  lg: 16,
  xl: 20,
  xxl: 24,
  xxxl: 32,
};

/**
 * Common shadow styles
 */
export const shadows = {
  small: {
    shadowColor: "#000",
    shadowOffset: {
      width: 0,
      height: 1,
    },
    shadowOpacity: 0.18,
    shadowRadius: 1.0,
    elevation: 1,
  },
  medium: {
    shadowColor: "#000",
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.23,
    shadowRadius: 2.62,
    elevation: 3,
  },
  large: {
    shadowColor: "#000",
    shadowOffset: {
      width: 0,
      height: 4,
    },
    shadowOpacity: 0.3,
    shadowRadius: 4.65,
    elevation: 6,
  },
};

export default {
  lightTheme,
  darkTheme,
  spacing,
  fontSize,
  shadows,
};
