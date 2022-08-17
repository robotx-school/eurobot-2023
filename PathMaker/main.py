import cv2
import numpy as np
from termcolor import colored
import json
import spilib
from config import *
import time
import sys
sys.path.append('../ControllerFramework/HighLevel') # Add folder with robot class
from robot import Robot


# Under DEV
class Logger:
    def __init__(self):
        pass

# Under DEV


def recreate_path_side(path):
    # right side converter
    converted_path = []
    for i in path:
        converted_path.append((903 - i[0], i[1]))
    return converted_path


def interactive_mode_cv(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDBLCLK:
        cv2.circle(field, (x, y), 5, (255, 0, 0), -1)
        print("New point:", x, y)
        robot.compute_point((x, y), field)



def save_path(path, path_name):
    with open(f'{path_name}.json', 'w') as f:
        json.dump(path, f)


def load_path(file_name):
    with open(f'{file_name}.json') as f:
        return json.load(f)

def save_path_frontend():
    path_name = input(colored("Name for path file>", "yellow"))
    try:
        save_path(path_curr, path_name)
        print(colored("Path saved!", "green"))
    except Exception as e:
        print(e)
        print(colored("Error during writing path", "red"))

if __name__ == "__main__":
    field = cv2.imread("field.png")
    
    print(colored(f"[DEBUG] Field size: {field.shape}", "yellow"))
    one_px = 3000 / field.shape[1]
    print(colored(f"[DEBUG] Px in mms: {one_px}", "yellow"))
    robot_size = 50  # Robot is not a point, it is a non zero vector
    mm_coef = 9.52381 # Dev robot
    rotation_coeff = 12.1 # Dev robot
    robot = Robot(robot_size, START_POINT, "E", mm_coef, rotation_coeff, one_px, 0)
    
    mode = int(input("Mode (0 - create path; 1 - calculate path; 2 - headless execution; -1 - exit)>"))
    
    if mode == 0:
        path_curr = []
        route_analytics = {"dist": 0, "rotations": 0}
        curr_x, curr_y = START_POINT # start
        robot_vect_x, robot_vect_y = curr_x + robot_size, curr_y
        cv2.arrowedLine(field, (curr_x, curr_y), (robot_vect_x, robot_vect_y), (0, 0, 255), 5)
        cv2.namedWindow('Interactive mode')
        cv2.setMouseCallback('Interactive mode', interactive_mode_cv)
        while True:
            cv2.imshow('Interactive mode', field)
            k = cv2.waitKey(20) & 0xFF
            if k == 27:
                exit_confirmation = input(colored("Do you want to save changes?(y/n/c)>", "yellow"))
                if exit_confirmation == "y":
                    save_path_frontend()
                elif exit_confirmation == "c":
                    print("Canceling...")
                else:
                    print("Goodbye")
                    cv2.destroyAllWindows()
                    break
            elif k == HOTKEYS[1]:
                for row in range(50, 969, 51):
                    cv2.line(field, (0, row), (field.shape[1], row), (0, 0, 0), 1)
                for column in range(52, 1484, 51):
                    cv2.line(field, (column, 0), (column, field.shape[0]), (0, 0, 0), 1)
            elif k == HOTKEYS[0]:
                save_path_frontend()

    elif mode == 1:
        cv2.arrowedLine(field, (robot.curr_x, robot.curr_y), (robot.robot_vect_x, robot.robot_vect_y), (0, 0, 255), 5)
        name = input(colored("Name for path file>", "yellow"))
        points_dest = load_path(name)
        for point in points_dest:
            robot.compute_point(point, field)

        print(colored(
            f"Summary:\nDistance: {robot.route_analytics['dist']}mm\nRotations: {robot.route_analytics['rotations']}\nFinal coordinates: {robot.curr_x, robot.curr_y}",
            "green"))
        cv2.imshow("Path Gen - Calculated image way", field)
        while True:
            key = cv2.waitKey(20) & 0xFF
            if key == 27:
                cv2.destroyAllWindows()
                break
                exit()
                
    
    elif mode == 2:
        cv2.arrowedLine(field, (robot.curr_x, robot.curr_y), (robot.robot_vect_x, robot.robot_vect_y), (0, 0, 255), 5)
        file_to_load = input("Route>")
        points_dest = load_path(file_to_load)
        for point in points_dest:
            computed = robot.compute_point(point, field)
            robot.go(computed)
        print(colored(
            f"Summary:\nDistance: {robot.route_analytics['dist']}mm\nRotations: {robot.route_analytics['rotations']}\nFinal coordinates: {robot.curr_x, robot.curr_y}\nMotors working time: {robot.route_analytics['motors_timing'] / 60} seconds",
            "green"))
       
    elif mode == -1:
        exit(0)

