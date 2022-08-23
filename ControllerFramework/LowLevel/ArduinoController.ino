#include <SPI.h>
#include <RF24_config.h>
#include <nRF24L01.h>
#include <RF24.h>
#include "GyverStepper.h"
#include <Servo.h>

Servo servo_0;

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
GStepper< STEPPER2WIRE> stepper1(800, 9, 8, 11);
GStepper< STEPPER2WIRE> stepper2(800, 7, 6, 11);
GStepper< STEPPER2WIRE> stepper3(800, 5, 4, 10);
GStepper< STEPPER2WIRE> stepper4(800, 3, 2, 10);
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
  stepper1.setRunMode(FOLLOW_POS);
  stepper2.setRunMode(FOLLOW_POS);
  stepper3.setRunMode(FOLLOW_POS);
  stepper4.setRunMode(FOLLOW_POS);
  stepper1.setMaxSpeed(1000);
  stepper2.setMaxSpeed(1000);
  stepper3.setMaxSpeed(1000);
  stepper4.setMaxSpeed(1000);
  stepper1.setAcceleration(300);
  stepper2.setAcceleration(300);
  stepper3.setAcceleration(300);
  stepper4.setAcceleration(300);
  stepper1.autoPower(1);
  stepper2.autoPower(1);
  stepper3.autoPower(1);
  stepper4.autoPower(1);
  stepper1.setTarget(10000, RELATIVE);
  stepper2.setTarget(10000, RELATIVE);
  stepper3.setTarget(10000, RELATIVE);
  stepper4.setTarget(10000, RELATIVE);
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
  sendData[0] = stepper1.tick();
  sendData[1] = stepper2.tick();
  sendData[2] = stepper3.tick();
  sendData[3] = stepper4.tick();
  if (spiTranferEnd) {
    joinRecievedBytes();
    switch(int_data[0]){
      case 0:
        break;
      case 1:
        stepper1.setMaxSpeed(int_data[1]);
        stepper2.setMaxSpeed(int_data[2]);
        stepper3.setMaxSpeed(int_data[3]);
        stepper4.setMaxSpeed(int_data[4]);
        stepper1.setAcceleration(int_data[5]);
        stepper2.setAcceleration(int_data[6]);
        stepper3.setAcceleration(int_data[7]);
        stepper4.setAcceleration(int_data[8]);
        stepper1.setTarget(int_data[9], RELATIVE);
        stepper2.setTarget(int_data[10], RELATIVE);      
        stepper3.setTarget(int_data[11], RELATIVE);
        stepper4.setTarget(int_data[12], RELATIVE);
        break;
      // case 2:
              
    }
  }
}
