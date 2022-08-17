#include <SPI.h>
#include <RF24_config.h>
#include <nRF24L01.h>
#include <RF24.h>
#include "GyverStepper.h"


const uint64_t pipe = 0xF1F1F1F1F1LL;
RF24 radio(9, 10); // CE, CSN

#define DATA_SIZE 40
byte data[DATA_SIZE];
int int_data[DATA_SIZE / 2];
byte sendData[DATA_SIZE];
volatile byte counter = 0;
volatile byte in_byte = 0;
volatile byte spiTranferEnd = 0;
volatile byte spiTranferStarted = 0;
GStepper< STEPPER2WIRE> stepperLeft(800, 2, 3, 4);
GStepper< STEPPER2WIRE> stepperRight(800, 5, 6, 7);
int right_moving = 0, left_moving = 0;
void fillSendData() {
  for (byte i = 0; i < 40; i++) {
    sendData[i] = i;
  }
}

void setup() {
  Serial.begin(9600);
  pinMode(MISO, OUTPUT);
  SPCR |= _BV(SPE);
  SPI.attachInterrupt();
  fillSendData();
  stepperLeft.setRunMode(FOLLOW_POS);
  stepperRight.setRunMode(FOLLOW_POS);
  stepperLeft.setMaxSpeed(1000);
  stepperRight.setMaxSpeed(1000);
  stepperLeft.setAcceleration(300);
  stepperRight.setAcceleration(300);
  stepperLeft.autoPower(1);
  stepperRight.autoPower(1);
  stepperRight.setTarget(100, RELATIVE);
  stepperLeft.setTarget(100, RELATIVE);
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
void sendNRF(){
  SPI.detachInterrupt();
  delay(2);
  radio.begin();
  delay(2);
  byte _[9];
  radio.setChannel(100);
  radio.setDataRate(RF24_1MBPS);
  radio.setPALevel(RF24_PA_HIGH);
  radio.setAutoAck(1);
  radio.stopListening();
  radio.openWritingPipe(pipe);
  _[0] = 1;
  radio.write(&_, sizeof(_));
  SPCR |= _BV(SPE);
  pinMode(10,INPUT);
  pinMode(11,INPUT);
  pinMode(12,OUTPUT);
  pinMode(13,INPUT);
  SPI.attachInterrupt();
}

void loop () {
  sendData[0] = stepperLeft.tick();
  sendData[1] = stepperRight.tick();
  if (spiTranferEnd) {
    joinRecievedBytes();
    switch(int_data[0]){
      case 0:
        break;
      case 1:
        stepperLeft.setMaxSpeed(int_data[1]);
        stepperRight.setMaxSpeed(int_data[4]);
        stepperLeft.setAcceleration(int_data[2]);
        stepperRight.setAcceleration(int_data[5]);
        stepperLeft.setTarget(int_data[3], RELATIVE);
        stepperRight.setTarget(int_data[6], RELATIVE);      
        break;
    }
  }
}
