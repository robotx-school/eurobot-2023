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
import sys
sys.path.append("../../PathFinding")
from planner import Planner


class Logger:
    def __init__(self):
        self.dir = Config.LOGS_DIRECTORY

    def get_time(self):
        unix_time = int(time.time())
        readable_time = datetime.datetime.utcfromtimestamp(unix_time).strftime('%H:%M:%S')
        return {"unix_time": unix_time, "display": readable_time}

    def gen_string(self, time, service_name, type_, message):
        # [time][service_name][type] message
        return f"[{time}][{service_name}][{type_}] {message}\n"

    def new_match(self):
        time_ = self.get_time()
        self.log_name = f"{time_['unix_time']}_{Config.ROUTE_PATH}.log"
        with open(os.path.join(self.dir, self.log_name), "w") as fd:
            fd.write(self.gen_string(time_["display"], "LOGGER", "INFO", "Match started!"))

    def write(self, service_name, type_, message):
        time_ = self.get_time()
        with open(os.path.join(self.dir, self.log_name), "a") as fd:
            fd.write(self.gen_string(time_["display"], service_name, type_, message))

class TaskManager:
    '''
    You can think, that this is core service of this robot. But... no. I can't select CORE service. This code is full of democracy
    '''
    def __init__(self):
        pass

    def match(self, tasks):
        # Synchronous tasks execution
        for task in tasks[1:]:
            # Block process here
            interpreter.process_instruction(task)
        print("[DEBUG][TMGR] Tasks pull empty.")
        print(motors_controller.logged_points)
            

class MotorsController:
    '''
    Drive from point A (current) to point B
    Bypass obstacles or stopping in front of them (data from lidar).
    '''
    def __init__(self):
        self.logged_points = []

    def drive(self, point, bypass_obstacles=True):
        #print(point)
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
                #print(map_server.robots_coords)
                #print(other_robots, this_robot_coordinates, point)
                obstacle_on_the_way = planner.check_obstacle(other_robots, this_robot_coordinates, point)
                if obstacle_on_the_way[0]:
                    #FIXIT
                    # DELETE last logged point from log
                    print(colored("OBSTACLE", "red"))
                    spilib.spi_send([1, 0, 0]) # emergency stop
                    time.sleep(0.5) # wait for motors to step
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
                    #planner.visualize(bp[0])
                    #print("--- BYPASS ---")
                    robot.curr_x = this_robot_coordinates[0]
                    robot.curr_y = this_robot_coordinates[1]
                    robot.generate_vector()
                    for step in bp[1]:
                        self.drive(step, bypass_obstacles=False) # FIXIT

            recieved = spilib.spi_send([])
            if (recieved[0] == 0 and recieved[1] == 0):
                break
            # Process lidar data example hook
            if (recieved[8]):
                pass
            time.sleep(0.05)
        #print(self.logged_points)
        #print(robot.curr_x, robot.curr_y)

class Interpreter:
    def __init__(self):
        self.local_variables = {} # pull of local variables
        self.if_cond = 0  # 0 - no conditions; 1 - true condition; 2 - false condition

    def process_instruction(self, task):
        if task["action"] == 1:
            motors_controller.drive(task["point"])

    def preprocess_route_header(self, route):
        header = route[0]
        if header["action"] == -1:  # Header action
            return tuple(header["start_point"]), header["direction"]

    def load_route_file(self, path):
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