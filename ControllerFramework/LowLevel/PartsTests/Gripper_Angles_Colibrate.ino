#define L_MOTOR_DIR_PIN 6
#define L_MOTOR_PWM_PIN 7
#define R_MOTOR_DIR_PIN 8
#define R_MOTOR_PWM_PIN 9
#define DEBUG 0
#define DISP_CLK 21
#define DISP_DIO 20

#define LED_PIN 23
#define NUMPIXELS 100
#include <Adafruit_NeoPixel.h>
#include "GyverTM1637.h"
#include <Servo.h>
#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>
const uint64_t pipe = 0xF0F1F2F3F4LL;
RF24 radio(4, 53);  // CE, CSN

GyverTM1637 disp(DISP_CLK, DISP_DIO);

uint8_t data[13];
uint8_t maxSpeed = 0;
uint16_t resultCounter = 8888;
uint32_t dispTimer = 0;
uint32_t radioTimer = 0;
Servo part0;
Servo part1;
Servo part2;
Servo part3;
Servo gripLeft;
Servo gripRight;
Servo cherryStart;

Servo servos[] = { part0, part1, part2, part3, gripLeft, gripRight };
int servosCurrentPos[] = { 83, 20, 160, 130, 70, 115 };
int servosTargetPos[] = { 83, 20, 160, 130, 70, 115 };
uint32_t servosTimer[] = { 0, 0, 0, 0, 0, 0 };
int sDelay = 30;
uint32_t servosDelay[] = { sDelay, sDelay, sDelay, sDelay, sDelay, sDelay };

int grabState = 0;
uint32_t grabTimer = 0;

int dropState = 0;
uint32_t dropTimer = 0;


Adafruit_NeoPixel pixels(NUMPIXELS, LED_PIN, NEO_GRB + NEO_KHZ800);
uint8_t partyActivate = 0;
uint32_t partyTimer = 0;
uint32_t partyButtonTimer = 0;

void closeGripper() {
  servosTargetPos[4] = 120;
  servosTargetPos[5] = 60;
}
void openGripper() {
  servosTargetPos[4] = 80;
  servosTargetPos[5] = 105;
}
void dropGripper() {
  servosTargetPos[3] = 152;
  servosTargetPos[4] = 65;
  servosTargetPos[5] = 120;
}
void grabControl() {
  int spDelay = 700;
  if (grabState == 1 and millis() - grabTimer > 100) {
    openGripper();
    servosTargetPos[0] = 83;
    servosTargetPos[1] = 27;
    servosTargetPos[2] = 177;
    servosTargetPos[3] = 108;
    grabTimer = millis();
    grabState++;
  } else if (grabState == 2 and millis() - grabTimer > spDelay) {
    servosTargetPos[0] = 83;
    servosTargetPos[1] = 24;
    servosTargetPos[2] = 172;
    servosTargetPos[3] = 106;
    grabTimer = millis();
    grabState++;
  } else if (grabState == 3 and millis() - grabTimer > spDelay) {
    servosTargetPos[0] = 83;
    servosTargetPos[1] = 31;
    servosTargetPos[2] = 173;
    servosTargetPos[3] = 100;
    grabTimer = millis();
    grabState++;
  } else if (grabState == 4 and millis() - grabTimer > spDelay) {
    servosTargetPos[0] = 83;
    servosTargetPos[1] = 40;
    servosTargetPos[2] = 173;
    servosTargetPos[3] = 90;
    grabTimer = millis();
    grabState++;
  }else if (grabState == 5 and millis() - grabTimer > spDelay) {
    closeGripper();
    grabTimer = millis();
    grabState++;
  } else if (grabState == 6 and millis() - grabTimer > spDelay+300) {
    servosTargetPos[0] = 83;
    servosTargetPos[1] = 27;
    servosTargetPos[2] = 177;
    servosTargetPos[3] = 108;
    grabTimer = millis();
    grabState++;
  }else if (grabState == 7 and millis() - grabTimer > spDelay) {
    servosTargetPos[0] = 83;
    servosTargetPos[1] = 20;
    servosTargetPos[2] = 160;
    servosTargetPos[3] = 128;
    grabTimer = millis();
    grabState++;
  }
}
void dropControl() {
  if (dropState == 1 and millis() - dropTimer > 100) {
    servosTargetPos[0] = 83;
    servosTargetPos[1] = 22;
    servosTargetPos[2] = 73;
    servosTargetPos[3] = 145;
    dropTimer = millis();
    dropState++;
  } 
  if (dropState == 3) {
    dropGripper();
    dropTimer = millis();
    dropState++;
  }
  if (dropState == 4 and millis() - dropTimer > 2000) {
    closeGripper();
    servosTargetPos[3] = 145;
    dropTimer = millis();
    dropState=0;
  }
}
void servoPosControl() {
  for (int i = 0; i <= 5; i++) {
    if (millis() - servosTimer[i] > servosDelay[i]) {
      int delta = servosCurrentPos[i] == servosTargetPos[i] ? 0 : (servosCurrentPos[i] < servosTargetPos[i] ? 1 : -1);
      servosCurrentPos[i] += delta;
      servosTimer[i] = millis();
      servos[i].write(servosCurrentPos[i]);
    }
  }
}

void servoController() {
  servoPosControl();
  grabControl();
  dropControl();
}



