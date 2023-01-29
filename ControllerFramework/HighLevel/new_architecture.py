import threading
import spilib
from flask import Flask, jsonify, render_template, request
from robot import Robot
from config import *
import json
import time
from sync import *
#from services.webapi_service import WebApi
import logging
from services.socket_service import SocketService
import socket
from termcolor import colored

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)


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

        @self.app.route('/api/upd', methods=['POST'])
        def __upd_route_json():
            global route
            route = json.loads(request.data.decode('utf-8'))
            return self.get_route_json()

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

    def run(self):
        print(colored("[INFO][WEB] Started", "green"))
        self.app.run(host=self.host, port=self.port)

    def index(self):
        return render_template("index.html", route_path=ROUTE_PATH, start_point=robot.start_point, strategy_id=STRATEGY_ID,
                               execution_status=GLOBAL_STATUS["route_executing"], use_strategy_id=int(USE_STRATEGY_ID), side=robot.side,
                               robot_id=ROBOT_ID, local_ip=socket.gethostbyname(socket.gethostname()), polling_interval=JS_POLLING_INTERVAL,
                               web_port=FLASK_PORT)

    def tmgr(self):
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
        GLOBAL_STATUS["execution_request"] = 2  # Emergency stop request
        return jsonify({"status": True})

    def change_config(self):
        if request.form.get("masterPassword") == MASTER_PASSWORD:
            return jsonify({"status": True})
        return jsonify({"status": False, "text": "Invalid master password"})

    def get_route_json(self):
        global route
        return {"status": True, "data": route}


class Interpreter:
    def __init__(self):
        self.local_variables = {}
        self.if_cond = 0  # 0 - no conditions; 1 - true condition; 2 - false condition

    def interpet_step(self, instruction):
        global robot
        if self.if_cond in [0, 1] or instruction["action"] in [7, "endif"]:
            if instruction["action"] == 0:
                if instruction["subaction"] == 0:
                    print("[DEBUG] Interpreter data")
                    print("Variables:", self.local_variables)
                elif instruction["subaction"] in [1, "print"]:
                    print(instruction["text"])
            elif instruction["action"] == 1:
                try:
                    robot.go(instruction["point"]) 
                except FileNotFoundError:
                    print(colored("[FATAL][INTERPRETER] Can't communicate with SPI", "red"))
                time.sleep(3) # Fake step execution time
            elif instruction["action"] == [2, "servo"]:
                # Servo
                pass
            elif instruction["action"] in [3, "delay"]:
                time.sleep(instruction["seconds"])
            elif instruction["action"] in [4, "backward"]:
                point = instruction["back_point"]

                angle, dist = robot.compute_point(
                    point, [], visualize=False, change_vector=False)
                angle = 0
                dist *= robot.mm_coef
                dist += int(instruction["extra_force"] * robot.mm_coef)
                spilib.move_robot("forward", False, distance=-int(dist))

            elif instruction["action"] in [5, "set_var"]:
                self.local_variables[instruction["var_name"]
                                     ] = instruction["var_value"]
                GLOBAL_STATUS["step_executing"] = False
            elif instruction["action"] in [6, "if"]:
                if type(instruction["current_value"]) == int:
                    val_to_check = instruction["current_value"]
                else:
                    if instruction["current_value"] in self.local_variables:
                        val_to_check = self.local_variables[instruction["current_value"]]
                    else:
                        val_to_check = 1  # If no such variable we will compare with 1
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

    # Write your custom interpreter functions after this comment

    def check_aruco(self, var_to_save, aruco_number):
        pass


