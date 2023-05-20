# -*- coding: utf-8 -*-
"""

This is a main file of robots high-level. 

How to run:
    Run without arguments:
        $ python main.py
    We recomend to run it inside `screen session` to avoid process dead, when you disconnects from ssh session.
    Or autostart with provided systemd service config (cherry_bot.service)

Config:
    Config for high-level can be found in `config.py`

Todo:
    * Fix bypass

Created by RobotX team in 2022/2023 years.
"""
import logging
import threading
import socket
import json
from robot import Robot
from config import Config
import spilib
import time
from termcolor import colored
import os
import datetime
from flask import Flask, jsonify, render_template, request
from typing import List
import cv2
#sys.path.append("../../PathFinding")
#from planner import Planner

# Force disable Flask logs (set only for critical - ERROR)
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# Fallback and Init data
GLOBAL_SIDE = Config.SIDE # fallback side
ROUTE_PATH = Config.ROUTE_PATH

# Gripper servos
default_servo_lists = {"grabControl_start": [ [6, 8, 7],
                            [[80, 75, 14]]],

                       "grabControl_end": [[0, 1, 2, 3],
                            [[83,27,177,108],
                             [83,20,160,128]]],

                       "dropControl_start": [[7, 8, 6],
                            [[100, 25, 145]]],
                       
                       "dropControl_end": [[0, 1, 2, 3],
                            [[83,22,73,145]]],

                       "closeGripper": [[4, 5],
                            [[100, 90]]],

                       "openGripper": [[4, 5],
                            [[50, 130]]],
                       "init": [[4, 5, 6, 7, 8], 
                           [[50, 140, 150, 10, 30]]],
                       "up": [[8], [[65]]],

                       "dropGripper": [[3, 4, 5],
                            [[152, 65, 120]]]}


def gripper_servo(servo_list : list,
               pos_list : list,
               spDelay : float = 0.7):
    
    time.sleep(0.07)
    for servo_pos in pos_list:
        for i in range(len(servo_list)):
            spilib.move_servo(servo_list[i], servo_pos[i], 10)
        time.sleep(spDelay)

