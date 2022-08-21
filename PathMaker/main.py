import threading
import tkinter
import cv2
from termcolor import colored
import json
from config import *
import time
import sys
# Add folder with robot class
sys.path.append('../ControllerFramework/HighLevel')
from robot import Robot
import spilib


class ConfigWindow:
    def __init__(self, start_coords):
        self.root = tkinter.Tk()
        self.root.title("Config robot")
        self.root.geometry("300x100")
        try:
            self.root.attributes('-type', 'dialog')
        except:
            pass
        self.coords_variable = tkinter.StringVar()
        self.coords_variable.set(f"{start_coords[0]}, {start_coords[1]}")
        self.build()
        self.root.mainloop()

    def build(self):
        self.start_point_label = tkinter.Label(
            self.root, text="Start coords(x, y):")
        self.start_point_input = tkinter.Entry(
            self.root, textvariable=self.coords_variable)
        self.start_point_label.grid(row=0, column=0, sticky="w")
        self.start_point_input.grid(row=0, column=1, padx=5, pady=5)
        self.apply_button = tkinter.Button(
            text="Apply", command=lambda: redraw(self.coords_variable))
        self.apply_button.grid(row=1, sticky="nsew")


def redraw(coords):
    global robot, field
    raw = coords.get().split(",")
    x = int(raw[0])
    y = int(raw[1])
    robot.calculate_robot_start_vector((x, y), "E")
    field = cache_field_image.copy()
    cv2.arrowedLine(field, (robot.curr_x, robot.curr_y),
                    (robot.robot_vect_x, robot.robot_vect_y), (0, 0, 255), 5)
    for point in robot.curr_path_points:
        cv2.circle(field, point, 5, (255, 0, 0), -1)
        robot.compute_point(point, field, False)


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
    route = [{"action": -1, "start_point": robot.start_point, "direction": "E"}]
    for point in path:
        route.append({"action": 1, "point": point})
    with open(f'{path_name}.json', 'w') as f:
        json.dump(route, f)


def load_path(file_name):
    with open(f'{file_name}.json') as f:
        return json.load(f)


def save_path_frontend():
    path_name = input(colored("Name for path file>", "yellow"))
    try:
        save_path(robot.curr_path_points, path_name)
        print(colored("Path saved!", "green"))
    except Exception as e:
        print(e)
        print(colored("Error during writing path", "red"))


def safe_exit():
    exit_confirmation = input(
        colored("Do you want to save changes?(y/n/c)>", "yellow"))
    if exit_confirmation == "y":
        save_path_frontend()
    elif exit_confirmation == "c":
        print("Canceling...")
    else:
        print("Goodbye")
        cv2.destroyAllWindows()
        exit()


if __name__ == "__main__":
    field = cv2.imread("field.png")
    cache_field_image = field.copy()

    print(colored(f"[DEBUG] Field size: {field.shape}", "yellow"))
    one_px = 3000 / field.shape[1]
    print(colored(f"[DEBUG] Px in mms: {one_px}", "yellow"))
    robot_size = 50  # Robot is not a point, it is a non zero vector
    mm_coef = 9.52381  # Dev robot
    rotation_coeff = 12.1  # Dev robot
    robot = Robot(robot_size, START_POINT, "E",
                  mm_coef, rotation_coeff, one_px, 0)

    mode = int(input(
        "Mode (0 - create path; 1 - calculate path; 2 - modify route; 3 - headless execution; 4 - test tk; -1 - exit)>"))

    if mode == 0:
        cv2.arrowedLine(field, (robot.curr_x, robot.curr_y),
                        (robot.robot_vect_x, robot.robot_vect_y), (0, 0, 255), 5)
        cv2.namedWindow('Interactive mode')
        cv2.setMouseCallback('Interactive mode', interactive_mode_cv)
        while True:
            cv2.imshow('Interactive mode', field)
            k = cv2.waitKey(20) & 0xFF
            if k == 27:
                safe_exit()
            elif k == HOTKEYS[1]:
                for row in range(50, 969, 51):
                    cv2.line(field, (0, row),
                             (field.shape[1], row), (0, 0, 0), 1)
                for column in range(52, 1484, 51):
                    cv2.line(field, (column, 0),
                             (column, field.shape[0]), (0, 0, 0), 1)
            elif k == HOTKEYS[0]:
                save_path_frontend()
            elif k == HOTKEYS[2]:
                threading.Thread(target=lambda: ConfigWindow(
                    robot.start_point)).start()

    elif mode == 1:
        name = input(colored("Name for path file>", "yellow"))
        points_dest = load_path(name)
        robot.calculate_robot_start_vector(points_dest[0]["start_point"], points_dest[0]["direction"])
        cv2.arrowedLine(field, (robot.curr_x, robot.curr_y),
                        (robot.robot_vect_x, robot.robot_vect_y), (0, 0, 255), 5)
        for instruction in points_dest:
            if instruction["action"] == 1:
                robot.compute_point(instruction["point"], field)

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
        current_route = input("Route>")
        route = load_path(current_route)
        robot.calculate_robot_start_vector(route[0]["start_point"], "E")
        cv2.arrowedLine(field, (robot.curr_x, robot.curr_y),
                        (robot.robot_vect_x, robot.robot_vect_y), (0, 0, 255), 5)
        for instruction in route:
            if instruction["action"] == 1:
                robot.curr_path_points.append(instruction["point"])
                cv2.circle(field, instruction["point"], 5, (255, 0, 0), -1)
                robot.compute_point(instruction["point"], field)
        cv2.namedWindow('Path Gen - Edit route')
        cv2.setMouseCallback('Path Gen - Edit route', interactive_mode_cv)
        while True:
            cv2.imshow("Path Gen - Edit route", field)
            key = cv2.waitKey(20) & 0xFF
            if key == 27:
                safe_exit()
            elif key == HOTKEYS[0]:
                save_path_frontend()

    elif mode == 3:
        cv2.arrowedLine(field, (robot.curr_x, robot.curr_y),
                        (robot.robot_vect_x, robot.robot_vect_y), (0, 0, 255), 5)
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

    elif mode == 4:
        threading.Thread(target=lambda: ConfigWindow(
            robot.start_point)).start()
