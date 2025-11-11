#include <WiFi.h>
#include <PubSubClient.h>
#include <DHT.h>
#include <ArduinoJson.h>

// Konfigurasi WiFi
const char* ssid = "Wokwi-GUEST";
const char* password = "";

// Konfigurasi MQTT
const char* mqtt_server = "test.mosquitto.org";
const int mqtt_port = 1883;
const char* mqtt_topic_data = "iot/sensor/data";
const char* mqtt_topic_relay = "iot/relay/control";

// Pin Configuration
#define DHT_PIN 4
#define DHT_TYPE DHT22
#define LDR_PIN 34
#define RELAY_PIN 2
#define LED_PIN 5

// Sensor Objects
DHT dht(DHT_PIN, DHT_TYPE);

// WiFi dan MQTT Clients
WiFiClient espClient;
PubSubClient client(espClient);

// Variabel untuk timing
unsigned long lastMsg = 0;
const long interval = 5000; // Kirim data setiap 5 detik

// Variabel sensor
float temperature = 0;
float humidity = 0;
int lightLevel = 0;
bool relayState = false;

void setup() {
  Serial.begin(115200);
  
  // Inisialisasi pin
  pinMode(RELAY_PIN, OUTPUT);
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(RELAY_PIN, LOW);
  digitalWrite(LED_PIN, LOW);
  
  // Inisialisasi sensor DHT
  dht.begin();
  
  // Koneksi WiFi
  setup_wifi();
  
  // Setup MQTT
  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(callback);
  
  Serial.println("ESP32 IoT Project Started!");
  Serial.println("Sensors: DHT22, LDR");
  Serial.println("Actuators: Relay, LED");
}

void setup_wifi() {
  delay(10);
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  randomSeed(micros());

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}

void callback(char* topic, byte* payload, unsigned int length) {
  Serial.print("Message arrived [");
  Serial.print(topic);
  Serial.print("] ");
  
  String message;
  for (int i = 0; i < length; i++) {
    message += (char)payload[i];
  }
  Serial.println(message);

  // Parse JSON untuk kontrol relay
  if (String(topic) == mqtt_topic_relay) {
    DynamicJsonDocument doc(1024);
    deserializeJson(doc, message);
    
    String relayCommand = doc["relay"];
    
    if (relayCommand == "ON") {
      digitalWrite(RELAY_PIN, HIGH);
      digitalWrite(LED_PIN, HIGH);
      relayState = true;
      Serial.println("Relay and LED turned ON");
    } else if (relayCommand == "OFF") {
      digitalWrite(RELAY_PIN, LOW);
      digitalWrite(LED_PIN, LOW);
      relayState = false;
      Serial.println("Relay and LED turned OFF");
    }
  }
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    
    String clientId = "ESP32Client-";
    clientId += String(random(0xffff), HEX);
    
    if (client.connect(clientId.c_str())) {
      Serial.println("connected");
      client.subscribe(mqtt_topic_relay);
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      delay(5000);
    }
  }
}

void readSensors() {
  // Baca DHT22
  humidity = dht.readHumidity();
  temperature = dht.readTemperature();
  
  // Baca LDR
  int analogValue = analogRead(LDR_PIN);
  lightLevel = map(analogValue, 0, 4095, 0, 1000);
  
  // Cek apakah pembacaan DHT valid
  if (isnan(humidity) || isnan(temperature)) {
    Serial.println("Failed to read from DHT sensor!");
    // Set nilai default jika sensor error
    temperature = 25.0;
    humidity = 50.0;
  }
  
  // Print ke Serial Monitor
  Serial.println("=== Sensor Readings ===");
  Serial.print("Temperature: ");
  Serial.print(temperature);
  Serial.println(" °C");
  Serial.print("Humidity: ");
  Serial.print(humidity);
  Serial.println(" %");
  Serial.print("Light Level: ");
  Serial.print(lightLevel);
  Serial.println(" Lux");
  Serial.print("Relay State: ");
  Serial.println(relayState ? "ON" : "OFF");
  Serial.println("========================");
}

void publishSensorData() {
  // Buat JSON object
  DynamicJsonDocument doc(1024);
  doc["suhu"] = temperature;
  doc["humidity"] = humidity;
  doc["lux"] = lightLevel;
  doc["relay_state"] = relayState;
  doc["device_id"] = "ESP32_01";
  
  String jsonString;
  serializeJson(doc, jsonString);
  
  // Publish ke MQTT
  if (client.publish(mqtt_topic_data, jsonString.c_str())) {
    Serial.println("Data published successfully");
    Serial.println("Published: " + jsonString);
  } else {
    Serial.println("Failed to publish data");
  }
}

void loop() {
  // Cek koneksi MQTT
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  // Kirim data sensor setiap interval yang ditentukan
  unsigned long now = millis();
  if (now - lastMsg > interval) {
    lastMsg = now;
    
    readSensors();
    publishSensorData();
  }
  
  delay(100); // Small delay untuk stabilitas
}