class WebApi:
    def __init__(self, name, host, port):
        self.app = Flask(name, template_folder="webui/templates",
                         static_url_path='', static_folder='webui/static')
        self.host = host
        self.port = port
        self.app.config["TEMPLATES_AUTO_RELOAD"] = True

        # UI routes
        @self.app.route('/')
        def __index():
            return self.index()

        # API routes
        # AJAX from UI

        @self.app.route('/api/change_config', methods=['POST'])
        def __change_config():
            # Update robot config route
            return self.change_config()

        @self.app.route('/api/get_route_json')
        def __get_route_json():
            # Get current route as json
            return self.get_route_json()

        @self.app.route('/api/update_route', methods=['POST'])
        def __upd_route_json():
            self.update_route()
            return self.get_route_json()

        # Debug(dev) routes

        @self.app.route('/api/debug/info')
        def __debug_info():
            return self.debug_info()

        # Testing routes

        @self.app.route('/api/start_route')
        def __start_route():
            return self.start_route()

        @self.app.route('/api/emergency_stop')
        def __emergency_stop():
            return self.emergency_stop()

        @self.app.route('/joystick')
        def __joystick():
            return self.joystick()

        @self.app.route('/api/controll')
        def controll():
            dir_ = request.args.get("dir")
            steps = int(request.args.get("steps"))
            if dir_ == "backward":
                dir_ = "forward"
                steps = -steps
            spilib.move_robot(dir_, 1, distance=steps)
            return "1"

        @self.app.route('/api/actuator/trick')
        def make_trick():
            if GLOBAL_SIDE == "blue":
                spilib.led_fill(0, 92, 230)
            elif GLOBAL_SIDE == "green":
                spilib.led_fill(0, 230, 92)
            return jsonify({"status": True})

        @self.app.route('/api/actuator/trick_clear')
        def trick_clear():
            spilib.led_clear()
            return jsonify({"status": True})

        @self.app.route('/api/actuator/set_prediction')
        def set_prediction():
            try:
                new_prediction = int(request.args.get("cnt", default=51)) 
            except ValueError:
                new_prediction = 51 # Fallback to stable prediction
            spilib.change_prediction(new_prediction)
            return jsonify({"status": True})

    def joystick(self):
        return render_template("joystick.html")
    
    def shutdown(self):
        '''
        Turn off Flask Server
        '''
        exit(0)  # It will kill only this thread

    def run(self):
        logger.write(
            "WEB", "INFO", f"Starting WebAPI on {self.host}:{self.port}")
        self.app.run(host=self.host, port=self.port)

    def index(self):
        global GLOBAL_SIDE
        return render_template("index.html", route_path=ROUTE_PATH, start_point=robot.start_point, strategy_id=Config.STRATEGY_ID,
                               execution_status=False, use_strategy_id=int(Config.USE_STRATEGY_ID),
                               robot_id=Config.ROBOT_ID, local_ip=socket.gethostbyname(socket.gethostname()), polling_interval=Config.JS_POLLING_INTERVAL,
                               web_port=Config.FLASK_PORT, side=GLOBAL_SIDE)

    def debug_info(self):
        return jsonify({"CTD": "Disconnected",
                        "log_file": logger.log_name,
                        "position": {
                            "x,y": (robot.curr_x, robot.curr_y),
                            "vector_x": robot.robot_vect_x,
                            "vector_y": robot.robot_vect_y
                        },
                        "logged_points": motors_controller.logged_points
                        })

    def start_route(self):
        launch()
        return jsonify({"status": True})

    def change_config(self):
        global GLOBAL_SIDE, route, robot, ROUTE_PATH
        GLOBAL_SIDE = request.form.get("robot_side")
        ROUTE_PATH = request.form.get("route_path") 
        
        route = interpreter.load_route_file(ROUTE_PATH, GLOBAL_SIDE)
        # Reload and reprocess route file
        # Load task header, with some config (init coords and vector)
        route_header = interpreter.preprocess_route_header(route)
        # Calculate current robot vector, based on start coordinates and direction.
        logger.write("TMGR", "INFO", "Applying robot position to model")
        robot.calculate_robot_start_vector(route_header[0], route_header[1])
        return {"status": True}


    def update_route(self):
        route = json.loads(request.data.decode('utf-8'))

    def get_route_json(self):
        return {"status": True, "data": route}

# @legacy
class LocalCamera:
    '''
    Class to handle local camera on robot
    '''

    def __init__(self, camera_id=Config.CAMERA_ID):
        self.camera = cv2.VideoCapture(camera_id)

    def get_frame(self):
        st, frame = self.camera.read()
        return frame

    def release_camera(self):
        pass


