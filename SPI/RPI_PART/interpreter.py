import spilib
import time


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
            steps_cnt = step["distance"] 
        elif step["action"] in ["right", "left"]:
            steps_cnt = step["angle"] * self.rotate_coef
        try: # FIXIT USED HERE ONLY WHILE LOCAL PC DEVELOPMENT
            spilib.move_robot(action, self.interpreter_controller_flag, speed=speed, steps=steps_cnt, sensor_id=sensor_id, sensor_val=sensor_val)
        except:
            time.sleep(2) # Fake execution time
        
class Interpreter:
    '''
    Main interpreter class
    This class execute code(JSON file) line by line
    '''
    def __init__(self, motors_driver, logger):
        self.finish_program = False # Interrupt program execution flag
        self.motors_driver = motors_driver
        self.logger = logger
        self.execution_vars = {} # Execution session data container
        self.curr_if_stack = [0, -1] # (if_id, execution_status)
        # Execution status variants:
        # -1: if not assign(no loop, execution works)
        # 0: false if(no execution works until if finished with endif)
        # 1: true execution enabled if var is true(1, True, true)

    def interpret(self, data):
        self.logger.start_execution()
        self.execution_vars = {} # Clear session data
        for step in data:
            if not self.finish_program:
                if self.curr_if_stack[1] in [-1, 1] or step['action'] == 'endif':
                    if step["action"] in ["forward", "left", "right"]:
                        self.logger.write_entry(f"Motors {step['action']}")
                        self.motors_driver.drive(step)
                        #print(step) LOGGER
                    elif step["action"] == "servo":
                        self.logger.write_entry(f"Servo action: {step['num']} steps")
                        #spilib.move_servo(step["num"], step["start_angle"], step["finish_angle"], step["delay"]) # Servo works without driver wrapper like motors
                    elif step["action"] == "python": # Execute custom python code from custom_python
                        self.logger.write_entry("Python code")
                        eval(step["source"])
                    elif step["action"].startswith("threaded_"): # Multithreading on interpretation level (NOT fully implemented yet)
                        pass
                    elif step['action'] == "delay": # Delay on interpretation level
                        self.logger.write_entry(f"Delay {step['delay']}")
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
                    elif step['action'] == "endif": # Finish checking
                        self.curr_if_stack[1] = -1
                        self.curr_if_stack[0] = 0
            else: # Interrupt execution (used for emergency stop)
                break
        self.finish_program = False # Toggle back interruption flag
        # Clear if stack
        self.curr_if_stack[0] = 0
        self.curr_if_stack[1] = -1
        # Finish logger 
        self.logger.finish_execution()
        print(self.execution_vars)

if __name__ == "__main__":
    print("Executing")
