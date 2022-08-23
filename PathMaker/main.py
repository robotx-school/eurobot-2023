import tkinter
import threading
import cv2
from termcolor import colored
import json
from config import *
import time
import sys
# Add folder with robot class(works under upstream github repo)
# Use only stable classes from HighLevel(that merged to master branch)
sys.path.append('../ControllerFramework/HighLevel')
import spilib
from robot import Robot

EDITING_MODE_ID = 0  # 0 - create points; 1 - bind actions to point; 2 - deletion mode


class TkExtraWindow:
    def __init__(self, **kwargs):
        self.root = tkinter.Tk()
        try:
            self.root.attributes('-type', 'dialog')
        except:
            pass
        if kwargs["type"] == 0:
            self.root.title("Config robot")
            self.root.geometry("300x100")
            start_coords = kwargs["start_coords"]
            current_robot_direction = kwargs["robot_direction"]
            self.coords_variable = tkinter.StringVar()
            self.coords_variable.set(f"{start_coords[0]}, {start_coords[1]}")
            self.build_base_config()

        elif kwargs["type"] == 1:
            self.root.title("Add actions")
            self.root.geometry("350x200")
            self.build_actions()
        self.root.mainloop()

    def build_base_config(self):
        self.start_point_label = tkinter.Label(
            self.root, text="Start coords(x, y):")
        self.start_point_input = tkinter.Entry(
            self.root, textvariable=self.coords_variable)
        self.start_point_label.grid(row=0, column=0, sticky="w")
        self.start_point_input.grid(row=0, column=1, padx=5, pady=5)
        self.apply_button = tkinter.Button(
            text="Apply", command=lambda: redraw(self.coords_variable))
        self.apply_button.grid(row=1, sticky="nsew")

    def build_actions(self):
        self.actions_list_title = tkinter.Label(
            self.root, text="Actions list", font="Arial 15")
        self.actions_list_title.pack()
        self.actions_box = tkinter.Listbox(selectmode=tkinter.EXTENDED)
        self.actions_box.pack(side=tkinter.LEFT)
        self.actions_scroll = tkinter.Scrollbar(command=self.actions_box.yview)
        self.actions_scroll.pack(side=tkinter.LEFT, fill=tkinter.Y)
        self.actions_box.config(yscrollcommand=self.actions_scroll.set)
        self.actions_frame = tkinter.Frame()
        self.actions_frame.pack(side=tkinter.LEFT, padx=10)
        self.action_name = tkinter.Entry(self.actions_frame)
        self.action_name.pack(anchor=tkinter.N)
        self.add_btn = tkinter.Button(self.actions_frame, text="Add", command=self.add_action)\
            .pack(fill=tkinter.X)
        self.remove_btn = tkinter.Button(self.actions_frame, text="Delete", command=self.remove_action)\
            .pack(fill=tkinter.X)
        self.apply_actions_btn = tkinter.Button(self.actions_frame, text="Apply", command=self.apply_actions)\
            .pack(fill=tkinter.X)

    def add_action(self):
        self.actions_box.insert(tkinter.END, self.action_name.get())
        self.action_name.delete(0, tkinter.END)

    def remove_action(self):
        select = list(self.actions_box.curselection())
        select.reverse()
        for i in select:
            self.actions_box.delete(i)

    def apply_actions(self):
        pass


def redraw(coords, direction):
    global robot, field
    raw = coords.get().split(",")
    x = int(raw[0])
    y = int(raw[1])
    robot.calculate_robot_start_vector((x, y), direction)
    field = cache_field_image.copy()
    cv2.arrowedLine(field, (robot.curr_x, robot.curr_y),
                    (robot.robot_vect_x, robot.robot_vect_y), (0, 0, 255), 5)
    for point in robot.curr_path_points:
        cv2.circle(field, point["point"], 5, (255, 0, 0), -1)
        robot.compute_point(point["point"], field, False)