class Logger:
    '''
    Project-wide service to log match events into log file and terminal (later)
    '''

    def __init__(self):
        self.base_dir = Config.LOGS_DIRECTORY
        self.start_log()  # create self.current_log_space
        self.log_name = None
        self.current_match_id = -1  # Increment, so, minimum is 0
        self.stdout_enabled = True
        self.color_mapping = {
            "INFO": "cyan",
            "ERROR": "red",
            "WARN": "yellow",
            "SUCCESS": "green",
            "DEBUG": "magenta"
        }

    def start_log(self) -> None:
        # Create log folder for current run
        time_ = self.get_time('%H_%M_%S.%m_%d')
        unix_time, parsed = time_["unix_time"], time_["display"]
        self.current_log_space = os.path.join(
            self.base_dir, f"{unix_time}_run_at_{parsed}")
        os.mkdir(self.current_log_space)
        # Create sys_log file
        with open(os.path.join(self.current_log_space, "sys.log"), "w") as fd:
            init_time = self.get_time()
            fd.write(self.gen_string(
                init_time["display"], "LOGGER", "INFO", "Logger started!"))

    def get_time(self, format_: str = '%H:%M:%S') -> dict:
        '''
        Get current unix time and convert it to human-readable H:M:S
        '''
        unix_time = int(time.time())
        readable_time = datetime.datetime.utcfromtimestamp(
            unix_time).strftime(format_)
        return {"unix_time": unix_time, "display": readable_time}

    def gen_string(self, time: int, service_name: str, type_: str, message: str) -> str:
        '''
        Generate log string with such format:
        [time][service_name][type] message
        '''
        return f"[{time}][{service_name}][{type_}] {message}\n"

    def new_match(self) -> None:
        '''
        Initalize log file for new match
        '''
        self.current_match_id += 1
        os.mkdir(os.path.join(self.current_log_space,
                 f"match_{self.current_match_id}"))
        time_ = self.get_time()
        with open(os.path.join(self.current_log_space, f"match_{self.current_match_id}", "runtime.log"), "w") as fd:
            fd.write(self.gen_string(
                time_["display"], "LOGGER", "INFO", "Match started!"))

    def write(self, service_name: str, type_: str, message: str, log_to="sys") -> None:
        '''
        Generate string and append it to log file
        '''
        log_path = os.path.join(self.current_log_space, "sys.log") if log_to == "sys" else os.path.join(
            self.current_log_space, f"match_{self.current_match_id}", "runtime.log")
        time_ = self.get_time()
        log_string = self.gen_string(
            time_["display"], service_name, type_, message)
        with open(log_path, "a") as fd:
            fd.write(log_string)
        if self.stdout_enabled:
            if type_ in self.color_mapping:
                log_color = self.color_mapping[type_]
            else:
                log_color = ""
            print(colored(log_string, log_color), end="")


class PointsManager:
    '''
    This service dynamicly calculates gained points.
    How it works:
    * Each robot calculates local points for his actions, like building cake.
    * We have main robot, that will get points from second robot.
    '''

    def __init__(self) -> None:
        self.local_mapping = {
            "parking": 15,
            "funny_action": 5
        }
        self.curr_points = 0

    def __str__(self):
        return f"Current points: {self.curr_points}"

    def calculate_cake(self, layers_count: int, legendary: bool) -> int:
        pass


class TaskManager:
    '''
    You can think, that this is core service of this robot. But... no. I can't select CORE service. This code is full of democracy.
    '''

    def __init__(self):
        logger.write("TMGR", "INFO", "TaskManager ready!")

    def match(self, tasks: List[dict]):
        self.match_start_time = time.time()
        # Synchronous tasks execution
        logger.write("TMGR", "INFO", "Starting tasks execution loop")
        # Clear logged points for new match
        motors_controller.logged_points = []
        for task in tasks[1:]:
            logger.write(
                "TMGR", "INFO", f"Executing new task from route: {task}", log_to="match")
            # Block process here
            interpreter.process_instruction(task)
        self.match_finish_time = time.time()
        logger.write("TMGR", "SUCCESS", "All tasks finished! Match finished!")
        logger.write(
            "TMGR", "INFO", f"Logged points: {motors_controller.logged_points}", log_to="match")
        logger.write(
            "TMGR", "INFO", f"Match duration (seconds): {self.match_finish_time - self.match_start_time}", log_to="match")
        logger.write("TMGR", "INFO", f"Distance: N/A", log_to="match")
        logger.write("TMGR", "INFO", f"Points gained: N/A", log_to="match")


