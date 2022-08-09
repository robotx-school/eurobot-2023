import spidev
import time

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
    N = 40
    spi = spidev.SpiDev()
    spi.open(0, 0)
    spi.max_speed_hz = 1000000
    txData = list_int_to_bytes(txData)
    txData = txData+[0] * (N - len(txData))
    rxData = []
    _ = spi.xfer2([240])  # 240 - b11110000 - start byte

    for i in range(40):
        rxData.append(spi.xfer2([txData[i]])[0])
    spi.close()

    return rxData

if __name__ == "__main__":
    data = [i for i in range(20)] # sample data 
    print(data)
    print(spi_send(data))
