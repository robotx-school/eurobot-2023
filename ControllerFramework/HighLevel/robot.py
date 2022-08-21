from geometry import *
import cv2
import spilib
import time


class Robot:
    '''
    High level(RPi level) robot declaration
    Available execution as virtual machine(simulation) or as high level commander under Arduino via SPI

    '''

    def __init__(self, robot_size, start_point, robot_direction, side, mm_coef, rotation_coeff, one_px, mode=0, field_side_real=(3000, 2000), field_size_px=(1532, 1022)):
        self.robot_size = robot_size
        self.side = side
        self.start_point = start_point
        self.route_analytics = {"dist": 0, "rotations": 0, "motors_timing": 0}
        self.mm_coef = mm_coef  # Dev robot = 9.52381
        self.rotation_coeff = rotation_coeff  # Dev robot = 12.1
        self.one_px = one_px
        self.curr_path_points = []
        self.curr_x, self.curr_y = start_point  # Robot start
        # Generate robot vector
        self.robot_vect_x, self.robot_vect_y = self.curr_x + \
            self.robot_size, self.curr_y  # Right(East)
        self.mode = mode  # (0 - virtual mode; 1 - real mode)
        self.field_side_real = field_side_real
        self.field_size_px = field_size_px

    def calculate_robot_start_vector(self, robot_coords, direction):
        self.start_point = robot_coords
        self.curr_x, self.curr_y = robot_coords
        self.robot_vect_x, self.robot_vect_y = self.curr_x + \
            self.robot_size, self.curr_y  # For East

    def compute_point(self, point, field, append_point=True, visualize=True, change_vector=True):
        '''
        Compute angle to rotate and distance to ride for next point and also recalculate finish point and vector angle

        Args:
            point(tuple): point to follow (x, y) in px
            field(numpy array): image of field in 2d fro top view
            append_point(bool): append point to local array storing current session points
            visualize(bool): draw point and final vector on image
            change_vector(bool): change final vector after point computation(False if we driving backward)
        Returns:
            Modify field img
            Angle to rotate (float)
            Distancse in millimeters (int)
        '''
        if append_point:
            self.curr_path_points.append(point)
        robot_vect, robot_vect_1 = vect_from_4points(
            self.curr_x, self.curr_y, self.robot_vect_x, self.robot_vect_y)
        point_vect, point_vect_1 = vect_from_4points(
            self.curr_x, self.curr_y, point[0], point[1])

        angle = angle_between_2vectors(
            robot_vect, robot_vect_1, point_vect, point_vect_1)
        dist = round(self.one_px * (((self.curr_x -
                     point[0]) ** 2 + (self.curr_y - point[1]) ** 2) ** 0.5))

        self.route_analytics["dist"] += dist
        if int(angle) != 0:
            self.route_analytics["rotations"] += 1

        # print(colored(f"Angle to rotate: {angle}", "blue"))
        # print(colored(f"Distance in millimetrs: {dist}", "yellow"))
        # print("---" * 10)
        if visualize:
            cv2.arrowedLine(field, (self.curr_x, self.curr_y),
                            (point[0], point[1]), (0, 255, 0), 2)

        self.curr_x, self.curr_y = point[0], point[1]
        
        if change_vector:
            self.robot_vect_x, self.robot_vect_y = point[0] + point_vect // 5, point[
                1] + point_vect_1 // 5  # Remake with line equation; Calculate new y using y = kx + b; where x = x + robot_size
        if visualize:
            cv2.arrowedLine(field, (self.curr_x, self.curr_y),
                            (self.robot_vect_x, self.robot_vect_y), (255, 0, 0), 5)
        return angle, dist

    def go(self, instruction):
        '''
        Move real robot with concret angle and distance via SPI communication with Arduino
        Warn! With current SPI library design this function will freeze code(spilib.move_robot function)
        Args:
            instruction(tuple): (angle_to_rotate, distance_to_move)
        Returns:
            Execution status and execution time(tuple: (bool, float))
        '''

        if self.mode == 1:  # Check if real mode selected
            angle, dist = self.compute_point(instruction, [], visualize=False)
            print(angle, dist)
            start_time = time.time()
            if angle != 0:
                # print("Rotate") # Force log
                direction = "right"
                if angle < 0:
                    direction = "left"
                #spilib.move_robot(direction, False, distance=abs(int(angle * self.rotation_coeff)))
            dist = int(self.mm_coef * dist)
            # spilib.move_robot("forward", interpreter_control_flag, distance=dist) # FIXIT(uncomment in real)
            time.sleep(5)  # FIXIT(Remove in real)
            going_time = time.time() - start_time
            self.route_analytics["motors_timing"] += going_time
            return (True, going_time, dist)
        else:
            return (False, 0)

    def get_sensors_data(self):
        '''
        Get values from all sensors connected to robot(works only in real mode)
        Returns:
            Sensors data(list)
        '''
        if self.mode == 1:
            sensors_data = spilib.spi_send([])
            return sensors_data

    def stop_robot(self):
        spilib.stop_robot()

    def interpret_route(self, route, monitoring_dict):
        '''
        Go through each command in route and execute it. Fully works in real mode and partially in simulation mode
        Args:
            route(list of dicts): all robot's route
            monitoring_dict(dict): communication of interpreter and min program to share current robot statistic(like steps done, time spent and etc.)
        Returns:
            bool: execution status
        '''
        steps_cnt = len(route) - 1
        execution_start = time.time()
        monitoring_dict["start_time"] = execution_start
        for instruction in route:
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
                if self.side == 1:
                    final_point[0] = self.field_size_px[1] - final_point[0]
                try:
                    status, going_time, dist_drived = self.go(final_point)
                    monitoring_dict["steps_done"] += 1
                    monitoring_dict["steps_left"] = steps_cnt - \
                        monitoring_dict["steps_done"]
                    monitoring_dict["distance_drived"] += dist_drived
                    monitoring_dict["motors_time"] += going_time
                except FileNotFoundError: # Handle spi error
                    print("[DEBUG] Warning! Invalaid SPI connection")
                    time.sleep(5)
            elif instruction["action"] == 2:
                # Reserved for servo
                pass
            elif instruction["action"] == 3:
                # Reserved for delay on high-level
                time.sleep(instruction["seconds"])
            elif instruction["action"] == 4:
                # Backward driving
                point = instruction["back_point"]
                angle, dist = self.compute_point(point, [], visualize=False, change_vector=False)
                angle = 0
                dist += int(instruction["extra_force"] * self.mm_coef)
                print(-dist)
                spilib.move_robot("forward", False, distance=-dist)
            elif instruction["action"] == 5:
                # Reserved for motors stop
                self.stop_robot()
        return True
