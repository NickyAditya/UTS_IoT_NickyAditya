#include <DHT.h>

#define DHT_PIN 8
#define LED_HIJAU 5
#define LED_KUNING 10
#define LED_MERAH 12
#define RELAY_POMPA 7
#define BUZZER 9

// DHT sensor setup
#define DHT_TYPE DHT22
DHT dht(DHT_PIN, DHT_TYPE);

void setup() {
  Serial.begin(9600);
  Serial.println("=== Sistem Hidroponik IoT ===");
  
  // Initialize DHT sensor
  dht.begin();
  
  // Set pin modes
  pinMode(LED_GREEN, OUTPUT);
  pinMode(LED_YELLOW, OUTPUT);
  pinMode(LED_RED, OUTPUT);
  pinMode(RELAY_PUMP, OUTPUT);
  pinMode(BUZZER, OUTPUT);
  
  // Turn off all outputs initially
  digitalWrite(LED_GREEN, LOW);
  digitalWrite(LED_YELLOW, LOW);
  digitalWrite(LED_RED, LOW);
  digitalWrite(RELAY_PUMP, LOW);
  digitalWrite(BUZZER, LOW);
  
  Serial.println("System Ready!");
  delay(2000); // Give DHT time to stabilize
}

void loop() {
  // Read temperature and humidity
  float humidity = dht.readHumidity();
  float temperature = dht.readTemperature();
  
  // Check if any reads failed
  if (isnan(humidity) || isnan(temperature)) {
    Serial.println("ERROR: Failed to read from DHT sensor!");
    // Blink red LED to indicate error
    digitalWrite(LED_RED, HIGH);
    delay(500);
    digitalWrite(LED_RED, LOW);
    delay(500);
    return;
  }
  
  // Display readings
  Serial.print("Temp: ");
  Serial.print(temperature, 1);
  Serial.print("°C | Humidity: ");
  Serial.print(humidity, 1);
  Serial.print("% | ");
  
  // Turn off all LEDs and buzzer first
  digitalWrite(LED_GREEN, LOW);
  digitalWrite(LED_YELLOW, LOW);
  digitalWrite(LED_RED, LOW);
  digitalWrite(BUZZER, LOW);
  
  // Temperature control logic
  if (temperature > 35.0) {
    // OVERHEATING: Red LED + Buzzer
    digitalWrite(LED_RED, HIGH);
    digitalWrite(BUZZER, HIGH);
    Serial.print("Status: OVERHEATING!");
  }
  else if (temperature >= 30.0 && temperature <= 35.0) {
    // WARM: Yellow LED
    digitalWrite(LED_YELLOW, HIGH);
    Serial.print("Status: WARM");
  }
  else {
    // COOL: Green LED
    digitalWrite(LED_GREEN, HIGH);
    Serial.print("Status: COOL");
  }
  
  // Pump control based on humidity
  if (humidity < 60.0) {
    digitalWrite(RELAY_PUMP, HIGH);
    Serial.println(" | Pump: ON");
  } else {
    digitalWrite(RELAY_PUMP, LOW);
    Serial.println(" | Pump: OFF");
  }
  
  Serial.println("---");
  delay(2000);
}