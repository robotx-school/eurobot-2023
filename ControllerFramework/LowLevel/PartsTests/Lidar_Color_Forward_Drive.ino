#include "TFLidar.h"
#include "GyverStepper.h"
#include <microLED.h>
#include <SPI.h>

#define COLOR_DEBTH 3
#define STRIP_PIN 22
#define NUMLEDS 2

microLED<NUMLEDS, STRIP_PIN, MLED_NO_CLOCK, LED_WS2818, ORDER_GRB, CLI_AVER> rgbLed;

TFLidar frontLidar;
TFLidar backLidar;

int frontDist;
int backDist;

GStepper< STEPPER2WIRE> stepperLeft(800, 48, 49, 45); //шаговНаОборот, step, dir, en);  
GStepper< STEPPER2WIRE> stepperRight(800, 46, 47, 45);
byte leftMoving;
byte rightMoving;

uint32_t distTimer=0;

#define DATA_SIZE 40
byte data[DATA_SIZE];
int int_data[DATA_SIZE / 2];
byte sendData[DATA_SIZE];
volatile byte counter = 0;
volatile byte in_byte = 0;
volatile byte spiTranferEnd = 0;
volatile byte spiTranferStarted = 0;

void fillSendData() {
  for (byte i = 1; i < 40; i++) {
    sendData[i] = i;
  }
}

void checkDist(){
  if (millis()-distTimer>50){
    frontLidar.getData(frontDist);
    backLidar.getData(backDist);
    rgbLed.set(0, mHSV(frontDist, 255, 255));
    rgbLed.set(1, mHSV(backDist, 255, 255));
    rgbLed.show();
    distTimer = millis();
  }
}
void setup() {
  rgbLed.setBrightness(120);
  Serial.begin(9600);
  Serial2.begin(115200);
  Serial3.begin(115200);
  delay(20);
  frontLidar.begin(&Serial2); 
  backLidar.begin(&Serial3);

  stepperLeft.setRunMode(FOLLOW_POS);
  stepperRight.setRunMode(FOLLOW_POS);
  stepperLeft.setMaxSpeed(1000);
  stepperRight.setMaxSpeed(1000);
  stepperLeft.setAcceleration(300);
  stepperRight.setAcceleration(300);
  stepperLeft.invertEn(1);
  stepperRight.invertEn(1);
  stepperRight.reverse(1);
  stepperLeft.autoPower(1);
  stepperRight.autoPower(1);
  stepperRight.setTarget(100, RELATIVE);
  stepperLeft.setTarget(100, RELATIVE);
  
  pinMode(MISO, OUTPUT);
  SPCR |= _BV(SPE);
  SPI.attachInterrupt();
  fillSendData();
}

ISR (SPI_STC_vect)
{
  in_byte = SPDR;
  if (in_byte == 240 and !spiTranferStarted) {
    spiTranferStarted = 1;
    counter = 0;
    SPDR = sendData[counter];
  }
  if (spiTranferStarted and counter > 0) {
    data[counter - 1] = in_byte;
    SPDR = sendData[counter];
  }
  counter++;

  if (counter == DATA_SIZE) {
    SPDR = sendData[counter - 1];
    counter = 0;
    spiTranferStarted = 0;
    spiTranferEnd = 1;
  }
}

void joinRecievedBytes() {
  for (int i = 0; i < DATA_SIZE; i += 2) {
    int_data[i / 2] = data[i] << 8 | data[i + 1];
  }
  spiTranferEnd = 0;
}
void printSpiData() {
  for (int i = 0; i < DATA_SIZE / 2; i++) {
    Serial.print(int_data[i]);
    Serial.print(" ");
  }
  Serial.println();

}


void loop() {
  leftMoving = stepperLeft.tick();
  rightMoving = stepperRight.tick();

  checkDist();
  
  sendData[0] = leftMoving;
  sendData[1] = rightMoving;
  
  if (spiTranferEnd) {
    joinRecievedBytes();
    if (int_data[0] == 1) { //установка новой цели для моторов
      printSpiData();
      if (int_data[1] and int_data[2] and int_data[3]) {
        stepperLeft.setMaxSpeed(int_data[1]);
        stepperLeft.setAcceleration(int_data[2]);
        stepperLeft.setTarget(int_data[3], RELATIVE);
      }
      if (int_data[4] and int_data[5] and int_data[6]) {
        stepperRight.setMaxSpeed(int_data[4]);
        stepperRight.setAcceleration(int_data[5]);
        stepperRight.setTarget(int_data[6], RELATIVE);
      }
    }
  }
}
