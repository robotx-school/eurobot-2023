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
    


class Interpreter:
    def __init__(self):
        self.local_variables = {}
    def interpet_step(self, instruction):
        if instruction["action"] == 1:
            print("Going to point:", instruction["point"])
            time.sleep(0.1)
            

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
        self.services = {"webapi": None, "socketclient": None}
        self.strict_mode = True
        self.spi_data = [-1] * 20
    def loop(self):
        while True:
            self.spi_data = spilib.fake_req_data()
            #print(spi_data)
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
                        GLOBAL_STATUS["goal_point"] = route[GLOBAL_STATUS["current_step"]]["point"]
                        interpreter.interpet_step(route[GLOBAL_STATUS["current_step"]])
                        GLOBAL_STATUS["current_step"] += 1
                    else:
                        GLOBAL_STATUS["route_executing"] = False
                        GLOBAL_STATUS["goal_point"] = [-1, -1]
                        print("Route queue finished")
                else:
                    if self.spi_data[0] == 0 and self.spi_data[1] == 0:
                        print("Next step")
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


if __name__ == "__main__":
    try:
        robot = Robot(ROBOT_SIZE, START_POINT, ROBOT_DIRECTION, SIDE,
                    MM_COEF, ROTATION_COEFF, ONE_PX, 1)
        interpreter = Interpreter()
        route = interpreter.load_route_file(ROUTE_PATH)
        webapi = WebApi(__name__, FLASK_HOST, FLASK_PORT)
        tmgr = TaskManager()
        tmgr.start_service("webapi", webapi)
        tmgr.loop()
    except KeyboardInterrupt:
        exit(0)