class MotorsController:
    '''
    Drive from point A (current) to point B
    Bypass obstacles or stopping in front of them (data from lidar).
    '''

    def __init__(self):
        self.logged_points = []
        logger.write("MOTORS", "INFO", "Motors controller ready!")

    def drive(self, point: tuple, bypass_obstacles: bool = False) -> None:
        '''
        Function to move robot from current point to another.
        Alss, this function checking osbtacles and trying to bypass them.
        '''
        logger.write("MOTORS", "INFO",
                     f"Planning to drive to {point}", log_to="match")
        self.logged_points.append(point)
        angle, dist = robot.compute_point(point, [], visualize=False)
        # Rotate to get correct vector in real life
        if angle != 0:
            direction = "right"
            if angle < 0:
                direction = "left"
            spilib.move_robot(direction, False, distance=abs(
                int(angle * robot.rotation_coeff)))
            # move to a callback
            while True:
                recieved = spilib.spi_send([])
                if (recieved[0] == 0 and recieved[1] == 0):
                    break
                time.sleep(0.05)
        # Move forward
        dist = int(robot.mm_coef * dist)
        spilib.move_robot("forward", False, distance=dist)
        print("Driving to dist: ", dist)
        while True:
            # Checking for obstacles on the way by data from CTD
            recieved = spilib.spi_send([])  # get robot status
            #print(recieved)
            #front_lidar = recieved[6]
            #print(front_lidar)
            if (recieved[0] == 0 and recieved[1] == 0):  # motors stopped; step finished
                break  # Go for next step

            # Process lidar data example hook
            if (recieved[8]):
                pass
            time.sleep(1)  # FIXIT Why we use it here?


class Interpreter:
    def __init__(self):
        self.local_variables = {}  # pull of local variables, that used in RoboScript route
        self.if_cond = 0  # 0 - no conditions; 1 - true condition; 2 - false condition
        logger.write("RoboScript", "INFO", "Interpreter ready!")

    def process_instruction(self, task: dict) -> None:
        global GLOBAL_SIDE
        if task["action"] in [0, "log"]:
            '''
            Debug/log to stdout
            '''
            print(task["content"])
        elif task["action"] in [1, "forward", "drive"]:
            '''
            Drive to point
            '''
            motors_controller.drive(task["point"])
        elif task["action"] == [2, "servo"]:
            '''
            Move servo to another angle with specified speed
            '''
            if "speed" in task:
                speed = task["speed"]
            else:
                speed = 10
            spilib.move_servo(task["id"], task["angle"], speed)
            time.sleep(2)
        elif task["action"] in [3, "delay"]:
            '''
            Wait for some time on interpeter level.
            '''
            if "seconds" in task:
                time.sleep(task["seconds"])
            else:
                print(colored(
                    "[ERROR][RoboScript] Processing error; no `seconds` value in task", "red"))
        elif task["action"] in [4, "backward"]:
            '''
            Move robot backward. This function will move robot backward, but we will save robot origin vector and change only coordinates.
            Also, this function supports extra_dist to coolibrate robot using field bumpers. Extra_dist in mms.
            '''
            if "back_point" in task:
                point = task["back_point"]
                angle, dist = robot.compute_point(
                    point, [], visualize=False, change_vector=False)
                angle = 0
                dist *= robot.mm_coef
                if "extra_force" in task:
                    dist += int(task["extra_force"] * robot.mm_coef)
                spilib.move_robot("forward", False, distance=-int(dist))
            else:
                # FIXIT Match Runtime log
                logger.write("RoboScript", "ERROR",
                             "Processing error; no `back_point` value in task")
        elif task["action"] in [5, "set_var"]:
            '''
            Set some value to some variable.
            '''
            self.local_variables[task["name"]] = task["value"]
        elif task["action"] in [6, "log_var"]:
            '''
            Print var value to stdout
            '''
            print("Dbg")
        elif task["action"] in [7, "if"]:
            '''
            If condition
            '''
            if not "current_value" in task:
                print(colored(
                    "[ERROR][RoboScript] Processing error; no `current_value` value in task", "red"))
                exit(1)
            if not "compare_with" in task:
                print(colored(
                    "[ERROR][RoboScript] Processing error; no `compare_with` value in task", "red"))
                exit(1)

            if type(task["current_value"]) == int:
                val_to_check = task["current_value"]
            else:
                if task["current_value"] in self.local_variables:
                    val_to_check = self.local_variables[task["current_value"]]
                else:
                    print(colored(
                        f"[ERROR][RoboScript] Runtime error; variable {task['current_value']} not inited", "red"))
                    exit(1)

            val_to_compare_with = task["compare_with"]
            if val_to_check == val_to_compare_with:
                self.if_cond = 1
            else:
                self.if_cond = 2
        elif task["action"] in [8, "else"]:
            '''
            Else for if condition
            '''
            pass

        elif task["action"] in [9, "endif"]:
            '''
            Close if conditional
            '''
            self.if_cond = 0

        elif task["action"] in [10, "prediction"]:
            pass

        elif task["action"] in ["front_lidar_get"]:
            pass

        elif task["action"] in ["trick"]:
            if GLOBAL_SIDE == "blue":
                spilib.led_fill(0, 92, 230)
            elif GLOBAL_SIDE == "green":
                spilib.led_fill(0, 230, 92)
        elif task["action"] in ["prediction"]:
            spilib.change_prediction(task["points"])
        elif task["action"] == "open_gripper":
            #gripper_servo(default_servo_lists["openGripper"][0], default_servo_lists["openGripper"][1])
            spilib.move_servo(4, 50, 10)
            spilib.move_servo(5, 140, 10)
        elif task["action"] == "close_gripper":
            gripper_servo(default_servo_lists["closeGripper"][0], default_servo_lists["closeGripper"][1])
        elif task["action"] == "gripper_init":
            gripper_servo(default_servo_lists["init"][0], default_servo_lists["init"][1])
        elif task["action"] == "gripper_grab_start":
            gripper_servo(default_servo_lists["grabControl_start"][0], default_servo_lists["grabControl_start"][1])
        elif task["action"] == "gripper_grab_pos":
            gripper_servo(default_servo_lists["dropControl_start"][0], default_servo_lists["dropControl_start"][1])


    def preprocess_route_header(self, route: List[dict]) -> tuple:
        header = route[0]
        if header["action"] == -1:  # Header action
            return tuple(header["start_point"]), header["direction"]

    def load_route_file(self, path: str, side: str) -> List[dict]:
        with open(path) as f:
            route = json.load(f)
        route_new = []
        if side == "green": # Reload angles
            for task in route:
                if task["action"] in [1, "drive"]:
                    route_new.append({"action": "drive", "point": task})
                else:
                    route_new.append(task)
        return route


