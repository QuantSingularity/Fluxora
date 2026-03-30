import { NavigationContainer } from "@react-navigation/native";
import { Provider as PaperProvider } from "react-native-paper"; // Import PaperProvider
import AppNavigator from "./src/navigation/AppNavigator";
import "react-native-gesture-handler";

// Optional: Define a custom theme
// import { DefaultTheme } from 'react-native-paper';
// const theme = {
//   ...DefaultTheme,
//   colors: {
//     ...DefaultTheme.colors,
//     primary: 'tomato',
//     accent: 'yellow',
//   },
// };

export default function App() {
  return (
    // Wrap the entire app in PaperProvider
    <PaperProvider>
      <NavigationContainer>
        <AppNavigator />
      </NavigationContainer>
    </PaperProvider>
  );
}
