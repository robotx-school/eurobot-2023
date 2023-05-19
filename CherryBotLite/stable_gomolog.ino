/*
   Check README.md ; requirements.txt

   spilib_lite is a fork of spilib (see README.md ).

   This is an Arduino program for working
   with a script high_level.py by SPI (40/20 packets).

   Arduino SPI send data to Main SPI sendData
   sendData[0-3] : Stepper status
   sendData[4] : Digital read
   sendData[5] : Analog read
*/

#include <color_utility.h>
#include <microLED.h>
#include <SPI.h>
#include "GyverStepper.h"
#include "GyverTM1637.h"
#include <Servo.h>
#include "TFLidar.h"

#define DISP_CLK 21
#define DISP_DIO 20

#define STRIP_PIN 23
#define NUMLEDS 160
microLED<NUMLEDS, STRIP_PIN, MLED_NO_CLOCK, LED_WS2818, ORDER_GRB, CLI_AVER> strip;

#define ONE_STRIP_PIN 22
#define ONE_NUMLEDS 1
microLED<ONE_NUMLEDS, ONE_STRIP_PIN, MLED_NO_CLOCK, LED_WS2818, ORDER_GRB, CLI_AVER> one_strip;

TFLidar frontLidar;
TFLidar backLidar;
int frontDist;
int backDist;

#define CLK 21
#define DIO 20
GyverTM1637 disp(DISP_CLK, DISP_DIO);


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
bool WAITING = false;
bool LIDAR_SCANNED_CIRCLE = false; // start
int LIDAR_MIN_DIST_CIRCLE = 1000; 
int PENDING_STEPS = 0;
int PREDICTION_POINTS = 0;

#define DATA_SIZE 40
byte data[DATA_SIZE];
int int_data[DATA_SIZE / 2];
byte sendData[DATA_SIZE];

uint32_t distTimer = 0;
volatile byte counter = 0;
volatile byte in_byte = 0;
volatile byte spiTranferEnd = 0;
volatile byte spiTranferStarted = 0;

GStepper< STEPPER2WIRE> stepper1(800, 46, 47, 45);
GStepper< STEPPER2WIRE> stepper2(800, 48, 49, 45);
int servo_0_flex = 0;
Servo servos[25] = {};
int servo_speed[25] = {10, 50, 100, 10, 20, 30, 40, 50, 60, 70, 80, 90, 90, 70, 60, 50, 40, 30, 20, 10, 40, 50, 60, 70, 0};
int servo_targets[25] = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0}; //Цель
int servo_pos[25] = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0}; //Тех
long servo_timers[25] = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0};
int servo_0_target = 0;
long timer_0 = 0;
int right_moving = 0, left_moving = 0;
void fillSendData() {
  for (byte i = 0; i < 40; i++) {
    sendData[i] = i;
  }
}

void checkDist() {
  if (millis() - distTimer > 80) {
    frontLidar.getData(frontDist);
    if (frontDist < LIDAR_MIN_DIST_CIRCLE){
      LIDAR_MIN_DIST_CIRCLE = frontDist;
    }
    distTimer = millis();
  }
}

