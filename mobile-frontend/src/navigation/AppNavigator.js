import { createDrawerNavigator } from "@react-navigation/drawer";
import AnalyticsScreen from "../screens/AnalyticsScreen";
import DashboardScreen from "../screens/DashboardScreen";
import PredictionsScreen from "../screens/PredictionsScreen";
import SettingsScreen from "../screens/SettingsScreen";

const Drawer = createDrawerNavigator();

const AppNavigator = () => {
  return (
    <Drawer.Navigator initialRouteName="Dashboard">
      <Drawer.Screen name="Dashboard" component={DashboardScreen} />
      <Drawer.Screen name="Analytics" component={AnalyticsScreen} />
      <Drawer.Screen name="Predictions" component={PredictionsScreen} />
      <Drawer.Screen name="Settings" component={SettingsScreen} />
    </Drawer.Navigator>
  );
};

export default AppNavigator;
