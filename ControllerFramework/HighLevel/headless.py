from robot import Robot
from config import *

route = load_route_file("headless.json")
START_POINT = preprocess_route_header(route)
robot = Robot(ROBOT_SIZE, START_POINT, "E", SIDE, MM_COEF, ROTATION_COEFF, ONE_PX, 1) # Start robot in real mode
stop_flag = False
robot.interpret_route(route, monitoring_dict, stop_flag)