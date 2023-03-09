#include <WiFi.h>
#include <PubSubClient.h>
#include "ICM_20948.h"

// IMU DECLARATIONS
//#define USE_SPI
#define SERIAL_PORT Serial

#define SPI_PORT SPI
#define CS_PIN 2 

#define WIRE_PORT Wire
#define AD0_VAL 1

#ifdef USE_SPI
ICM_20948_SPI myICM;
#else
ICM_20948_I2C myICM;
#endif
// END IMU DECLARATIONS

// MQTT DECLARATIONS
const char *ssid =  "ITSMONDAYWIPE";   // name of your WiFi network
const char *password =  "sharpantsnow"; // password of the WiFi network

const char *ID = "player1";  // Name of our device, must be unique
const char *TOPIC = "team6";  // Topic to subcribe to

IPAddress broker(192,168,0,113); // IP address of your MQTT broker eg. 192.168.1.50
WiFiClient wclient;

PubSubClient client(wclient); // Setup MQTT client
bool state=0;
//END MQTT DECLARATIONS

// setup_wifi(): connects to wifi network, retries if it doesn't work until it does.
void setup_wifi(){
  WiFi.begin(ssid, password);
  while(WiFi.status() != WL_CONNECTED){
    delay(500);
    Serial.print(".");
  }

  Serial.println("WiFi Connected");
  Serial.println(WiFi.localIP());
}


// reconnect(): if we lose wifi, reconnect until we start again.
void reconnect(){
  while(!client.connected()){
    Serial.print("Attempting Connection...");
    if(client.connect(ID)){
      Serial.print(TOPIC);
    } else {
      Serial.println("Trying again in 3 sec");
      delay(3000);
    }
  }
}

void setup() {
  SERIAL_PORT.begin(115200);
  while(!SERIAL_PORT){};

  // WIFI SETUP
  delay(100);
  setup_wifi();
  client.setServer(broker, 1883);
  delay(100);

  //IMU SETUP
  #ifdef USE_SPI
    SPI_PORT.begin();
  #else
    WIRE_PORT.begin();
    WIRE_PORT.setClock(400000);
  #endif
  bool initialized = false;
  while(!initialized){  
    #ifdef USE_SPI
      myICM.begin(CS_PIN, SPI_PORT);
    #else
      myICM.begin(WIRE_PORT, AD0_VAL);
    #endif

    SERIAL_PORT.print(F("Initialization of the sensor returned: "));
    SERIAL_PORT.println(myICM.statusString());
    if (myICM.status != ICM_20948_Stat_Ok){
      SERIAL_PORT.println("Trying again...");
      delay(500);
    } else {
      initialized = true;
    }
  }
}

void loop() {
  if (!client.connected()){
    reconnect();
  }
  client.loop();

  if(myICM.dataReady())
  {
    myICM.getAGMT();
    int dat = printScaledAGMT(&myICM);
    if(dat == 0) client.publish(TOPIC, "LEFT");
    if(dat == 1) client.publish(TOPIC, "RIGHT");
    delay(30);
  }
  else
  {
    SERIAL_PORT.println("waiting for data");
    delay(30);
  }

}

// 0 -> left, 1 -> right
int getDir(float accX){
  if(accX > 0) return 0;
  else return 1;
}

#ifdef USE_SPI
int printScaledAGMT(ICM_20948_SPI *sensor)
{
#else
int printScaledAGMT(ICM_20948_I2C *sensor)
{
#endif
  return getDir(sensor->accX());
}







































