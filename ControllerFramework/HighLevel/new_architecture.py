import threading
import spilib
from flask import Flask, jsonify
from robot import Robot
from config import *
import logging
import json
import time

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

GLOBAL_STATUS = {
    "step_executing": False,
    "route_executing": False,
    "execution_request": 0,
    "current_step": 1,
    "goal_point": (-1, -1)
}


class WebApi():
    def __init__(self, name, host, port):
        self.app = Flask(name, template_folder="webui/templates",
                         static_url_path='', static_folder='webui/static')
        self.host = host
        self.port = port
        self.app.config["TEMPLATES_AUTO_RELOAD"] = True


        ## UI routes
        @self.app.route('/')
        def __index():
            return self.index()

        ## API routes
        # Debug(dev) routes
        @self.app.route('/api/dev/tmgr')
        def __tmgr():
            return self.tmgr()


        # Testing routes
        @self.app.route('/api/start_route')
        def __start_route():
            return self.start_route()
        
        @self.app.route('/api/emergency_stop')
        def __emergency_stop():
            return self.emergency_stop()
        # Not working FIXIT
        @self.app.route('/api/shutdown')
        def __shutdown():
            exit(1)
            return "1"
    
    def run(self):
        self.app.run(host=self.host, port=self.port)
    def index(self):
        return "NOT PORTED YET"

    def tmgr(self):
        global GLOBAL_STATUS
        active_services = tmgr.services.copy()
        for service in active_services:
            if active_services[service] != None:
                active_services[service] = "Running"
            else:
                active_services[service] = "Not running"

        return jsonify({"global_data": GLOBAL_STATUS, "tmgr_services": active_services, "spi_data": tmgr.spi_data})
    def start_route(self):
        GLOBAL_STATUS["route_executing"] = True
        GLOBAL_STATUS["current_step"] = 1
        GLOBAL_STATUS["goal_point"] = (-1, -1)
        return jsonify({"status": True})
    def emergency_stop(self):
        GLOBAL_STATUS["execution_request"] = 2 # Emergency stop request
        return jsonify({"status": True})



class Interpreter:
    def __init__(self):
        self.local_variables = {}
        self.if_cond = 0 # 0 - no conditions; 1 - true condition; 2 - false condition 
    def interpet_step(self, instruction):
        global robot
        if self.if_cond in [0, 1] or instruction["action"] in [7, "endif"]:
            if instruction["action"] == 0:
                print("[DEBUG] Interpreter data")
                print("Variables:", self.local_variables)
            elif instruction["action"] == 1:
                #print("Going to point:", instruction["point"])
                try:
                    robot.go(instruction["point"])
                except FileNotFoundError:
                    print("[FATAL] Can't communicate with SPI")
                time.sleep(0.1)
            elif instruction["action"] == [2, "servo"]:
                # Servo
                pass
            elif instruction["action"] in [3, "delay"]:
                time.sleep(instruction["seconds"])
            elif instruction["action"] in [4, "backward"]:
                pass
            elif instruction["action"] in [5, "set_var"]:
                self.local_variables[instruction["var_name"]] = instruction["var_value"]
                GLOBAL_STATUS["step_executing"] = False
            elif instruction["action"] in [6, "if"]:
                if type(instruction["current_value"]) == int:
                    val_to_check = instruction["current_value"]
                else:
                    if instruction["current_value"] in self.local_variables:
                        val_to_check = self.local_variables[instruction["current_value"]]
                    else:
                        val_to_check = 1 # If no such variable we will compare with 1
                val_to_compare_with = instruction["compare_with"]
                if val_to_check == val_to_compare_with:
                    self.if_cond = 1
                else:
                    self.if_cond = 2
            elif instruction["action"] in [7, "endif"]:
                self.if_cond = 0
                

    def preprocess_route_header(self, route):
        header = route[0]
        if header["action"] == -1:  # Header action
            return tuple(header["start_point"]), header["direction"]

    def load_route_file(self, path):
        with open(path) as f:
            route = json.load(f)
        return route

    def check_aruco(self, var_to_save, aruco_number):
        pass


class TaskManager:
    def __init__(self):
        self.services = {"webapi": None, "socketclient": None}
        self.strict_mode = True
        self.spi_data = [-1] * 20
    def loop(self):
        while True:
            self.spi_data = spilib.fake_req_data()
            #print(spi_data)
            if GLOBAL_STATUS["execution_request"] == 2:
                print("[EMERGENCY] Stop robot")
                GLOBAL_STATUS["route_executing"] = False
                GLOBAL_STATUS["step_executing"] = False
                GLOBAL_STATUS["goal_point"] = [-1, -1]
                GLOBAL_STATUS["execution_request"] = 0
                #spilib.stop_robot()
            if GLOBAL_STATUS["route_executing"] == False:
                if self.spi_data[4]:
                    GLOBAL_STATUS["route_executing"] = True
                    GLOBAL_STATUS["current_step"] = 1
                    GLOBAL_STATUS["goal_point"] = (-1, -1)
                    print("Starting...")
            else:
                if not GLOBAL_STATUS["step_executing"]:
                    if len(route) - 1 >= GLOBAL_STATUS["current_step"]:
                        GLOBAL_STATUS["step_executing"] = True
                        if route[GLOBAL_STATUS["current_step"]]["action"] == 1:
                            GLOBAL_STATUS["goal_point"] = route[GLOBAL_STATUS["current_step"]]["point"]
                        interpreter.interpet_step(route[GLOBAL_STATUS["current_step"]])
                        GLOBAL_STATUS["current_step"] += 1
                    else:
                        GLOBAL_STATUS["route_executing"] = False
                        GLOBAL_STATUS["goal_point"] = [-1, -1]
                        print("Route queue finished")
                else:
                    if self.spi_data[0] == 0 and self.spi_data[1] == 0:
                        GLOBAL_STATUS["step_executing"] = False
            #time.sleep(2)
    def start_service(self, service_type, service_class):
        if service_type in self.services:
            if self.strict_mode and self.services[service_type]:
                return -90 # Service already running (bypass using strict_mode = False)
            else:
                self.services[service_type] = threading.Thread(target=service_class.run)
                self.services[service_type].start()
        else:
            return -100 # No such service type
    
    def inject_route_steps(self, inject_start_pos, steps):
        global route



if __name__ == "__main__":
    try:
        robot = Robot(ROBOT_SIZE, START_POINT, ROBOT_DIRECTION, SIDE,
                    MM_COEF, ROTATION_COEFF, ONE_PX, 1)
        interpreter = Interpreter()
        route = interpreter.load_route_file(ROUTE_PATH)
        route_header = interpreter.preprocess_route_header(route)
        robot.calculate_robot_start_vector(route_header[0], route_header[1])
        
        webapi = WebApi(__name__, FLASK_HOST, FLASK_PORT)
        tmgr = TaskManager()
        tmgr.start_service("webapi", webapi)
        tmgr.loop()
    except KeyboardInterrupt:
        exit(0)
