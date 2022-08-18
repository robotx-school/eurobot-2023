from robot import Robot
import json
from flask import Flask, render_template
import threading
import time

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

ROUTE_PATH = "route.json"
ROBOT_SIZE = 50
START_POINT = (0, 0)
MM_COEF = 9.52381 # Dev robot
ROTATION_COEFF = 12.1 # Dev robot
ONE_PX = 1.95822454308094 # Const
STRATEGY_ID = 0
MASTER_PASSWORD = "test_pass"
ROBOT_ID = 0 # Edit manualy
USE_STRATEGY_ID = True

app = Flask(__name__, template_folder="webui/templates", static_url_path='', static_folder='webui/static')
app.config["TEMPLATES_AUTO_RELOAD"] = True
#app.config['STATIC_FOLDER'] = "webui/static"

@app.route("/")
def index():
    return render_template("index.html", route_path=ROUTE_PATH, start_point=START_POINT, strategy_id=STRATEGY_ID)

if __name__ == "__main__":
    if USE_STRATEGY_ID:
        ROUTE_PATH = load_route_by_strategy_id(STRATEGY_ID, ROBOT_ID)
    route = load_route_file(ROUTE_PATH)
    START_POINT = preprocess_route_header(route)
    print(START_POINT)
    robot = Robot(ROBOT_SIZE, START_POINT, "E", MM_COEF, ROTATION_COEFF, ONE_PX, 1) # Start robot in real mode
    #app.run(host="0.0.0.0", port="8080")
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port="8080")).start()
    print("[DEBUG] WebUI started")
    # Polling loop(get sensors data from arduino)
    print("[DEBUG] Statring polling loop")
    while True:
        #sensors_data = robot.get_sensors_data() Works only on real RPi 
        sensor_data = [0] * 20
        sensor_data[2] = 1 # Starter sensor
        time.sleep(4) # Simulate that we pulled the starter
        if sensor_data[2] == 1:
            robot.interpret_route(route)
            exit(0) # Finish program; stop robot high-level
        else:
            continue
