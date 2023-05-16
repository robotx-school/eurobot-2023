import spilib as sp
import time

def move_servo(servo_id, target, speed=1):
    sp.spi_send([2, servo_id, target, speed])

def grab_cherries():
    # Go to grab pose
    move_servo(6, 90)
    move_servo(7, 20)
    move_servo(8, 75)
    time.sleep(1)
    # Grab
    move_servo(5, 30)
    move_servo(4, 120)
    time.sleep(1)
    # Go to high pose
    move_servo(8, 30)
    move_servo(7, 10)
    move_servo(6, 120)

if __name__ == "__main__":
    grab_cherries()    
    #move_servo(8, 50)
    #time.sleep(0.5)
    #move_servo(6, 90)
    #time.sleep(0.5)
    #move_servo(7, 20)
    #time.sleep(1)
    #move_servo(8, 75)
    #time.sleep(1)
    #move_servo(5, 30)
    #move_servo(4, 120)
    #time.sleep(2)
    #sp.spi_send([2, 8, 40])
