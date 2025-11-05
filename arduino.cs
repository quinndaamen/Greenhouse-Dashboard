#include <Adafruit_Sensor.h>
#include <DHT.h>
#include <DHT_U.h>
#include <math.h>

#define DHTPIN 12               
#define DHTTYPE DHT11           
#define LIGHTSENSOR_PIN A2
#define ORANGE 7
#define GREEN 5
#define RED 4

DHT_Unified dht(DHTPIN, DHTTYPE);
uint32_t delayMS;

const float uTemp = 23;
const float uHumidity = 75;

void setup() {
  Serial.begin(9600);
  dht.begin();

  sensor_t sensor;
  dht.temperature().getSensor(&sensor);
  delayMS = sensor.min_delay / 1000;

  pinMode(LIGHTSENSOR_PIN, INPUT);
  pinMode(RED, OUTPUT);
  pinMode(GREEN, OUTPUT);
  pinMode(ORANGE, OUTPUT);     
}

void loop() {
  delay(delayMS);

  sensors_event_t event;
  dht.temperature().getEvent(&event);
  float temp = isnan(event.temperature) ? -1 : event.temperature;
 
  dht.humidity().getEvent(&event);
  float hum = isnan(event.relative_humidity) ? -1 : event.relative_humidity;

  float Rsensor = getRes(); 
  float lux = 325 * pow(Rsensor, -1.4);

  Serial.print("Temp:");
  Serial.print(temp, 1);
  Serial.print(",Hum:");
  Serial.print(hum, 1);
  Serial.print(",Light:");
  Serial.println(lux, 1);

  // temp score
  int tempScore, humScore;

  if (temp >= uTemp * 0.9 && temp <= uTemp * 1.1)
      tempScore = 50;
  else if (temp >= uTemp * 0.875 && temp <= uTemp * 1.2)
      tempScore = 40;
  else if (temp >= uTemp * 0.85 && temp <= uTemp * 1.3)
      tempScore = 30;
  else if (temp >= uTemp * 0.825 && temp <= uTemp * 1.4)
      tempScore = 20;
  else
      tempScore = 0;

  // Hum score
  if (hum >= uHumidity * 0.9 && hum <= uHumidity * 1.1)
      humScore = 50;
  else if (hum >= uHumidity * 0.875 && hum <= uHumidity * 1.2)
      humScore = 40;
  else if (hum >= uHumidity * 0.85 && hum <= uHumidity * 1.3)
      humScore = 30;
  else if (hum >= uHumidity * 0.825 && hum <= uHumidity * 1.4)
      humScore = 20;
  else
      humScore = 0;

  // Score with LEDs
  int totalScore = tempScore + humScore;

  if (totalScore >= 80) { 
      digitalWrite(GREEN, HIGH);
      digitalWrite(ORANGE, LOW);
      digitalWrite(RED, LOW);
  } else if (totalScore >= 30) { 
      digitalWrite(GREEN, LOW);
      digitalWrite(ORANGE, HIGH);
      digitalWrite(RED, LOW);
  } else { // bad
      digitalWrite(GREEN, LOW);
      digitalWrite(ORANGE, LOW);
      digitalWrite(RED, HIGH);
  }

  delay(1000);
}

float getRes() {
  int sensorValue = analogRead(LIGHTSENSOR_PIN);
  if (sensorValue == 0) sensorValue = 1; 
  float Rsensor = (float)(1023 - sensorValue) * 10 / sensorValue;
  return Rsensor;  
}