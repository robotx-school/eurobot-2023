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
from typing import List
import sys
sys.path.append("../../PathFinding")
from planner import Planner


class Logger:
    '''
    Project-wide service to log match events into log file and terminal (later)
    '''
    def __init__(self):
        self.dir = Config.LOGS_DIRECTORY

    def get_time(self) -> dict:
        '''
        Get current unix time and convert it to human-readable H:M:S
        '''
        unix_time = int(time.time())
        readable_time = datetime.datetime.utcfromtimestamp(unix_time).strftime('%H:%M:%S')
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
        time_ = self.get_time()
        #strategy_name = Config.ROUTE_PATH.split(".")
        strategy_name = "developer_pursuit" # develop log name
        self.log_name = f"{time_['unix_time']}_{strategy_name}.log"
        with open(os.path.join(self.dir, self.log_name), "w") as fd:
            fd.write(self.gen_string(time_["display"], "LOGGER", "INFO", "Match started!"))

    def write(self, service_name: str, type_: str, message: str) -> None:
        '''
        Generate string and append it to log file
        '''
        time_ = self.get_time()
        with open(os.path.join(self.dir, self.log_name), "a") as fd:
            fd.write(self.gen_string(time_["display"], service_name, type_, message))

class TaskManager:
    '''
    You can think, that this is core service of this robot. But... no. I can't select CORE service. This code is full of democracy.
    '''
    def __init__(self):
        pass

    def match(self, tasks: List[dict]):
        # Synchronous tasks execution
        for task in tasks[1:]:
            logger.write("TMGR", "INFO", "Executing new task from route")
            # Block process here
            interpreter.process_instruction(task)
        print("[DEBUG][TMGR] Tasks pull empty.")
        print(motors_controller.logged_points)
        logger.write("TMGR", "INFO", "All steps done. Match finished!")

class MotorsController:
    '''
    Drive from point A (current) to point B
    Bypass obstacles or stopping in front of them (data from lidar).
    '''
    def __init__(self):
        self.logged_points = []

    def drive(self, point: tuple, bypass_obstacles: bool = True) -> None:
        '''
        Function to move robot from current point to another.
        Alss, this function checking osbtacles and trying to bypass them.
        '''
        logger.write("MOTORS", "INFO", f"Planning to drive to {point}")
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
        while True:
            # Checking for obstacles on the way by data from CTD
            if bypass_obstacles:
                other_robots = map_server.robots_coords.copy()
                other_robots.pop(Config.ROBOT_ID) # delete current robot coords from potentional obstacles
                this_robot_coordinates = map_server.robots_coords[Config.ROBOT_ID]
                #print(other_robots, this_robot_coordinates, point)
                obstacle_on_the_way = planner.check_obstacle(other_robots, this_robot_coordinates, point)
                # FIXIT
                # Handle situation: we have obstacle on the way, but planner can't generate bypass way.
                # In this case, I think we will wait for some time, trying to generate bypass route
                if obstacle_on_the_way[0]:
                    self.logged_points.pop() # Delete last point from log
                    print(colored("[INFO][MOTORS] OBSTACLE", "red"))
                    logger.write("MOTORS", "WARN", "Obstacle on the way. Trying to bypass")
                    spilib.spi_send([1, 0, 0]) # emergency stop
                    time.sleep(0.2) # wait for motors to stop
                    distance_to_obstacle = ((this_robot_coordinates[0] - obstacle_on_the_way[1][0]) ** 2 + (
                        this_robot_coordinates[1] - obstacle_on_the_way[1][1]) ** 2) ** 0.5
                    #print("Obstacles on the way\nDistance to obstacle:", distance_to_obstacle * self.one_px)
                    converted_obstacles = [[int(obstacle[0] * planner.virtual_map_coeff), int(
                        obstacle[1] * planner.virtual_map_coeff)] for obstacle in other_robots]
                    dt_for_planner = [int(this_robot_coordinates[0] * planner.virtual_map_coeff), int(this_robot_coordinates[1] * planner.virtual_map_coeff)], [
                        int(point[0] * planner.virtual_map_coeff), int(point[1] * planner.virtual_map_coeff)]
                    bp = planner.generate_way(
                        *dt_for_planner, converted_obstacles)
                    print(colored(f"[DEBUG][MOTORS] Bypass way: {bp}", "magenta"))
                    # Sync current robot coordinates with real from CTD
                    robot.curr_x = this_robot_coordinates[0]
                    robot.curr_y = this_robot_coordinates[1]
                    robot.generate_vector()
                    logger.write("MOTORS", "INFO", "Starting bypass route")
                    for step in bp[1]:
                        self.drive(step, bypass_obstacles=False) # FIXIT # This disble recursive obstacles bypass, when we have to bypass obstacles on bypass route.
                    logger.write("MOTORS", "INFO", "Obstacle passed")
                    #robot.curr_x = point[0]
                    #robot.curr_y = point[1]
                    #robot.generate_vector()

            recieved = spilib.spi_send([]) # get robot status
            if (recieved[0] == 0 and recieved[1] == 0): # motors stopped; step finished
                break # Go for next step

            # Process lidar data example hook
            if (recieved[8]):
                pass
            time.sleep(0.05) # FIXIT Why we use it here?

