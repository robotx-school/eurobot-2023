# Communication protocol
This documentation does not depend on the low-level protocol (SPI, i2c), as it describes the high-level command exchange protocol between arduino and raspberry

## Data-packets
Each data packet have 20 items. </br>
Raspberry sends commands to arduino and arduino(as responce) sends sensors data.
### Raspberry
`[command_id, cmd_arg_0, cmd_arg_1, cmd_arg_2, cmd_arg_3...]` </br>
__`command_id`__ - id of command to execute on arduino </br>
Available commands: </br>
1. 0 - stop all motors: no arguments
2. 1 - start motors: cmd_arg_0 - left motor speed, cmd_arg_1 - left motor accel, cmd_arg_2 - left motor steps, cmd_arg_3 - right motor speed, cmd_arg_4 - right motor accel, cmd_arg_5 - right motor steps
3. 2 - move servo: cmd_arg_0 - start position angle, cmd_arg_1 - finish position angle, cmd_arg_2 - delay(to move smoothly)
4. 3 - get all sensors: no arguments(As responce we will get all sensors values)
__`cmd_arg_0`__ - argument for command </br>
 And all other elements are also command arguments
### Arduino
`[motor_0_steps, motor_1_steps, distance_0, distance_1, distance_2, distance_3, distance_4, button_0, button_1]`</br>
Output: </br>
1. motor_0_steps - current steps on motor 0
2. motor_1_steps - current steps on motor 1
3. distance_0 - data from distance meter sensor number 0
4. distance_1 - data from distance meter sensor number 1
5. distance_2, distance_3, distance_4 - reserved for distance meters
6. button_0 - button for selecting side
7. button_1 - button for selecting stategy(send as int)