class TaskManager:
    def __init__(self):
        self.services = {"webapi": None, "socketclient": None}
        self.strict_mode = True
        self.spi_data = [-1] * 20

    def loop(self):
        global route, robot
        while True:
            self.spi_data = spilib.spi_send()

            # print(spi_data)
            if GLOBAL_STATUS["execution_request"] == 2:
                print("[EMERGENCY] Stop robot")
                GLOBAL_STATUS["route_executing"] = False
                GLOBAL_STATUS["step_executing"] = False
                GLOBAL_STATUS["goal_point"] = [-1, -1]
                GLOBAL_STATUS["execution_request"] = 0
                spilib.stop_robot()
            if GLOBAL_STATUS["bypass"]:  # Inject steps into current route
                GLOBAL_STATUS["current_step"] -= 1
                step = GLOBAL_STATUS["current_step"]
                # Linear steps injection
                print(step)
                for el in GLOBAL_STATUS["bypass"]:
                    route.insert(step, el)
                    step += 1
                GLOBAL_STATUS["bypass"] = []
                # Interrupt current step
                GLOBAL_STATUS["step_executing"] = False
                # Temp fix; for test ONLY; GET coords FROM CTD; Direction from local dat; or ctd later
                robot.curr_x = 0
                robot.curr_y = 356
                #robot.robot_direction = "E"
                robot.generate_vector()
                spilib.spi_send([1, 0, 0])  # Stop robot # FIXIT; Move to spilib library; use it as abstarcture of spi dirver
                print(colored("[DEBUG][TMGR] Modified route:", "yellow"), route)
                time.sleep(0.5) # wait until robot stops; const #FIXIT; move to config
                print(colored("[DEBUG][TMGR] Robot stopped! Starting injected steps", "green"))

            if GLOBAL_STATUS["route_executing"] == False: # Physical starter; disabled now
                if False:
                    GLOBAL_STATUS["route_executing"] = True
                    GLOBAL_STATUS["current_step"] = 1
                    GLOBAL_STATUS["goal_point"] = (-1, -1)
                    print("Starting...")
            else: # Route is executing now
                if not GLOBAL_STATUS["step_executing"]: # No steps executing now
                    if len(route) - 1 >= GLOBAL_STATUS["current_step"]: # We have steps to execute
                        GLOBAL_STATUS["step_executing"] = True # New step is executing now flag toggle to TRUE
                        if route[GLOBAL_STATUS["current_step"]]["action"] == 1:
                            GLOBAL_STATUS["goal_point"] = route[GLOBAL_STATUS["current_step"]]["point"] # set point we follow
                            print(colored("[DEBUG][TMGR] Planning to point:", "magenta"),
                                  GLOBAL_STATUS["goal_point"])
                        interpreter.interpet_step(
                            route[GLOBAL_STATUS["current_step"]])
                        GLOBAL_STATUS["current_step"] += 1 # Next step
                    else:
                        GLOBAL_STATUS["route_executing"] = False
                        GLOBAL_STATUS["goal_point"] = [-1, -1]
                        print(colored("[INFO][TMGR] Route queue finished!", "green"))
                else:
                    if self.spi_data[0] == 0 and self.spi_data[1] == 0:
                        GLOBAL_STATUS["step_executing"] = False
            # time.sleep(2)

    def start_service(self, *args):
        if args[0] in self.services:
            if self.strict_mode and self.services[args[0]]:
                # Service already running (bypass using strict_mode = False)
                return -90
            else:
                self.services[args[0]] = threading.Thread(
                    target=lambda: args[1].run(*args[2:]))
                self.services[args[0]].start()
        else:
            return -100  # No such service type


if __name__ == "__main__":
    try:
        robot = Robot(ROBOT_SIZE, START_POINT, ROBOT_DIRECTION, SIDE,
                      MM_COEF, ROTATION_COEFF, ONE_PX, 1)
        interpreter = Interpreter()
        route = interpreter.load_route_file(ROUTE_PATH)
        route_header = interpreter.preprocess_route_header(route)
        robot.calculate_robot_start_vector(route_header[0], route_header[1])
        tmgr = TaskManager()
        webapi = WebApi(__name__, FLASK_HOST, FLASK_PORT)
        try:
            socket_service = SocketService(SOCKET_SERVER_HOST, SOCKET_SERVER_PORT, ROBOT_ID, route)
            tmgr.start_service("socketclient", socket_service, ONE_PX)
        except:
            print(colored("[ERROR] Can't connect to CTD. Offline mode active!", "yellow"))

        tmgr.start_service("webapi", webapi)

        tmgr.loop()
    except KeyboardInterrupt:
        exit(0)