void setup() {
  Serial.begin(9600);
  pinMode(24, INPUT_PULLUP);
  pinMode(25, INPUT_PULLUP);
  pinMode(MISO, OUTPUT);
  SPCR |= _BV(SPE);
  SPI.attachInterrupt();
  fillSendData();
  Serial2.begin(115200);
  Serial3.begin(115200);
  delay(20);
  frontLidar.begin(&Serial2);
  backLidar.begin(&Serial3);
  stepper1.setRunMode(FOLLOW_POS);
  stepper2.setRunMode(FOLLOW_POS);
  stepper1.setMaxSpeed(1000);
  stepper2.setMaxSpeed(1000);
  stepper1.setAcceleration(500);
  stepper2.setAcceleration(500);
  stepper1.autoPower(true);
  stepper2.autoPower(true);
 

  stepper1.invertEn(true);
  stepper2.reverse(true);
  stepper2.invertEn(true);
  timer_0 = millis();
  
  // Gripper base from robot corpus to final gripper
  servo_0.attach(48);
  servo_1.attach(46);
  servo_2.attach(44);
  servo_3.attach(42); 
  servo_4.attach(40); // griper servo left
  servo_5.attach(38); // griper servo right
  servo_6.attach(36); // gripper base_0
  servo_7.attach(34); // gripper base_1
  servo_8.attach(32); // gripper base_2
  servo_9.attach(30);
  
  servo_0.write(0);
  servo_1.write(0);
  servo_2.write(0);
  servo_3.write(0);
  servo_4.write(70);
  servo_5.write(120);
  servo_6.write(120);
  servo_7.write(10);
  servo_8.write(30);
  servo_9.write(0);

  servo_targets[9] = 118; // Init pose of lidar servo
  servo_speed[9] = 0; // Max speed
  
  disp.clear();
  disp.brightness(2);
  disp.displayInt(PREDICTION_POINTS);
  

  // Steppers warmup and test
  stepper1.setTarget(100, RELATIVE);
  stepper2.setTarget(100, RELATIVE);

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


void flexim() {
  for (int i = 0; i <= 23; i++) {
    if (millis() - servo_timers[i] >= servo_speed[i] and servo_pos[i] != servo_targets[i]) {
      servo_timers[i] = millis();
      if (servo_targets[i] - servo_pos[i] > 0) {
        servo_pos[i]++;
      } else {
        servo_pos[i]--;
      }
      servo_array[i].write(servo_pos[i]);
    }
  }
}

void loop () {
  checkDist(); // Update lidar "Circle" Data
  flexim(); // Control servos

  if (WAITING && (servo_pos[9] <= 55 || servo_pos[9] >= 117)  && LIDAR_MIN_DIST_CIRCLE < 1000){
    if (LIDAR_MIN_DIST_CIRCLE > 50){
      Serial.println("Can drive");
      Serial.println(LIDAR_MIN_DIST_CIRCLE);
      stepper1.setTarget(PENDING_STEPS, RELATIVE);
      stepper2.setTarget(PENDING_STEPS, RELATIVE);
      WAITING = false;
    }
    
  }
  
  sendData[0] = stepper1.tick(); 
  sendData[1] = stepper2.tick();
  //if (WAITING){ // If robot is stopped, because an obstacle located with lidar, simulate that robot is driving to prevent high level from jumping to next step;
  //  sendData[0] = 1;
  //  sendData[1] = 1;
  //}
  // Lessuse for current robot
  //sendData[2] = stepper3.tick();
  //sendData[3] = stepper4.tick();
  if(0){
if (servo_pos[9] <= 55) {
     servo_targets[9] = 118;
     servo_speed[9] = 15;
     sendData[8] = servo_pos[9];
     LIDAR_SCANNED_CIRCLE = false; // start circle
     
   }
   else if (servo_pos[9] >= 117) {
     servo_targets[9] = 54;
     servo_speed[9] = 15;
     sendData[8] = servo_pos[9];
     LIDAR_SCANNED_CIRCLE = true; // finish circle
     LIDAR_MIN_DIST_CIRCLE = 1000;
   }
   else {
     sendData[8] = servo_pos[9];
  }
  }
   
  
  if (spiTranferEnd) {
    joinRecievedBytes();

    switch (int_data[0]) {
      case 0: // Reserved for fun
        break;
      case 1: // Control steppers
        /* Index in input buffer
        0: command name - 1; fixed
        1: stepper_0 max speed
        2: stepper_0 acceleration
        3: stepper_0 steps to go count
        4: stepper_1 max speed
        5: stepper_1 acceleration
        6: stepper_1 steps to go count
        */
        stepper1.setMaxSpeed(int_data[1]);
        stepper2.setMaxSpeed(int_data[4]);
        
        stepper1.setAcceleration(int_data[2]);
        stepper2.setAcceleration(int_data[5]);
        
        stepper1.setTarget(-int_data[3], RELATIVE);
        stepper2.setTarget(-int_data[6], RELATIVE);
        
        break;
      case 2: // Control servo
        /* Index in  input buffer
        0: command name - 2; fixed
        1: servo index
        2: servo speed (timer between 1 degree steps)
        3: servo target angle to rotate in degrees
        */
        servo_targets[int_data[1]] = int_data[3];
        servo_speed[int_data[1]] = int_data[2];
        break;
      case 3: // Change pin mode of pin (write/read)
        pinMode(int_data[1], int_data[2]);
        break;
      case 4: // Digital read from selected port
        sendData[4] = digitalRead(int_data[1]);
        break;
      case 5: // Digital write to selected pin
        digitalWrite(int_data[1], int_data[2]);
        break;
      case 6: // Analog read from selected pin (is it float?)
        sendData[5] = analogRead(int_data[1]);
        break;
      case 7: // Analog write to selected pin
        analogWrite(int_data[1], int_data[2]);
        break;
      case 8: // Play trick with robot color changing
        switch (int_data[1]) {
          case 0:
            switch (int_data[2]) {
              case 0:
                strip.clear();
                strip.show();
                break;
              case 1:
                strip.setBrightness(int_data[3]);
                strip.show();
                break;
              case 2:
                strip.fill(mRGB(int_data[3], int_data[4] , int_data[5]));
                strip.show();
                break;
              case 3:
                strip.set(int_data[3], mRGB(int_data[4], int_data[5] , int_data[6]));
                strip.show();
                break;
            }
            break;
          case 1:
            switch (int_data[2]) {
              case 0:
                one_strip.clear();
                one_strip.show();
                break;
              case 1:
                one_strip.setBrightness(int_data[3]);
                one_strip.show();
                break;
              case 2:
                one_strip.fill(mRGB(int_data[3], int_data[4] , int_data[5]));
                one_strip.show();
                break;
              case 3:
                one_strip.set(int_data[3], mRGB(int_data[4], int_data[5] , int_data[6]));
                one_strip.show();
                break;
            }
            break;
        }
        break;
      case 9: // Check lidar and stop robot if needed
        frontLidar.getData(frontDist);
        //backLidar.getData(backDist);
        frontDist = constrain(frontDist, 0, 255);
        backDist = 255;
        sendData[6] = frontDist;
        sendData[7] = backDist;
        if (frontDist < 45 && !WAITING){
          PENDING_STEPS = -abs(abs(stepper1.getTarget()) - abs(stepper1.getCurrent()));  
          stepper1.brake();
          stepper2.brake();
          WAITING = true;
        }
        break;
      case 10: // Update prediction display data
        disp.displayInt(int_data[1]);
        break;
    }
  }
  
}
