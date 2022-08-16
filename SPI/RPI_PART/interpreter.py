import spilib
import time
import json


class MotorsAPI:
    '''
    This class works with motors on high level
    It is a wrapper around low level spilib driver
    '''
    def __init__(self, rotate_coef=40):
        self.rotate_coef = rotate_coef
        self.interpreter_controller_flag = False

    def drive(self, step):
        action = step["action"]
        speed = step["speed"]
        if "sensor_id" in step:
            sensor_id = step["sensor_id"]
            sensor_val = step["sensor_val"]
        else:
            sensor_id = -1
            sensor_val = -1
        if step["action"] == "forward":
            distance = step["distance"]
        elif step["action"] in ["right", "left"]:
            distance = step["angle"] * self.rotate_coef
        try:
            spilib.move_robot(action, self.interpreter_controller_flag, speed=speed, distance=distance, sensor_id=sensor_id, sensor_val=sensor_val)
        except FileNotFoundError:
            pass
        
        
class Interpreter:
    '''
    Main interpreter class
    This class execute code(JSON file) line by line
    '''
    def __init__(self, motors_driver):
        self.finish_program = False # Interrupt program execution flag
        self.motors_driver = motors_driver
        self.execution_vars = {} # Execution session data container
        self.curr_if_stack = [0, -1] # (if_id, execution_status)
        
        # Execution status variants:
        # -1: if not assign(no loop, execution works)
        # 0: false if(no execution works until if finished with endif)
        # 1: true execution enabled if var is true(1, True, true)
        # 2: execute as else part of if
    def interpret(self, data):
        self.execution_vars = {} # Clear session data
        for step in data:
            if not self.finish_program:
                if self.curr_if_stack[1] in [-1, 1, 2] or step['action'] in ['endif', 'else']:
                    if step["action"] in ["forward", "left", "right"]:
                        self.motors_driver.drive(step)
                    elif step['action'] == "delay": # Delay on interpretation level
                        time.sleep(step["delay"])
                    elif step['action'] == "init_var":
                        self.execution_vars[step['var_name']] = step['var_value']
                    elif step['action'] == "set_var":
                        if step['var_name'] in self.execution_vars:
                            self.execution_vars[step['var_name']] = step['var_value']
                    elif step['action'] == 'if':
                        # Assign if
                        var_to_check = step['check_var']
                        if var_to_check in self.execution_vars:
                            if self.execution_vars[var_to_check] in ["1", "True", "true", 1]:
                                self.curr_if_stack[1] = 1
                                self.curr_if_stack[0] = step['if_id']
                            else:
                                self.curr_if_stack[1] = 0
                                self.curr_if_stack[0] = step['if_id']
                        else:
                            self.curr_if_stack[1] = 0 # Deny if execution
                    elif step['action'] == "else":
                        if self.curr_if_stack[1] == 0:
                            self.curr_if_stack[1] = 2
                        elif self.curr_if_stack[1] == 1:
                            self.curr_if_stack[1] = 0
                    elif step['action'] == "exit":
                        self.finish_program = True
                        self.motors_driver.interpreter_controller_flag = True
                        break
                    elif step['action'] == "endif": # Finish checking
                        self.curr_if_stack[1] = -1
                        self.curr_if_stack[0] = 0
            else: # Interrupt execution (used for emergency stop)
                break
        self.finish_program = False # Toggle back interruption flag
        # Clear if stack
        self.curr_if_stack[0] = 0
        self.curr_if_stack[1] = -1

if __name__ == "__main__":
    print("Running interpreter CLI...")
    motors_driver = MotorsAPI()
    interpreter = Interpreter(motors_driver)
    print("Motors driver and Interpreter loaded")
    routing_file_path = "ways/route.json" #input("Path to JSON>")
    with open(routing_file_path) as file:
        route = json.load(file)
    interpreter.interpret(route)
