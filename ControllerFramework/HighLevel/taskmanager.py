from robot import Robot
from config import *
import json
import time
from flask import Flask
from multiprocessing import Process, Manager # Porting from threading
import spilib

# Global status variables
# 0 - no execution
# 1 - execution starting request
# 2 - execution is going
# 3 - execution stop request
class WebUI:
    def __init__(self, name, host, port):
        self.app = Flask(name)
        self.host = host
        self.port = port

        @self.app.route('/')
        def __index():
            return self.index()

        @self.app.route('/start')
        def __start():
            return self.start()

        @self.app.route('/stop')
        def __stop():
            return self.stop()

    def index(self):
        return f'Execution status: {self.share_data["execution_status"]}'

    def start(self):
        self.share_data["execution_status"] = 1
        return str(self.share_data)

    def stop(self):
        self.share_data["execution_status"] = 3
        return str(self.share_data)

    def update_share_data(self, share_data):
        self.share_data = share_data

    def run(self):
        self.app.run(host=self.host, port=self.port)

class Interpreter: # Move interpeter from robot classs to another micro-service
    def __init__(self):
        pass

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
                status, going_time, dist_drived = robot.go(final_point)
                '''monitoring_dict["steps_done"] += 1
                monitoring_dict["steps_left"] = steps_cnt - \
                    monitoring_dict["steps_done"]
                monitoring_dict["distance_drived"] += dist_drived
                monitoring_dict["motors_time"] += going_time'''
            except FileNotFoundError:  # Handle spi error
                print("[DEBUG] Warning! Invalaid SPI connection")
                time.sleep(5)
        elif instruction["action"] == 2:
            # Reserved for servo
            pass
        elif instruction["action"] == 3:
            # Delay on high-level
            time.sleep(instruction["seconds"])
        elif instruction["action"] == 4:
            # Backward driving
            point = instruction["back_point"]
            angle, dist = robot.compute_point(
                point, [], visualize=False, change_vector=False)
            angle = 0
            dist += int(instruction["extra_force"] * robot.mm_coef)
            print(-dist)
            spilib.move_robot("forward", False, distance=-dist)
        self.share_data["step_executing"] = False

    def preprocess_route_header(self, route):
        header = route[0]
        if header["action"] == -1: # Header action
            return tuple(header["start_point"])


class TaskManager:
    def __init__(self):
        '''
        Works every time without freezing. If it hangs, robot will die)
        '''
        self.time_start = 0
        self.emergency_time = 90
        self.step_id = 0
        self.processes = {"web": None, "interpreter": None}
        self.processes_manager = Manager()
        self.share_dict = self.processes_manager.dict()
        # Default start values
        self.share_dict["execution_status"] = 0
        self.share_dict["step_executing"] = False

    def mainloop(self):
        global route
        while True:
            if self.share_dict["execution_status"] == 1: # start
                print("[DEBUG] Start execution")
                self.step_id = 0
                self.share_dict["execution_status"] = 2
                self.time_start = time.time()
            elif self.share_dict["execution_status"] == 2: # execution is going now
                time_gone = time.time() - self.time_start
                if time_gone >= self.emergency_time:
                    print("[DEBUG] Return back")
                    self.share_dict["execution_status"] = 0
                    self.kill_process("interpreter")
                else:
                    if self.step_id < len(route):
                        if not self.share_dict["step_executing"]:
                            self.start_process(type="interpreter", process_class=interpreter, step=route[self.step_id])
                            self.step_id += 1
                            time.sleep(0.1)
                    else:
                        print("[DEBUG] Execution queue finished")
                        self.share_dict["execution_status"] = 0 # Execution finished
            elif self.share_dict["execution_status"] == 3: # Kill interpreter process
                self.share_dict["execution_status"] = 0
                self.kill_process("interpreter")
    
    def start_process(self, **kwargs):
        if kwargs["type"] == "web":
            kwargs["process_class"].update_share_data(self.share_dict)
            self.processes["web"] = Process(target=lambda: kwargs["process_class"].run())
            self.processes["web"].start()
        elif kwargs["type"] == "interpreter":
            kwargs["process_class"].update_share_data(self.share_dict)
            self.processes["interpreter"] = Process(target=lambda: kwargs["process_class"].interpet_step(kwargs["step"]))
            self.processes["interpreter"].start()
    def kill_process(self, process_name):
        if self.processes[process_name] and process_name in self.processes:
            self.processes[process_name].terminate()
            return 1 # Process killed
        else:
            return 0 # No such process


def load_route_file(path):
    with open(path) as f:
        route = json.load(f)
    return route

if __name__ == "__main__":
    interpreter = Interpreter()
    monitoring_dict = {"steps_done": 0, "steps_left": 0, "distance_drived": 0, "motors_time": 0, "start_time": 0}
    route = load_route_file("hl.json")
    START_POINT = interpreter.preprocess_route_header(route)
    robot = Robot(ROBOT_SIZE, START_POINT, "E", SIDE, MM_COEF, ROTATION_COEFF, ONE_PX, 1) # Start robot in real mode
    web_ui = WebUI(__name__, "0.0.0.0", "8080")
    tmgr = TaskManager()
    tmgr.start_process(type="web", process_class=web_ui)
    tmgr.mainloop()