def interactive_mode_cv(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDBLCLK:
        if EDITING_MODE_ID == 0:
            cv2.circle(field, (x, y), 5, (255, 0, 0), -1)
            print("New point:", x, y)
            robot.compute_point((x, y), field)
        elif EDITING_MODE_ID == 1:
            print(x, y)


def save_path(path, path_name):
    route = [{"action": -1, "start_point": robot.start_point,
              "direction": robot.robot_direction}]
    for point in path:
        route.append(point)
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
    field = cv2.imread(FIELD_IMG_PATH)
    cache_field_image = field.copy()

    print(colored(f"[DEBUG] Field size: {field.shape}", "yellow"))
    one_px = 3000 / field.shape[1]
    print(colored(f"[DEBUG] Px in mms: {one_px}", "yellow"))
    robot_size = 50  # Robot is not a point, it is a non zero vector
    mm_coef = 9.52381  # Dev robot
    rotation_coeff = 12.1  # Dev robot
    robot = Robot(robot_size, START_POINT, ROBOT_DIRECTION, SIDE,
                  mm_coef, rotation_coeff, one_px, 0)

    mode = int(input(
        "Mode (0 - create path; 1 - calculate path; 2 - modify route; 3 - headless execution; 4 - display two routes; 5 - test tk; -1 - exit)>"))

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
                threading.Thread(target=lambda: TkExtraWindow(type=0,
                                                              start_coords=robot.start_point)).start()
            elif k == HOTKEYS[3]:
                if EDITING_MODE_ID == 0:
                    EDITING_MODE_ID = 1
                    #threading.Thread(target=lambda: TkExtraWindow(type=1)).start()
                else:
                    EDITING_MODE_ID = 0

    elif mode == 1:
        name = input(colored("Name for path file>", "yellow"))
        points_dest = load_path(name)
        robot.calculate_robot_start_vector(
            points_dest[0]["start_point"], points_dest[0]["direction"])
        cv2.arrowedLine(field, (robot.curr_x, robot.curr_y),
                        (robot.robot_vect_x, robot.robot_vect_y), (0, 0, 255), 5)
        for instruction in points_dest:
            if instruction["action"] == 1:
                angle, dist = robot.compute_point(instruction["point"], field)
                print(angle, dist)

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
        robot.calculate_robot_start_vector(
            route[0]["start_point"], route[0]["direction"])
        cv2.arrowedLine(field, (robot.curr_x, robot.curr_y),
                        (robot.robot_vect_x, robot.robot_vect_y), (0, 0, 255), 5)
        for instruction in route:
            if instruction["action"] == 1:
                robot.curr_path_points.append(
                    {"action": 1, "point": instruction["point"]})
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
        route_0_path = input("Route #0>")
        route_1_path = input("Route #1>")
        route_0 = load_path(route_0_path)
        route_1 = load_path(route_1_path)

        robot.calculate_robot_start_vector(
            route_0[0]["start_point"], route_0[0]["direction"])
        cv2.arrowedLine(field, (robot.curr_x, robot.curr_y),
                        (robot.robot_vect_x, robot.robot_vect_y), COLOR_ROBOT_0, 5)
        robot_1 = Robot(robot_size, route_1[0]["start_point"], route_1[0]["direction"], SIDE,
                        mm_coef, rotation_coeff, one_px, 0)
        cv2.arrowedLine(field, (robot_1.curr_x, robot_1.curr_y),
                        (robot_1.robot_vect_x, robot_1.robot_vect_y), COLOR_ROBOT_1, 5)

        for instruction in route_0:
            if instruction["action"] == 1:
                robot.compute_point(instruction["point"], field, visualize_color=(
                    15, 15, 145), visualize_vector_color=(0, 0, 255))

        for instruction_1 in route_1:
            if instruction_1["action"] == 1:
                robot_1.compute_point(instruction_1["point"], field, visualize_color=(
                    130, 17, 17), visualize_vector_color=(255, 0, 0))

        # print(colored(
        #    f"Summary:\nDistance: {robot.route_analytics['dist']}mm\nRotations: {robot.route_analytics['rotations']}\nFinal coordinates: {robot.curr_x, robot.curr_y}",
        #    "green"))

        cv2.imshow("Path Gen - Calculated image way", field)

        while True:
            key = cv2.waitKey(20) & 0xFF
            if key == 27:
                cv2.destroyAllWindows()
                break
                exit()

    elif mode == 5:
        threading.Thread(target=lambda: TkExtraWindow(type=0, start_coords=(0, 0), robot_direction=ROBOT_DIRECTION
                                                      )).start()
        # threading.Thread(target=lambda: TkExtraWindow(type=1
        #    )).start()
