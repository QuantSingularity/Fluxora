import { useState } from "react";
import { ScrollView, StyleSheet, View } from "react-native";
import {
  ActivityIndicator,
  Appbar,
  Button,
  Card,
  Dialog,
  HelperText,
  Paragraph,
  Portal,
  TextInput,
  Title,
  useTheme,
} from "react-native-paper";
import { postPredictions } from "../api/api";

const PredictionsScreen = ({ navigation }) => {
  const theme = useTheme();
  const [timestampInput, setTimestampInput] = useState(
    new Date().toISOString(),
  );
  const [meterIdInput, setMeterIdInput] = useState("meter_123");
  const [contextInput, setContextInput] = useState("{}");
  const [contextError, setContextError] = useState(null);

  const [predictions, setPredictions] = useState(null);
  const [confidenceIntervals, setConfidenceIntervals] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [errorVisible, setErrorVisible] = useState(false);

  const hideErrorDialog = () => setErrorVisible(false);

  const validateContextJson = (text) => {
    setContextInput(text);
    try {
      JSON.parse(text);
      setContextError(null);
    } catch (_e) {
      setContextError("Invalid JSON format");
    }
  };

  const handlePredict = async () => {
    if (!timestampInput || !meterIdInput) {
      setError("Timestamp and Meter ID are required.");
      setErrorVisible(true);
      return;
    }

    let parsedContext;
    try {
      parsedContext = JSON.parse(contextInput);
      setContextError(null);
    } catch (_e) {
      setContextError("Invalid JSON format");
      setError("Context Features must be a valid JSON object.");
      setErrorVisible(true);
      return;
    }

    try {
      setLoading(true);
      setError(null);
      setErrorVisible(false);
      setPredictions(null);
      setConfidenceIntervals(null);

      const payload = {
        timestamps: [timestampInput],
        meter_ids: [meterIdInput],
        context_features: parsedContext,
      };

      console.log("Sending payload:", JSON.stringify(payload));
      const data = await postPredictions(payload);
      console.log("Received response:", data);

      setPredictions(data.predictions);
      setConfidenceIntervals(data.confidence_intervals);
    } catch (err) {
      console.error("Prediction API Call Failed:", err);
      let errorMessage =
        "Prediction failed. Please check the backend connection and input format.";
      if (err.response) {
        errorMessage += `\nDetails: ${JSON.stringify(err.response.data)}`;
      } else if (err.request) {
        errorMessage =
          "Prediction failed: No response received from the server. Is it running?";
      } else {
        errorMessage = `Prediction failed: ${err.message}`;
      }
      setError(errorMessage);
      setErrorVisible(true);
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <Appbar.Header>
        {/* <Appbar.BackAction onPress={() => navigation.goBack()} /> */}
        <Appbar.Content title="Energy Predictions" />
      </Appbar.Header>

      <ScrollView style={styles.content}>
        <Card style={styles.card}>
          <Card.Content>
            <Title>Input Parameters</Title>
            <TextInput
              label="Timestamp (ISO Format)"
              value={timestampInput}
              onChangeText={setTimestampInput}
              mode="outlined"
              style={styles.input}
            />
            <TextInput
              label="Meter ID"
              value={meterIdInput}
              onChangeText={setMeterIdInput}
              mode="outlined"
              style={styles.input}
            />
            <TextInput
              label="Context Features (JSON)"
              value={contextInput}
              onChangeText={validateContextJson}
              mode="outlined"
              style={styles.input}
              multiline
              numberOfLines={4}
              error={!!contextError}
            />
            <HelperText type="error" visible={!!contextError}>
              {contextError}
            </HelperText>
            <Button
              mode="contained"
              onPress={handlePredict}
              disabled={loading || !!contextError}
              loading={loading}
              style={styles.button}
              icon="send"
            >
              Get Predictions
            </Button>
          </Card.Content>
        </Card>

        {loading && (
          <ActivityIndicator
            animating={true}
            size="large"
            style={styles.loader}
            color={theme.colors.primary}
          />
        )}

        {predictions && (
          <Card style={styles.card}>
            <Card.Content>
              <Title>Prediction Results</Title>
              {predictions.map((pred, index) => (
                <View key={index} style={styles.predictionItem}>
                  <Paragraph>
                    Prediction:{" "}
                    <Text style={styles.predictionValue}>
                      {pred.toFixed(4)}
                    </Text>
                  </Paragraph>
                  {confidenceIntervals?.[index] && (
                    <Paragraph style={styles.confidenceText}>
                      (95% CI: {confidenceIntervals[index][0].toFixed(4)} -{" "}
                      {confidenceIntervals[index][1].toFixed(4)})
                    </Paragraph>
                  )}
                </View>
              ))}
            </Card.Content>
          </Card>
        )}
      </ScrollView>

      <Portal>
        <Dialog visible={errorVisible} onDismiss={hideErrorDialog}>
          <Dialog.Title>Prediction Error</Dialog.Title>
          <Dialog.Content>
            <Paragraph>{error}</Paragraph>
          </Dialog.Content>
          <Dialog.Actions>
            <Button onPress={hideErrorDialog}>OK</Button>
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
    padding: 15,
  },
  card: {
    marginBottom: 15,
    elevation: 3,
  },
  input: {
    marginBottom: 10,
  },
  button: {
    marginTop: 10,
  },
  loader: {
    marginVertical: 20,
  },
  predictionItem: {
    marginBottom: 10,
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: "#eee",
  },
  predictionValue: {
    fontWeight: "bold",
  },
  confidenceText: {
    fontSize: 12,
    color: "#666",
    marginTop: 2,
  },
});

export default PredictionsScreen;
