#include <SPI.h>
#include <RF24_config.h>
#include <nRF24L01.h>
#include <RF24.h>

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

#define STEPS_IN_MILLIMETER 40

int getSensors() {
  /*
  Function that get data from all sensors(all sensors described in README.md) and return in as array(20 items)
  */
}

void fillSendData() {
  /*
  Temp function for testing SPI
  */
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
}

ISR (SPI_STC_vect)
{
  /*
  Interrupt handler for SPI data transfer
  */
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
  /*
  Format recieved data from raspberry to array of int (20 items)
  */
  for (int i = 0; i < DATA_SIZE; i += 2) {
    int_data[i / 2] = data[i] << 8 | data[i + 1];
  }
  spiTranferEnd = 0;
}
void printSpiData() {
  /*
  Debug function for printing recieved data to Serial
  */
  for (int i = 0; i < DATA_SIZE / 2; i++) {
    Serial.print(int_data[i]);
    Serial.print(" ");
  }
  Serial.println();
}
void sendNRF(){
  /*
  NRF function to send data and revert SPI
  */
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
  if (spiTranferEnd) {
    joinRecievedBytes();
    printSpiData();
    switch(int_data[0]){
      case 0:
        Serial.println("Stop motors");
        break;
      case 1:
        Serial.println("Start motors");
        // Data to controll robot motors
        /*left_motor:
          speed: int_data[1]
          accel: int_data[2]
          distance: STEPS_IN_MILLIMETER * int_data[3]
        */

        /*right_motor:
          speed: int_data[4]
          accel: int_data[5]
          distance: STEPS_IN_MILLIMETER * int_data[6]
        */
        break;
      case 2:
        Serial.println("Move servo");
        // Data to controll servo
        /*
          README.md
        */

      
    }
  }
}
