from robot import Robot
from config import *
import json
import time
from multiprocessing import Process, Manager
import spilib
import logging
from socket_service import SocketService
from flask import Flask, render_template, jsonify, request
from webui_service import WebUI

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)


class SensorsService:
    def __init__(self):
        pass

    def update_share_data(self, share_data):
        self.share_data = share_data

    def read_loop(self):
        '''
        Not for all time. Works only on start. Make sure not to send multiple spi packets at one time
        '''
        while True:
            # change to spilib.get_sensors_data when on real robot
            sensors_data = spilib.fake_req_data()
            # print(sensors_data)
            if sensors_data[4] == 1:
                if self.share_data["execution_status"] == 0:
                    print("Starting")
                    # send start request
                    self.share_data["execution_status"] = 1
                    break


class Interpreter:
    global robot

    def __init__(self):
        self.local_variables = {}

    def update_share_data(self, share_data):
        self.share_data = share_data

    def interpet_step(self, instruction):
        self.share_data["step_executing"] = True
        if instruction["action"] == 0:
            # Reserved for high-level functions
            if instruction["sub_action"] == 0:
                # Reserved for loggging file
                pass
            elif instruction["sub_action"] == 1:
                # Reserved for stdout printing debug info
                pass

        elif instruction["action"] == 1:
            final_point = instruction["point"]
            if robot.side == 1:
                final_point[0] = robot.field_size_px[1] - final_point[0]
            try:
                #print("Driving to", final_point)

                status, going_time, dist_drived = robot.go(final_point)
                '''monitoring_dict["steps_done"] += 1
                monitoring_dict["steps_left"] = steps_cnt - \
                    monitoring_dict["steps_done"]
                monitoring_dict["distance_drived"] += dist_drived
                monitoring_dict["motors_time"] += going_time'''
            except FileNotFoundError:  # Handle spi error
                print("[DEBUG] Warning! Invalaid SPI connection")
                time.sleep(20)
        elif instruction["action"] == 2:
            # Reserved for servo
            pass
        elif instruction["action"] == 3:
            # Delay on high-level
            time.sleep(instruction["seconds"])
        elif instruction["action"] == 4:
            # Backward driving
            point = instruction["back_point"]
            #print("Driving to", point)

            angle, dist = robot.compute_point(
                point, [], visualize=False, change_vector=False)

            angle = 0
            dist *= robot.mm_coef
            dist += int(instruction["extra_force"] * robot.mm_coef)
            # Move to robot class FIXIT
            spilib.move_robot("forward", False, distance=-int(dist))
        elif instruction["action"] == "set_var":
            self.local_variables[instruction["var_name"]] = instruction["var_value"]

        elif instruction["action"] == "check_aruco":
            pass
        # Sync robot coords and vector with taskmanager thread
        self.share_data["robot_coords"] = (robot.curr_x, robot.curr_y)
        self.share_data["robot_vect"] = (
            robot.robot_vect_x, robot.robot_vect_y)
        self.share_data["step_executing"] = False

    def preprocess_route_header(self, route):
        header = route[0]
        if header["action"] == -1:  # Header action
            return tuple(header["start_point"])

    def load_route_file(self, path):
        with open(path) as f:
            route = json.load(f)
        return route


