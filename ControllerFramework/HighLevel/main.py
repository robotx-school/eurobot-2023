from robot import Robot
import json
from flask import Flask, render_template, request, jsonify
import threading
import time
from config import *
import logging
import socket

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

def load_route_by_strategy_id(strategy_id, robot_id):
    return f"./strategies/{strategy_id}/robot_{robot_id}.json"

def preprocess_route_header(route):
    header = route[0]
    if header["action"] == -1: # Header action
        return tuple(header["start_point"])

def load_route_file(path):
    with open(ROUTE_PATH) as f:
        route = json.load(f)
    return route


app = Flask(__name__, template_folder="webui/templates", static_url_path='', static_folder='webui/static')
app.config["TEMPLATES_AUTO_RELOAD"] = True

@app.route("/")
def index():
    return render_template("index.html", route_path=ROUTE_PATH, start_point=START_POINT, strategy_id=STRATEGY_ID, 
                                        execution_status=execution_status, use_strategy_id=int(USE_STRATEGY_ID), side=SIDE,
                                        robot_id=ROBOT_ID, local_ip=socket.gethostbyname(socket.gethostname()), polling_interval=JS_POLLING_INTERVAL,
                                        web_port=FLASK_PORT)
@app.route("/api/change_config", methods=["POST"])
def change_config():
    global START_POINT, ROUTE_PATH, USE_STRATEGY_ID, STRATEGY_ID, route, robot, SIDE
    if request.form.get("masterPassword") == MASTER_PASSWORD:
        raw_start_point = request.form.get("start_point").split(",")
        START_POINT = (int(raw_start_point[0]), int(raw_start_point[1]))
        ROUTE_PATH = request.form.get("route_path")
        USE_STRATEGY_ID = int(request.form['routeLoadingMethod'])
        STRATEGY_ID = int(request.form.get("strategy_id"))
        if USE_STRATEGY_ID:
            ROUTE_PATH = load_route_by_strategy_id(STRATEGY_ID, ROBOT_ID) 
        route = load_route_file(ROUTE_PATH)
        START_POINT = preprocess_route_header(route)
        robot.calculate_robot_start_vector(START_POINT, "E")
        SIDE = int(request.form['side_selector'])
        robot.side = SIDE
        return jsonify({"status": True})
    else:
        return jsonify({"status": False, "text": "Invalid master password"})

@app.route("/api/poll_robot_status")
def get_robot_status():
    global execution_status, monitoring_dict
    resp_dict = {"status": True, "execution_status": execution_status}
    resp_dict.update(monitoring_dict)
    if monitoring_dict["start_time"] != 0:
        resp_dict["route_time"] = int(time.time() - monitoring_dict["start_time"])
    if monitoring_dict["steps_left"] == 0:
        resp_dict["execution_status"] = 0
        execution_status = 0
    if not execution_status:
        monitoring_dict["start_time"] = 0
    return jsonify(resp_dict)

@app.route("/api/start_route")
def start_route():
    global monitoring_dict, execution_status
    monitoring_dict = {"steps_done": 0, "steps_left": 0, "distance_drived": 0, "motors_time": 0, "start_time": 0} # Clear dict
    execution_status = 1
    threading.Thread(target=robot.interpret_route, args=(route, monitoring_dict, )).start()
    return jsonify({"status": True})

@app.route("/api/emergency_stop")
def emergency_stop():
    global execution_status
    execution_status = 2 # Emergency status code

if __name__ == "__main__":
    execution_status = 0
    monitoring_dict = {"steps_done": 0, "steps_left": 0, "distance_drived": 0, "motors_time": 0, "start_time": 0}
    if USE_STRATEGY_ID:
        ROUTE_PATH = load_route_by_strategy_id(STRATEGY_ID, ROBOT_ID) 
    route = load_route_file(ROUTE_PATH)
    START_POINT = preprocess_route_header(route)
    robot = Robot(ROBOT_SIZE, START_POINT, "E", SIDE, MM_COEF, ROTATION_COEFF, ONE_PX, 1) # Start robot in real mode
    threading.Thread(target=lambda: app.run(host=FLASK_HOST, port=FLASK_PORT)).start()
    print("[DEBUG] WebUI started")
    # Polling loop(get sensors data from arduino)
    print("[DEBUG] Starting polling loop")
    while True:
        #sensors_data = robot.get_sensors_data() Works only on real RPi 
        sensors_data = [0] * 20
        #sensors_data[2] = 1 # Starter sensor
        time.sleep(4) # Simulate that we pulled the starter
        if sensors_data[2] == 1:
            execution_status = 1
            robot.interpret_route(route, monitoring_dict)
            execution_status = 0
        else:
            continue