void leftWheels(int speed) {
  speed = constrain(speed, -255, 255);
  if (speed > 0) {
    digitalWrite(L_MOTOR_DIR_PIN, 0);
    analogWrite(L_MOTOR_PWM_PIN, speed);
  } else if (speed < 0) {
    digitalWrite(L_MOTOR_DIR_PIN, 1);
    analogWrite(L_MOTOR_PWM_PIN, -speed);
  } else {
    digitalWrite(L_MOTOR_DIR_PIN, 0);
    analogWrite(L_MOTOR_PWM_PIN, 0);
  }
}
void rightWheels(int speed) {
  speed = constrain(speed, -255, 255);
  if (speed > 0) {
    digitalWrite(R_MOTOR_DIR_PIN, 1);
    analogWrite(R_MOTOR_PWM_PIN, speed);
  } else if (speed < 0) {
    digitalWrite(R_MOTOR_DIR_PIN, 0);
    analogWrite(R_MOTOR_PWM_PIN, -speed);
  } else {
    digitalWrite(R_MOTOR_DIR_PIN, 0);
    analogWrite(R_MOTOR_PWM_PIN, 0);
  }
}

void straight(int speed) {
  leftWheels(speed);
  rightWheels(speed);
}

void rotate(int speed) {
  speed = constrain(speed, -100, 100);
  leftWheels(speed);
  rightWheels(-speed);
}
void forwardRight(int speed) {
  leftWheels(speed);
  rightWheels(speed * 0.6);
}
void forwardLeft(int speed) {
  leftWheels(speed * 0.6);
  rightWheels(speed);
}

void STOP() {
  leftWheels(0);
  rightWheels(0);
}


void party() {
  if (partyActivate and millis() - partyTimer > 100) {
    for (int i = 0; i <= NUMPIXELS; i++) {
      pixels.setPixelColor(i, pixels.Color(random(0, 255), random(0, 255), random(0, 255)));
    }
    pixels.show();
  }
}
void setup() {

  pixels.begin();
  pixels.clear();

  pinMode(L_MOTOR_DIR_PIN, OUTPUT);
  pinMode(R_MOTOR_DIR_PIN, OUTPUT);
  pinMode(L_MOTOR_PWM_PIN, OUTPUT);
  pinMode(R_MOTOR_PWM_PIN, OUTPUT);

  part0.attach(30);
  part1.attach(32);
  part2.attach(34);
  part3.attach(36);
  gripLeft.attach(38);
  gripRight.attach(40);
  cherryStart.attach(42);

  Serial.begin(115200);

  radio.begin();
  delay(2);
  radio.setChannel(88);  // канал (0-127)
  radio.setDataRate(RF24_1MBPS);
  radio.setPALevel(RF24_PA_HIGH);
  radio.openReadingPipe(1, pipe);
  radio.startListening();




  disp.clear();
  disp.brightness(2);
  STOP();
}

void parseSerialInput() {
  String inputString = "";
  int inputArray[3];
  int inputIndex = 0;
  while (Serial.available() > 0) {
    delay(1);
    char inChar = Serial.read();
    if (inChar == '|') {
      Serial.println(inputString);
      char* ptr = strtok(inputString.c_str(), ";");
      while (ptr != NULL && inputIndex < 3) {
        inputArray[inputIndex] = atoi(ptr);
        inputIndex++;
        ptr = strtok(NULL, ";");
      }
      servosTargetPos[1] = inputArray[0];
      servosTargetPos[2] = inputArray[1];
      servosTargetPos[3] = inputArray[2];
      inputString = "";
      inputIndex = 0;
    } else if (isdigit(inChar) || inChar == ';') {
      inputString += inChar;
    }
  }
}

void loop() {
  parseSerialInput();
  servoController();
  if (radio.available()) {
    radioTimer = millis();
    radio.read(&data, sizeof(data));
    maxSpeed = data[4];
    if (!data[6]) {  //если не нажал левый дж
      data[1] == 127 ? leftWheels(0) : (data[1] == 255 ? leftWheels(maxSpeed) : leftWheels(-maxSpeed));
      data[3] == 127 ? rightWheels(0) : (data[3] == 255 ? rightWheels(maxSpeed) : rightWheels(-maxSpeed));
    }
    if (data[6]) {
      if (millis() - partyButtonTimer > 2000) {
        partyActivate = !partyActivate;
      }
    }

    if (data[8] == 1) {  //левая верхняя - начальное положение
      dropState = 0;
      servosTargetPos[0] = 83;
      servosTargetPos[1] = 20;
      servosTargetPos[2] = 160;
      servosTargetPos[3] = 130;
      openGripper();
    }
    if (data[9] == 1) {
      dropState = 0;
      grabState = 1;
      grabTimer = millis();
    }
    if (data[10] == 1 and dropState < 2 and  millis() - dropTimer > 1000) {
      dropState = 1;
      dropTimer = millis();
    } 
    if (data[10] == 1 and dropState==2 and millis() - dropTimer > 1000) {
      dropState = 3;
      dropTimer = millis();
    } 





    // gripLeft.write(ServoGripLeftPos - closeGrip);
    // gripRight.write(ServoGripRightPos + closeGrip);
  }
  if (data[9] == 0) {
    resultCounter = map(data[5], 0, 255, 10, 100);
  }



  if (DEBUG) {
    for (byte i = 0; i <= 12; i++) {
      Serial.print(data[i]);
      Serial.print("\t");
    }

    Serial.println();
  }

  if (millis() - radioTimer > 500) {
    STOP();  //если потеряли сигнал останавливаемся
  }
  if (millis() - dispTimer > 50) {
    dispTimer = millis();
    disp.displayInt(data[12]);
  }
}
