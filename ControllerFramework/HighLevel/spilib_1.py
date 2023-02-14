"""
Check __doc__ ; README.md ; requirements.txt

spilib_lite is a fork of spilib (see README.md ).

This is a python library for working with Arduino
by SPI (40/20 packets).



Global variables:
    FAKE_DATA (No longer supported)

Functions:
    Working with SPI communication:
        list_int_to_bytes()
        spi_send()
    High-level Arduino control functions:
        move_robot()
        stop_robot()
        get_sensors_data()
        move_servo()
    Low-level Arduino control functions:
        low_pinMode()
        low_digitalRead()
        low_digitalWrite()
        low_analogRead()
        low_analogWrite()
        low_digitalWrite_echo()
        low_digitalRead_echo()
        low_analogRead_echo()
    Working with LEDs:
        led_set()
        led_fill()
        led_setBrightness()
        led_clear()
    
        
Not supported functions:
    Ready-made Arduino control functions:
        check_sensor()
    Simulation of incoming data:
        fake_req_data()
        change_fake_data()
    Low-level Arduino control functions:
        low_analogWrite_echo()
"""

import spidev
import time
#import modules

global FAKE_DATA # For dev without working robot
FAKE_DATA = [0] * 20
#set global variables

def list_int_to_bytes(input_list) -> list:
    """
    Split list of int values (-32768 to 32767) to list transferable by SPI

    Args:
        input_list (list): max 20 numbers

    Returns:
        list: transferable list
    """
    output_list = []
    for int_data in input_list:
        output_list.append(int_data >> 8)
        output_list.append(int_data & 255)
    return output_list


def spi_send(txData = []) -> list:
    """
    Send generated list by SPI

    Args:
        txData (list): if less than 40 numbers, will be filled with 0's

    Returns:
        list: received data
    """
    try:
        N = 40
        spi = spidev.SpiDev()
        spi.open(0, 0)
        spi.max_speed_hz = 1000000
        txData = list_int_to_bytes(txData)
        txData = txData + [0] * (N - len(txData))
        rxData = []
        _ = spi.xfer2([240])  # 240 - b11110000 - start byte
        for i in range(40):
            rxData.append(spi.xfer2([txData[i]])[0])
        spi.close()
        return rxData
    except FileNotFoundError: # If spi communication problems
        return [0] * 20

def check_sensor(recieved, sensor_id, sensor_val):
    """
    This function is deprecated and is no longer supported.

    OLD DOC:

    Sensors not supported yet
    Check if sensor data is true. Used for distance meters

    Args:
        recieved (list): current sensors data from arduino
        sensord_id (int): sensor id to check
        sensor_val (int/str): value that makes sensors data to true

    Returns:
        Bool: Sensors true or false
    """
    if sensor_id != -1:
        if int(recieved[sensor_id]) == int(sensor_val):
            return True
        else:
            return False

def move_robot(dir_, interpreter_control_flag, speed=1000, accel=1000, distance=1000, verbose=False, sensor_id=-1, sensor_val=None):
    send_data = []
    """
    Moves a robot

    Args:
        dir (str): Possible values: 'forward', 'back', 'left', 'right'
        speed (int, optional): Speed. Defaults to 1000.
        accel (int, optional): Acceleration. Defaults to 1000.
        distance (int, optional): Number of distance. Defaults to 1000.
        verbose (bool, optional): Enable verbose printing. Defaults to False.
    """
    if dir_ == 'forward':
        send_data = [1, speed, accel, distance, speed, accel, distance]

    elif dir_ == 'left':
        send_data = [1, speed, accel, -distance, speed, accel, distance]
    elif dir_ == 'right':
        send_data = [1, speed, accel, distance, speed, accel, -distance]
    else:
        print(f'No such direction: {dir_}')
        return False
    received_data = spi_send(send_data)
    time.sleep(0.07)
    
    if verbose: # FIXIT move verbose to debug log
        print(f'Moved {dir}, speed: {speed}, accel: {accel}, distance: {distance}')
        print(f'Received from arduino: {received_data}')


def stop_robot():
    """
    Stop a robot
    """
    move_robot("forward", False, distance=0) # Messy but works

def get_sensors_data():
    """Get SPI Data"""
    return spi_send([])

def move_servo(servo_num, start_angle, finish_angle, delay):
    """
    Move Servo

    Args:
        servo_num (int): Servo number (1/2/3/4/5/6/7/8/9 <=>
                                       30/32/34/36/38/40/42/44/46/48)
        start_angle (int): Servo starting angle (degrees)
        finish_angle (int): Servo finishing angle (degrees)
        delay (int): Delay (milliseconds)
    """
    data = [2, servo_num, start_angle, finish_angle, delay]
    spi_send(data)
    time.sleep(0.07)
    while True:
        recieved = spi_send([])
        if (recieved[0] == 0 and recieved[1] == 0): # Why motors as sensors ????
            #print("Finish servo") Move to log debug
            break