class Interpreter:
    def __init__(self):
        self.local_variables = {} # pull of local variables, that used in RoboScript route
        self.if_cond = 0  # 0 - no conditions; 1 - true condition; 2 - false condition

    def process_instruction(self, task: dict) -> None:
        if task["action"] in [0, "log"]:
            '''
            Debug/log to stdout
            '''
            print(task["content"])
        elif task["action"] in [1, "drive"]:
            '''
            Drive to point
            '''
            motors_controller.drive(task["point"])
        elif task["action"] == 2:
            '''
            Move servo to another angle with specified speed
            '''
            # FIXIT
            # Write move_servo code here...
            pass
        elif task["action"] in [3, "delay"]:
            '''
            Wait for some time on interpeter level.
            '''
            if "seconds" in task:
                time.sleep(task["seconds"])
            else:
                print(colored("[ERROR][RoboScript] Processing error; no `seconds` value in task", "red"))
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
                print(colored("[ERROR][RoboScript] Processing error; no `back_point` value in task", "red"))
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
                print(colored("[ERROR][RoboScript] Processing error; no `current_value` value in task", "red"))
                exit(1)
            if not "compare_with" in task:
                print(colored("[ERROR][RoboScript] Processing error; no `compare_with` value in task", "red"))
                exit(1)

            if type(task["current_value"]) == int:
                val_to_check = task["current_value"]
            else:
                if task["current_value"] in self.local_variables:
                    val_to_check = self.local_variables[task["current_value"]]
                else:
                    print(colored(f"[ERROR][RoboScript] Runtime error; variable {task['current_value']} not inited", "red"))
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
            self.if_cond = 0

        elif task["action"] in [9, "endif"]:
            '''
            Close if conditional
            '''
            self.if_cond = 0

    def preprocess_route_header(self, route: List[dict]) -> tuple:
        header = route[0]
        if header["action"] == -1:  # Header action
            return tuple(header["start_point"]), header["direction"]

    def load_route_file(self, path: str) -> List[dict]:
        with open(path) as f:
            route = json.load(f)
        return route

class MapServer:
    '''
    MapServer - Service to store and fetch actual info of field from CTD. Store 4 points - 4 robots coords.
    robot_coords = [(this_robot), (second_robot), (enemy_0), (enemy_1)]
    '''
    def __init__(self, camera_tcp_host="localhost", camera_tcp_port=7070, updater_autorun=True):
        self.robots_coords = [[-1, -1], [-1, -1], [-1, -1], [-1, -1]] # INIT STATE; -1; -1; no robots on map
        self.camera_host = camera_tcp_host
        self.camera_port = camera_tcp_port
        self.camera_socket = None
        self.connect_ctd() # Connect to tcp camera socket
        self.updater_enabled = True
        if updater_autorun:
            self.updater_thread = threading.Thread(target=lambda: self.updater())
            self.updater_thread.start()


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
        self.send_payload({"action": 0, "robot_id": 0}) # no realtime robot id

    def connect_ctd(self):
        '''
        Connect to CTD camera tcp socket and store connection in self. 
        WARN! Run in __init__, before updater thread run!
        '''
        self.camera_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.camera_socket.connect((self.camera_host, self.camera_port))
        self.camera_auth()
    def updater(self):
        while self.updater_enabled:
            data_raw = self.camera_socket.recv(2048)
            try:
                data = json.loads(data_raw.decode("utf-8"))
            except:
                data = {}  # null data; for error handling on corrupted json payload
            if data and data["action"] == 3: 
                self.robots_coords = data["robots"].copy()

    def __str__(self):
        '''
        Pretty print for debug 
        FIXIT
        ''' 
        return f"This robot: {self.robots_coords[0][0]}, {self.robots_coords[0][1]}"

def launch():
    '''
    Wrapper to start robot match execution program.
    Start logger and route execution (task manager loop).
    '''
    logger.new_match()
    task_manager.match(route)

if __name__ == "__main__":
    # Init map service
    map_server = MapServer()
    # Init robot physical/math model service
    robot = Robot(Config.ROBOT_SIZE, Config.START_POINT, Config.ROBOT_DIRECTION, Config.SIDE,
                      Config.MM_COEF, Config.ROTATION_COEFF, Config.ONE_PX, 1)
    # Init interpreter service
    interpreter = Interpreter()
    # Load task
    route = interpreter.load_route_file(Config.ROUTE_PATH)
    # Load task header, with some config
    route_header = interpreter.preprocess_route_header(route)
    # Calculate current robot vector, based on start coordinates and direction.
    robot.calculate_robot_start_vector(route_header[0], route_header[1])
    # Init motors controller service
    motors_controller = MotorsController()
    # Init planner service
    planner = Planner(3.0, 2.0, 70)
    # Init && start task manager match mode
    task_manager = TaskManager()
    # Init logger service
    logger = Logger() 
    # Start match execution
    launch()
