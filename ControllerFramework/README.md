# Communication protocol
This documentation does not depend on the low-level protocol (SPI, i2c), as it describes the high-level command exchange protocol between arduino and raspberry

## Data-packets
Each data packet have 20 items. </br>
Raspberry sends commands to arduino and arduino(as responce) sends sensors data.
### Raspberry(High-level)
`[command_id, cmd_arg_0, cmd_arg_1, cmd_arg_2, cmd_arg_3...]` </br>
__`command_id`__ - id of command to execute on arduino </br>
Available commands: </br>
1. 0 - stop all motors: no arguments
2. 1 - start motors: cmd_arg_0 - left motor speed, cmd_arg_1 - left motor accel, cmd_arg_2 - left motor steps, cmd_arg_3 - right motor speed, cmd_arg_4 - right motor accel, cmd_arg_5 - right motor steps and same logic for 2 another motors
3. 2 - move servo: cmd_arg_0 - servo number, cmd_arg_1 - finish position angle, cmd_arg_2 - delay(to move smoothly)
4. 3 - change pin mode for concret pin(INPUT, OUPUT or INPUT PULLUP)
5. 4 - get digital pin status(HIGH, LOW)
6. 5 - set digital pin status(HIGH, LOW)
__`cmd_arg_0`__ - argument for command </br>
 And all other elements are also command arguments
### Arduino(Low-level)
`[motor_0_steps, motor_1_steps, motor_2_steps, motor_3_steps, not_configured, not_configured, not_configured, not_configured, not_configured]`</br>
Output: </br>
1. motor_0_steps - current steps on motor 0
2. motor_1_steps - current steps on motor 1
3. motor_2_steps - current steps on motor 2
4. motor_3_steps - current steps on motor 3
5. status of pin
6. not_configured
7. not_configured


