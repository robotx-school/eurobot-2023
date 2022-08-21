import spidev
import time


class SpiCommunication:
    def __init__(self, addr=(0, 0), spi_max_speed_hz=1000000):
        self.addr = addr
        self.spi = spidev.SpiDev()
        self.spi.open(*addr)
        self.spi.max_speed_hz = spi_max_speed_hz


    def list_int_to_bytes(self, input_list) -> list:
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


    def spi_send(self, txData=[]) -> list:
        """
        Send generated list by SPI

        Args:
            txData (list): if less than 40 numbers, will be filled with 0's

        Returns:
            list: received data
        """
        N = 40
        txData = self.list_int_to_bytes(txData)
        txData = txData + [0] * (N - len(txData))
        rxData = []
        _ = self.spi.xfer2([240])  # 240 - b11110000 - start byte
        for i in range(40):
            rxData.append(self.spi.xfer2([txData[i]])[0])
        self.spi.close()
        return rxData

    def move_robot(self, dir_, interpreter_control_flag, speed=1000, accel=1000, distance=1000, verbose=False, sensor_id=-1, sensor_val=None):
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
        received_data = self.spi_send(send_data)
        time.sleep(0.07)
        # Freeze app until action finish
        while True:
            recieved = self.spi_send([])
            if (recieved[0] == 0 and recieved[1] == 0):
                break
            time.sleep(0.5)  # Review this value FIXIT

            # Sensors not supported yet
            # if check_sensor(recieved, sensor_id, sensor_val):
            #    spi_send([1, 0, 0, 0, 0, 0, 0])
            #    print("Stop")
            #    break
        if verbose:  # FIXIT move verbose to debug log
            print(
                f'Moved {dir}, speed: {speed}, accel: {accel}, distance: {distance}')
            print(f'Received from arduino: {received_data}')


    def stop_robot(self):
        pass


    def move_servo(self, servo_num, start_angle, finish_angle, delay):
        """
        Reimplement function
        """
        data = [2, servo_num, start_angle, finish_angle, delay]
        spi_send(data)
        time.sleep(0.07)
        while True:
            recieved = spi_send([])
            if (recieved[0] == 0 and recieved[1] == 0):  # Why motors as sensors ????
                # print("Finish servo") Move to log debug
                break


if __name__ == "__main__":
    spi_communication = SpiCommunication()
    spi_communication.move_robot("left", False, distance=500)
    #move_robot("forward", False, distance=-1000)
