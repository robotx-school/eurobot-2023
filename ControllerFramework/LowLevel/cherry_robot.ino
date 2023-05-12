#include <SPI.h>
#include <RF24_config.h>
#include <nRF24L01.h>
#include <RF24.h>
#include "GyverStepper.h"
#include <Servo.h>
#include <microLED.h>

#define COLOR_DEBTH 3
#define STRIP_PIN 23
#define NUMLEDS 160

microLED<NUMLEDS, STRIP_PIN, MLED_NO_CLOCK, LED_WS2818, ORDER_GRB, CLI_AVER> trickLed;

Servo servo_0;
Servo servo_1;
Servo servo_2;
Servo servo_3;
Servo servo_4;
Servo servo_5;
Servo servo_6;
Servo servo_7;
Servo servo_8;
Servo servo_9;

Servo servo_array[10] = {servo_0, servo_1, servo_2, servo_3, servo_4, servo_5, servo_6, servo_7, servo_8, servo_9};

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
GStepper< STEPPER2WIRE> stepper1(800, 48, 49, 45);
GStepper< STEPPER2WIRE> stepper2(800, 46, 47, 45);
int servo_0_flex = 0;
Servo servos[25] = {};
int servo_speed[25] = {10, 50,100, 10,20, 30,40, 50,60, 70,80, 90,90, 70,60, 50,40, 30,20, 10,40, 50,60, 70, 0};
int servo_targets[25] = {0, 0,0, 0,0, 0,0, 0,0, 0,0, 0,0, 0,0, 0,0, 0,0, 0,0, 0,0, 0, 0}; //Цель
int servo_pos[25] = {0, 0,0, 0,0, 0,0, 0,0, 0,0, 0,0, 0,0, 0,0, 0,0, 0,0, 0,0, 0, 0};     //Тех
long servo_timers[25] = {0, 0,0, 0,0, 0,0, 0,0, 0,0, 0,0, 0,0, 0,0, 0,0, 0,0, 0,0, 0, 0};
int servo_0_target = 0;
long timer_0 = 0;
int right_moving = 0, left_moving = 0;
void fillSendData() {
  for (byte i = 0; i < 40; i++) {
    sendData[i] = i;
  }
}

void setup() {
  Serial.begin(9600);
  Serial.println(1234567890);
  pinMode(MISO, OUTPUT);
  SPCR |= _BV(SPE);
  SPI.attachInterrupt();
  fillSendData();
  stepper1.setRunMode(FOLLOW_POS);
  stepper2.setRunMode(FOLLOW_POS);
  
  stepper1.setMaxSpeed(1000);
  stepper2.setMaxSpeed(1000);
  stepper1.invertEn(1);
  stepper2.invertEn(1);
  stepper2.reverse(1);
  
  stepper1.setAcceleration(300);
  stepper2.setAcceleration(300);
  
  stepper1.autoPower(1);
  stepper2.autoPower(1);
  
 /* stepper1.setTarget(10000, RELATIVE);
  stepper2.setTarget(10000, RELATIVE);
  stepper3.setTarget(10000, RELATIVE);
  stepper4.setTarget(10000, RELATIVE); */
  timer_0 = millis();

  servo_0.attach(48);
  servo_1.attach(46);
  servo_2.attach(44);
  servo_3.attach(42);
  servo_4.attach(40);
  servo_5.attach(38);
  servo_6.attach(36);
  servo_7.attach(34);
  servo_8.attach(32);
  servo_9.attach(30);
  
  servo_0.write(0);
  servo_1.write(0);
  servo_2.write(0);
  servo_3.write(0);
  servo_4.write(0);
  servo_5.write(0);
  servo_6.write(0);
  servo_7.write(0);
  servo_8.write(0);
  servo_9.write(0); 

  // Init trcik-led to default green on start
  trickLed.fill(mGreen);
  trickLed.show();
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


void flexim(){
  for(int i=0; i <= 23;i++){
    if(millis() - servo_timers[i] >= servo_speed[i] and servo_pos[i] != servo_targets[i]){
      servo_timers[i] = millis();
      if(servo_targets[i] - servo_pos[i] > 0){
        servo_pos[i]++;
      }else{
        servo_pos[i]--;
      }
      servo_array[i].write(servo_pos[i]);
    }
  }
}

void loop () {
  flexim();
  //printSpiData();
  sendData[0] = stepper1.tick();
  sendData[1] = stepper2.tick();
  
  if (spiTranferEnd) {
    joinRecievedBytes();
    switch(int_data[0]){
      case 0:

        break;
      case 1:
        // Drive
        stepper1.setMaxSpeed(int_data[1]);
        stepper2.setMaxSpeed(int_data[4]);
        
        stepper1.setAcceleration(int_data[2]);
        stepper2.setAcceleration(int_data[5]);

        stepper1.setTarget(int_data[3], RELATIVE);
        stepper2.setTarget(int_data[6], RELATIVE);
        
        break;
     case 2:
        // Controll servo
        servo_targets[int_data[1]] = int_data[2];
        servo_speed[int_data[1]] = int_data[3];
        break;
     case 3:
        // Change pin mode for custom pin
        pinMode(int_data[1], int_data[2]);
        break;
     case 4:
        // Read data from custom pin
        sendData[4] = digitalRead(int_data[1]);
        break;
     case 5:
        // Write to custom pin
        //sendData[4] = digitalRead(int_data[1]);
        digitalWrite(int_data[1], int_data[2]);
        break;
      case 6:
        stepper1.brake();
        stepper2.brake();
        break;
      case 7:
        // Play trick
        trickLed.fill(mRGB(int_data[1], int_data[2], int_data[3]));
        trickLed.show();
        break;

    }
  }
}