class MapServer:
    '''
    MapServer - Service to store and fetch actual info of field from CTD. Store 4 points - 4 robots coords.
    robot_coords = [(this_robot), (second_robot), (enemy_0), (enemy_1)]
    '''

    def __init__(self, camera_tcp_host="localhost", camera_tcp_port=7070, updater_autorun=True):
        # INIT STATE; -1; -1; no robots on map
        self.robots_coords = [[-1, -1], [-1, -1], [-1, -1], [-1, -1]]
        self.camera_host = camera_tcp_host
        self.camera_port = camera_tcp_port
        self.camera_socket = None
        logger.write("MapServer", "INFO", "Connecting to camera tcp...")
        if Config.CONNECT_CTD:
            connected = self.connect_ctd()  # Connect to tcp camera socket
            if connected:
                self.updater_enabled = True
                if updater_autorun:
                    logger.write(
                        "MapServer", "INFO", "Starting realtime coords updater in another thread...")
                    self.updater_thread = threading.Thread(
                        target=lambda: self.updater())
                    self.updater_thread.start()
            else:
                logger.write("MapServer", "ERROR", "Can't connect to camera tcp")
        else:
            logger.write("MapServer", "ERROR", "Connection to map server disabled")

    def send_payload(self, data):
        '''
        High-level wrapper of socket send to support json payload. Serialize json/dict to string and encode to binary utf-8.
        '''
        dt_converted = json.dumps(data).encode("utf-8")
        self.camera_socket.send(dt_converted)
    
    def camera_auth(self):
        '''
        This methods sends data to CTD to get permission to get robots coords. Send this packet before others.
        '''
        self.send_payload({"action": 0, "robot_id": 0})  # no realtime robot id

    def connect_ctd(self):
        '''
        Connect to CTD camera tcp socket and store connection in self. 
        WARN! Run in __init__, before updater thread run!
        '''
        try:
            self.camera_socket = socket.socket(
                socket.AF_INET, socket.SOCK_STREAM)
            self.camera_socket.connect((self.camera_host, self.camera_port))
            self.camera_auth()
            return True
        except ConnectionRefusedError:
            return False

    def updater(self):
        while self.updater_enabled:
            data_raw = self.camera_socket.recv(2048)
            try:
                data = json.loads(data_raw.decode("utf-8"))
            except:
                data = {}  # null data; for error handling on corrupted json payload
            if data and data["action"] == 3:
                self.robots_coords = data["robots"].copy()

    def shutdown(self):
        self.updater_enabled = False
        self.camera_socket.close()

    def __str__(self):
        '''
        Pretty print for debug
        '''
        current_robot_coords = self.robots_coords[Config.ROBOT_ID]
        second_robot_coords = self.robots_coords[int(not Config.ROBOT_ID)]
        rival_0_coords = self.robots_coords[2]
        rival_1_coords = self.robots_coords[3]
        return f"{colored(f'This robot: {current_robot_coords}', 'green')}\n{colored(f'Second: {second_robot_coords}', 'green')}\n{colored(f'Rival #0: {rival_0_coords}', 'yellow')}\n{colored(f'Rival #1: {rival_1_coords}', 'yellow')}"


