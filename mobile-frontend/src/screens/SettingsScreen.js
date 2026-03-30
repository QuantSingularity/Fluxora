import AsyncStorage from "@react-native-async-storage/async-storage";
import { useEffect, useState } from "react";
import { Alert, ScrollView, StyleSheet, View } from "react-native";
import {
  Appbar,
  Button,
  Card,
  Dialog,
  Divider,
  List,
  Paragraph,
  Portal,
  Switch,
  TextInput,
  Title,
  useTheme,
} from "react-native-paper";
import { APP_CONFIG } from "../constants/config";
import { useAuth } from "../contexts/AuthContext";

const SettingsScreen = ({ navigation }) => {
  const theme = useTheme();
  const { user, logout } = useAuth();
  const [notificationsEnabled, setNotificationsEnabled] = useState(false);
  const [darkModeEnabled, setDarkModeEnabled] = useState(false);
  const [profileDialogVisible, setProfileDialogVisible] = useState(false);
  const [logoutDialogVisible, setLogoutDialogVisible] = useState(false);
  const [username, setUsername] = useState(user?.username || "");
  const [email, setEmail] = useState(user?.email || "");

  // Load settings from storage on mount
  useEffect(() => {
    loadSettings();
  }, [loadSettings]);

  const loadSettings = async () => {
    try {
      const notifications = await AsyncStorage.getItem("notificationsEnabled");
      const darkMode = await AsyncStorage.getItem("darkModeEnabled");

      if (notifications !== null) {
        setNotificationsEnabled(JSON.parse(notifications));
      }
      if (darkMode !== null) {
        setDarkModeEnabled(JSON.parse(darkMode));
      }
    } catch (error) {
      console.error("Failed to load settings:", error);
    }
  };

  const toggleNotifications = async () => {
    const newValue = !notificationsEnabled;
    setNotificationsEnabled(newValue);
    try {
      await AsyncStorage.setItem(
        "notificationsEnabled",
        JSON.stringify(newValue),
      );
      Alert.alert(
        "Notifications",
        `Notifications ${newValue ? "enabled" : "disabled"} successfully`,
      );
    } catch (error) {
      console.error("Failed to save notification setting:", error);
      // Revert on error
      setNotificationsEnabled(!newValue);
    }
  };

  const toggleDarkMode = async () => {
    const newValue = !darkModeEnabled;
    setDarkModeEnabled(newValue);
    try {
      await AsyncStorage.setItem("darkModeEnabled", JSON.stringify(newValue));
      Alert.alert(
        "Theme",
        `Dark mode ${newValue ? "enabled" : "disabled"}. Please restart the app for changes to take full effect.`,
      );
    } catch (error) {
      console.error("Failed to save dark mode setting:", error);
      // Revert on error
      setDarkModeEnabled(!newValue);
    }
  };

  const showProfileDialog = () => {
    setUsername(user?.username || "");
    setEmail(user?.email || "");
    setProfileDialogVisible(true);
  };

  const hideProfileDialog = () => {
    setProfileDialogVisible(false);
  };

  const saveProfile = async () => {
    if (!username.trim() || !email.trim()) {
      Alert.alert("Validation Error", "Username and email cannot be empty");
      return;
    }

    try {
      // In a real app, this would call an API to update the profile
      const updatedUser = { ...user, username, email };
      await AsyncStorage.setItem("user", JSON.stringify(updatedUser));

      Alert.alert("Success", "Profile updated successfully");
      hideProfileDialog();

      // In a real implementation, you would also update the auth context
      // For now, user needs to restart the app to see changes
    } catch (error) {
      console.error("Failed to update profile:", error);
      Alert.alert("Error", "Failed to update profile. Please try again.");
    }
  };

  const showLogoutDialog = () => {
    setLogoutDialogVisible(true);
  };

  const hideLogoutDialog = () => {
    setLogoutDialogVisible(false);
  };

  const handleLogout = async () => {
    try {
      await logout();
      hideLogoutDialog();
      // Navigation will be handled by auth state change
      Alert.alert("Success", "Logged out successfully");
    } catch (error) {
      console.error("Logout failed:", error);
      Alert.alert("Error", "Failed to logout. Please try again.");
    }
  };

  const clearCache = async () => {
    Alert.alert(
      "Clear Cache",
      "Are you sure you want to clear all cached data?",
      [
        {
          text: "Cancel",
          style: "cancel",
        },
        {
          text: "Clear",
          style: "destructive",
          onPress: async () => {
            try {
              // Clear all cached data except user and settings
              const keys = await AsyncStorage.getAllKeys();
              const keysToRemove = keys.filter(
                (key) =>
                  ![
                    "user",
                    "token",
                    "notificationsEnabled",
                    "darkModeEnabled",
                  ].includes(key),
              );
              await AsyncStorage.multiRemove(keysToRemove);
              Alert.alert("Success", "Cache cleared successfully");
            } catch (error) {
              console.error("Failed to clear cache:", error);
              Alert.alert("Error", "Failed to clear cache");
            }
          },
        },
      ],
    );
  };

  return (
    <View style={styles.container}>
      <Appbar.Header>
        <Appbar.Content title="Settings" />
      </Appbar.Header>

      <ScrollView style={styles.content}>
        {/* Preferences Section */}
        <List.Section title="Preferences">
          <List.Item
            title="Enable Notifications"
            description="Receive alerts for predictions and anomalies"
            left={() => <List.Icon icon="bell" />}
            right={() => (
              <Switch
                value={notificationsEnabled}
                onValueChange={toggleNotifications}
                color={theme.colors.primary}
              />
            )}
          />
          <Divider />
          <List.Item
            title="Dark Mode"
            description="Apply dark theme across the app"
            left={() => <List.Icon icon="theme-light-dark" />}
            right={() => (
              <Switch
                value={darkModeEnabled}
                onValueChange={toggleDarkMode}
                color={theme.colors.primary}
              />
            )}
          />
        </List.Section>

        <Divider style={styles.divider} />

        {/* Account Section */}
        <List.Section title="Account">
          <List.Item
            title="Profile"
            description="View and edit your profile"
            left={() => <List.Icon icon="account-circle-outline" />}
            onPress={showProfileDialog}
          />
          <List.Item
            title="Change Password"
            description="Update your account password"
            left={() => <List.Icon icon="lock-outline" />}
            onPress={() =>
              Alert.alert(
                "Coming Soon",
                "Password change feature will be available soon",
              )
            }
          />
          <Divider />
          <List.Item
            title="Logout"
            description="Sign out from your account"
            left={() => <List.Icon icon="logout" color="red" />}
            onPress={showLogoutDialog}
            titleStyle={{ color: "red" }}
          />
        </List.Section>

        <Divider style={styles.divider} />

        {/* Data & Storage Section */}
        <List.Section title="Data & Storage">
          <List.Item
            title="Clear Cache"
            description="Free up space by clearing cached data"
            left={() => <List.Icon icon="delete-outline" />}
            onPress={clearCache}
          />
          <List.Item
            title="Data Usage"
            description="View app data consumption"
            left={() => <List.Icon icon="chart-arc" />}
            onPress={() =>
              Alert.alert(
                "Coming Soon",
                "Data usage statistics will be available soon",
              )
            }
          />
        </List.Section>

        <Divider style={styles.divider} />

        {/* About Section */}
        <Card style={styles.card}>
          <Card.Content>
            <Title>About Fluxora</Title>
            <Paragraph>Version: {APP_CONFIG.VERSION}</Paragraph>
            <Paragraph>
              Fluxora is an advanced energy forecasting and optimization
              platform that helps you monitor and manage energy consumption
              patterns.
            </Paragraph>
            <Paragraph style={styles.copyright}>
              © 2024 Fluxora. All rights reserved.
            </Paragraph>
          </Card.Content>
          <Card.Actions>
            <Button
              onPress={() =>
                Alert.alert(
                  "Terms",
                  "Terms of Service content will be displayed here",
                )
              }
            >
              Terms of Service
            </Button>
            <Button
              onPress={() =>
                Alert.alert(
                  "Privacy",
                  "Privacy Policy content will be displayed here",
                )
              }
            >
              Privacy Policy
            </Button>
          </Card.Actions>
        </Card>
      </ScrollView>

      {/* Profile Dialog */}
      <Portal>
        <Dialog visible={profileDialogVisible} onDismiss={hideProfileDialog}>
          <Dialog.Title>Edit Profile</Dialog.Title>
          <Dialog.Content>
            <TextInput
              label="Username"
              value={username}
              onChangeText={setUsername}
              mode="outlined"
              style={styles.input}
            />
            <TextInput
              label="Email"
              value={email}
              onChangeText={setEmail}
              mode="outlined"
              keyboardType="email-address"
              autoCapitalize="none"
              style={styles.input}
            />
          </Dialog.Content>
          <Dialog.Actions>
            <Button onPress={hideProfileDialog}>Cancel</Button>
            <Button onPress={saveProfile}>Save</Button>
          </Dialog.Actions>
        </Dialog>

        {/* Logout Confirmation Dialog */}
        <Dialog visible={logoutDialogVisible} onDismiss={hideLogoutDialog}>
          <Dialog.Title>Confirm Logout</Dialog.Title>
          <Dialog.Content>
            <Paragraph>Are you sure you want to log out?</Paragraph>
          </Dialog.Content>
          <Dialog.Actions>
            <Button onPress={hideLogoutDialog}>Cancel</Button>
            <Button onPress={handleLogout} textColor="red">
              Logout
            </Button>
          </Dialog.Actions>
        </Dialog>
      </Portal>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#f5f5f5",
  },
  content: {
    flex: 1,
  },
  divider: {
    marginVertical: 10,
  },
  card: {
    margin: 15,
    elevation: 3,
  },
  input: {
    marginBottom: 15,
  },
  copyright: {
    marginTop: 10,
    fontSize: 12,
    color: "#999",
  },
});

export default SettingsScreen;
