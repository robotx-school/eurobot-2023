from robot import Robot
from config import *
import json
import time
#import threading Adapting code to use multiprocessing
import multiprocessing

class TaskManagerFunctions:
    # Functions
    def __init__(self):
        pass
    def return_back(self, current_x, current_y, dest_point_x, dest_point_y):
       pass
    def debug(self):
       print("Test action")

class TaskManager:
    # Monitor current robot status and pool of requested actions
    def __init__(self, start_time, robot, finish_point=(0, 356)):
        self.start_time = start_time
        self.robot = robot
        self.emergency_time = 5 # seconds
        self.finish_point = finish_point

    def monitoring_loop(self):
        global stop_flag
        while True:
            time_gone = time.time() - self.start_time
            if time_gone >= self.emergency_time:
                #print("Low time")
                stop_flag = True
                #current_x = self.robot.curr_x
                #current_y = self.robot.curr_y
                #angle, dist = self.robot.compute_point((current_x, current_y))
                #print(f"Current coords: {self.robot.curr_x}, {self.robot.curr_y}")
                break
            print(time_gone)
            time.sleep(0.5)

def preprocess_route_header(route):
    header = route[0]
    if header["action"] == -1: # Header action
        return tuple(header["start_point"])

def load_route_file(path):
    with open(path) as f:
        route = json.load(f)
    return route

monitoring_dict = {"steps_done": 0, "steps_left": 0, "distance_drived": 0, "motors_time": 0, "start_time": 0}
route = load_route_file("hl.json")
START_POINT = preprocess_route_header(route)
robot = Robot(ROBOT_SIZE, START_POINT, "E", SIDE, MM_COEF, ROTATION_COEFF, ONE_PX, 1) # Start robot in real mode
stop_flag = 0
start_time = time.time()
tmgr = TaskManager(start_time, robot)
tmgr_funcs = TaskManagerFunctions()
threading.Thread(target=lambda: tmgr.loop()).start() # Start task manager loop in another thread
#robot.interpret_route(route, monitoring_dict, stop_flag)
while True:
    if stop_flag:
        print("Stop")