class TaskManager:
    def __init__(self):
        '''
        Works every time without freezing. If it hangs, robot will die)
        '''
        self.time_start = 0
        self.emergency_time = 100
        self.step_id = 0
        self.processes = {"web": None, "interpreter": None,
                          "sensors": None, "socketclient": None}
        self.processes_manager = Manager()
        self.share_dict = self.processes_manager.dict()
        # Default start values
        self.share_dict["execution_status"] = 0
        self.share_dict["step_executing"] = False
        self.share_dict["goal_point"] = 0
        self.share_dict["robot_coords"] = (robot.curr_x, robot.curr_y)
        self.share_dict["robot_vect"] = (
            robot.robot_vect_x, robot.robot_vect_y)
        self.share_dict["socket_authenticated"] = False
        self.share_dict["current_route_data"] = {"start_point": robot.start_point, "route_path": ROUTE_PATH, "strategy_id": STRATEGY_ID, "use_strategy_id": int(USE_STRATEGY_ID), "side": SIDE, "robot_id": ROBOT_ID, "robot_dir": ROBOT_DIRECTION}
        
    def mainloop(self):
        global route, robot
        while True:
            if self.share_dict["execution_status"] == 1:  # start
                route = interpreter.load_route_file(ROUTE_PATH)
                print("[DEBUG] Start execution")
                self.step_id = 0
                self.share_dict["execution_status"] = 2
                self.time_start = time.time()
            elif self.share_dict["execution_status"] == 2:  # execution is going now
                time_gone = time.time() - self.time_start
                if time_gone >= self.emergency_time:
                    # Use local planner to build way (?) FIXIT
                    print("[DEBUG] Return back")
                    print(f"Current coords: {self.share_dict['robot_coords']}")
                    try:
                        spilib.stop_robot()
                    except FileNotFoundError: # spi error
                        print("[FATAL] Can't stop robot")
                    self.share_dict["execution_status"] = 0
                    self.kill_process("interpreter")
                else:
                    if self.step_id < len(route):
                        if not self.share_dict["step_executing"]:
                            self.start_process(
                                type="interpreter", process_class=interpreter, step=route[self.step_id])
                            self.share_dict["goal_point"] = route[self.step_id] # update our goal point
                            self.step_id += 1
                            
                            time.sleep(0.1)
                    else:
                        print("[DEBUG] Execution queue finished")
                        # Execution finished
                        self.share_dict["execution_status"] = 0
                        self.share_dict["goal_point"] = (-1, -1)
            elif self.share_dict["execution_status"] == 3:  # Kill interpreter process and stop robot
                self.kill_process("interpreter")
                spilib.stop_robot()
                self.share_dict["execution_status"] = 0
                self.share_dict["step_executing"] = False
                print("Robot stopped")

    def start_process(self, **kwargs):
        try:
            if kwargs["type"] == "web":
                kwargs["process_class"].update_share_data(self.share_dict)
                self.processes["web"] = Process(
                    target=lambda: kwargs["process_class"].run())
                self.processes["web"].start()
            elif kwargs["type"] == "interpreter":
                kwargs["process_class"].update_share_data(self.share_dict)
                self.processes["interpreter"] = Process(
                    target=lambda: kwargs["process_class"].interpet_step(kwargs["step"]))
                robot.curr_x, robot.curr_y = self.share_dict[
                    "robot_coords"][0], self.share_dict["robot_coords"][1]
                robot.robot_vect_x, robot.robot_vect_y = self.share_dict[
                    "robot_vect"][0], self.share_dict["robot_vect"][1]
                self.processes["interpreter"].start()
            elif kwargs["type"] == "sensors":
                kwargs["process_class"].update_share_data(self.share_dict)
                self.processes["sensors"] = Process(
                    target=lambda: kwargs["process_class"].read_loop())
                self.processes["sensors"].start()
            elif kwargs["type"] == "socketclient":
                kwargs["process_class"].update_share_data(self.share_dict)
                kwargs["process_class"].auth()
                self.processes["socketclient"] = Process(
                    target=lambda: kwargs["process_class"].listen_loop())
                self.processes["socketclient"].start()

            return 1
        except Exception as e:
            print(f"[FAILED] To start process\nError: {e}")
            return -10

    def kill_process(self, process_name):
        if self.processes[process_name] and process_name in self.processes:
            self.processes[process_name].terminate()
            self.processes[process_name] = None
            return 100  # Process killed
        else:
            return -100  # No such process


if __name__ == "__main__":
    interpreter = Interpreter()
    monitoring_dict = {"steps_done": 0, "steps_left": 0,
                       "distance_drived": 0, "motors_time": 0, "start_time": 0}
    route = interpreter.load_route_file(ROUTE_PATH)
    START_POINT = interpreter.preprocess_route_header(route)
    robot = Robot(ROBOT_SIZE, START_POINT, ROBOT_DIRECTION, SIDE,
                  MM_COEF, ROTATION_COEFF, ONE_PX, 1)  # Start robot in real mode
    web_ui = WebUI(__name__, FLASK_HOST, FLASK_PORT)
    sensors = SensorsService()
    tmgr = TaskManager()
    connected = False
    attempts = 0
    while not connected and attempts <= 5:
        try:
            socketclient = SocketService(
                SOCKET_SERVER_HOST, SOCKET_SERVER_PORT, ROBOT_ID)
            tmgr.start_process(type="socketclient", process_class=socketclient)
            connected = True
        except:
            print("[WARN] Can't connect to CTD socket server. Retrying...")
            attempts += 1
            time.sleep(1)
    if not connected:
        print("[FATAL] No connection with CTD")
    tmgr.start_process(type="web", process_class=web_ui)
    # tmgr.start_process(type="sensors", process_class=sensors) Disable for some time
    
    tmgr.mainloop()