def launch():
    '''
    Wrapper to start robot match execution program.
    Start logger and route execution (task manager active loop).
    '''
    logger.new_match()
    task_manager.match(route)


def robot_configure():
    '''
    Configure robot
    '''
    pass


if __name__ == "__main__":
    # Clear robot color
    spilib.led_clear()
    # Init logger service.
    logger = Logger()
    # Init map service; Offline navigation
    # map_server = MapServer(camera_tcp_host=Config.SOCKET_SERVER_HOST, camera_tcp_port=Config.SOCKET_SERVER_PORT)
    # Init robot physical/math model service
    robot = Robot(Config.ROBOT_SIZE, Config.START_POINT, Config.ROBOT_DIRECTION, Config.SIDE,
                  Config.MM_COEF, Config.ROTATION_COEFF, Config.ONE_PX, 1)
    # Init interpreter service
    interpreter = Interpreter()
    # Load init route from path provided in config
    route = interpreter.load_route_file(Config.ROUTE_PATH, GLOBAL_SIDE)
    # Load task header, with some config (init coords and vector)
    route_header = interpreter.preprocess_route_header(route)
    # Calculate current robot vector, based on start coordinates and direction.
    logger.write("TMGR", "INFO", "Applying robot position to model")
    robot.calculate_robot_start_vector(route_header[0], route_header[1])
    # Init motors controller service
    motors_controller = MotorsController()
    # Init planner service; Offline navigation
    #planner = Planner(3.0, 2.0, 70, logger)
    # Init && start task manager match mode
    task_manager = TaskManager()
    # Init && start web api/ui service
    web_api = WebApi(__name__, Config.FLASK_HOST, Config.FLASK_PORT)
    threading.Thread(target=lambda: web_api.run()).start() 
    gripper_servo(default_servo_lists["init"][0], default_servo_lists["init"][1])
    gripper_servo(default_servo_lists["closeGripper"][0], default_servo_lists["closeGripper"][1])
    gripper_servo(default_servo_lists["dropControl_start"][0], default_servo_lists["dropControl_start"][1])



    while True: # Wait for starter in main loop; Shit code
        if (bool(spilib.low_digitalRead_echo(25))): # Read starter pin from spi; If pin released -> Start Match
            print("Start!")
            launch()
            break

    #while True:
    #    print("Hang up code")
    # Shutdown high-level
    #map_server.shutdown()
    web_api.shutdown()
    while True: pass
    print("Goodbye...")

    # Debug is absolute
    if Config.DBG_CONSOLE_ENABLED:
        while True:
            command = input("DBG>")
            if command == "off":
                print("Safe shutting down...")
                map_server.shutdown()
                web_api.shutdown()
                exit(0)
            elif command == "launch":
                print("Starting")
                launch()

    # Start match execution
    # launch()
