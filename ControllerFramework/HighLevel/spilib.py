import spidev
import time


global FAKE_DATA # For dev without working robot
FAKE_DATA = [0] * 20

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
        #print("[ERROR] SPI communication problems")
        #time.sleep(2)
        return fake_req_data()
        return [0] * 20

def check_sensor(recieved, sensor_id, sensor_val):
    """
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



def move_robot(dir_, interpreter_control_flag, speed=1000, accel=1000, distance=1000, verbose=True, sensor_id=-1, sensor_val=None):
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
        print(f'Moved {dir_}, speed: {speed}, accel: {accel}, distance: {distance}')
        #print(f'Received from arduino: {received_data}')


def stop_robot():
    move_robot("forward", False, distance=0) # Messy but works

def get_sensors_data():
    return spilib.spi_send([])

def move_servo(servo_num, start_angle, finish_angle, delay):
    """
    Reimplement function
    """
    data = [2, servo_num, start_angle, finish_angle, delay]
    spi_send(data)
    time.sleep(0.07)
    while True:
        recieved = spi_send([])
        if (recieved[0] == 0 and recieved[1] == 0): # Why motors as sensors ????
            #print("Finish servo") Move to log debug
            break

# For dev without robot
def fake_req_data():
    time.sleep(0.1)
    try:
        with open("fake_spi") as file:
            return eval(file.read())
    except:
        return [0] * 20

def change_fake_data(ind, val):
    global FAKE_DATA
    FAKE_DATA[ind] = val



if __name__ == "__main__": 
    move_robot("forward", False, distance=10)
    #move_robot("forward", False, distance=-1000)
    #[2, servo_id, start_angle, finish_angle, delay_time]
    