def low_pinMode(pin, mode):
    """
    Low level function (Arduino): pinMode

    pin (int): pin number
    mode (int): integer mode number of pinMode
    """
    spi_send([3, pin, mode])

def low_digitalRead(pin):
    """
    Only changes the values in the returned package.
    Use get_sensors_data() to get the package itself.
    Low level function (Arduino): digitalRead

    pin (int): pin number
    """
    spi_send([4, pin])

def low_digitalWrite(pin, value):
    """
    Only changes the values on the Arduino.
    To return the package, use low_digitalWrite_echo() or
    low_digitalRead().
    Low level function (Arduino): digitalWrite

    pin (int): pin number
    value (bool -> int): digitalWrite value (0/1)
    """
    spi_send([5, pin, value])

def low_digitalWrite_echo(pin, value):
    """
    Low level functions (Arduino): digitalWrite + digitalRead

    pin (int): pin number
    value (bool -> int): digitalWrite value (0/1)

    Returns data get_sensors_data()[4]
    """
    low_digitalWrite(pin, value)
    low_digitalRead(pin)
    return get_sensors_data()[4]

def low_digitalRead_echo(pin):
    """
    The function returns data (digital) from the pin.
    Low level function (Arduino): digitalRead

    pin (int): pin number
    """
    spi_send([4, pin])
    return get_sensors_data()[4]
    

def low_analogRead(pin):
    """
    Only changes the values in the returned package.
    Use get_sensors_data() to get the package itself.
    Low level function (Arduino): analogRead
    ()
    
    pin (int): pin number
    """
    spi_send([6, pin])

def low_analogWrite(pin, value):
    """
    This function is deprecated and is no longer supported.
    The function does not work due to the initialization of servos.
    analogWrite() is locked and works like digitalWrite with values 0 and 255.

    OLD DOC:
    Only changes the values on the Arduino.
    To return the package, use low_analogWrite_echo() or
    low_analogRead().
    Low level function (Arduino): analogWrite

    pin (int): pin number
    value (bool -> int): analogWrite value (0-255)
    """
    spi_send([7, pin, value])

def low_analogWrite_echo(pin, value):
    """
    This function is deprecated and is no longer supported.
    The function does not work due to the initialization of servos.
    analogWrite() is locked and works like digitalWrite with values 0 and 255.

    OLD DOC:
    Low level functions (Arduino): analogWrite + analogRead

    pin (int): pin number
    value (bool -> int): analogWrite value (0/1)

    Returns data get_sensors_data()[5]
    """
    low_analogWrite(pin, value)
    low_analogRead(pin)
    return get_sensors_data()[5]

def low_analogRead_echo(pin):
    """
    The function returns data (analog) from the pin.
    Low level function (Arduino): analogRead

    pin (int): pin number
    """
    spi_send([6, pin])
    return get_sensors_data()[5]

def led_clear(one_strip = False):
    """
    Turns off the selected strip.

    one_strip (bool): Is a strip with one LED selected
    """
    if one_strip:
        spi_send([8, 1, 0])
    else:
        spi_send([8, 0, 0])

def led_setBrightness(value, one_strip = False):
    """
    Set LED Brightness.

    value (int) : Brightness (0-255)
    one_strip (bool): Is a strip with one LED selected
    """
    if one_strip:
        spi_send([8, 1, 1, value])
    else:
        spi_send([8, 0, 1, value])

def led_fill(r, g, b, one_strip = False):
    """
    Fill LED strip.

    r (int) : Red (R) in mRGB (0-255)
    g (int) : Green (G) in mRGB (0-255)
    b (int) : Blue (B) in mRGB (0-255)
    one_strip (bool): Is a strip with one LED selected
    """

    if one_strip:
        spi_send([8, 1, 2, r, g, b])
    else:
        spi_send([8, 0, 2, r, g, b])

def led_set(n, r, g, b, one_strip = False):
    """
    Fill LED strip.

    n (int) : LED number in the strip
    r (int) : Red (R) in mRGB (0-255)
    g (int) : Green (G) in mRGB (0-255)
    b (int) : Blue (B) in mRGB (0-255)
    one_strip (bool): Is a strip with one LED selected
    """

    if one_strip:
        spi_send([8, 1, 3, n, r, g, b])
    else:
        spi_send([8, 0, 3, n, r, g, b])

# For dev without robot
def fake_req_data():
    """
    This function is deprecated and is no longer supported.

    OLD DOC:
    For dev without robot
    Return eval of file 'fake_spi'
    """
    time.sleep(0.1)
    try:
        with open("fake_spi") as file:
            return eval(file.read())
    except:
        return [0] * 20

def change_fake_data(ind, val):
    """
    This function is deprecated and is no longer supported.

    OLD DOC:
    For dev without robot
    Edit global var FAKE_DATA
    ind (int): number of item in FAKE_DATA
    val (int): new value of FAKE_DATA[ind]
    """
    global FAKE_DATA
    FAKE_DATA[ind] = val
