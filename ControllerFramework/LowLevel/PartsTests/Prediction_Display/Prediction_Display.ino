#define DISP_CLK 21
#define DISP_DIO 20
#include "GyverTM1637.h"

GyverTM1637 disp(DISP_CLK, DISP_DIO);

void setup() {
  disp.clear();
  disp.brightness(2);
}


void loop() {
    disp.displayInt(3214);
}
