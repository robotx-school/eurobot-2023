from geometry import *
import cv2

class Robot:
    '''
    High level(RPi level) robot declaration
    Available execution as virtual machine(simulation) or as high level commander under Arduino via SPI

    '''
    def __init__(self, robot_size, start_point, robot_direction, mm_coef, rotation_coeff, one_px, mode=0):
        self.robot_size = robot_size
        self.side = 0
        self.route_analytics = {"dist": 0, "rotations": 0, "motors_timing": 0}
        self.mm_coef = mm_coef # Dev robot = 9.52381
        self.rotation_coeff = rotation_coeff # Dev robot = 12.1
        self.one_px = one_px
        self.curr_path_points = []
        self.curr_x, self.curr_y = start_point # Robot start
        # Generate robot vector
        self.robot_vect_x, self.robot_vect_y = self.curr_x + self.robot_size, self.curr_y # Right(East)
        self.mode = mode # (0 - virtual mode; 1 - real mode)
        
    
    def compute_point(self, point, field):
        '''
        Compute angle to rotate and distance to ride for next point and also recalculate finish point and vector angle

        Args:
            point(tuple): point to follow (x, y) in px
            field(numpy array): image of field in 2d fro top view
        Returns:
            Modify field img
            Angle to rotate (float)
            Distancse in millimeters (int)
        '''
        self.curr_path_points.append(point)
        robot_vect, robot_vect_1 = vect_from_4points(self.curr_x, self.curr_y, self.robot_vect_x, self.robot_vect_y)
        point_vect, point_vect_1 = vect_from_4points(self.curr_x, self.curr_y, point[0], point[1])

        angle = angle_between_2vectors(robot_vect, robot_vect_1, point_vect, point_vect_1)
        dist = round(self.one_px * (((self.curr_x - point[0]) ** 2 + (self.curr_y - point[1]) ** 2) ** 0.5))
        
        self.route_analytics["dist"] += dist
        if int(angle) != 0:
            self.route_analytics["rotations"] += 1

        # print(colored(f"Angle to rotate: {angle}", "blue"))
        # print(colored(f"Distance in millimetrs: {dist}", "yellow"))
        # print("---" * 10)
        cv2.arrowedLine(field, (self.curr_x, self.curr_y), (point[0], point[1]), (0, 255, 0), 2)

        self.curr_x, self.curr_y = point[0], point[1]

        self.robot_vect_x, self.robot_vect_y = point[0] + point_vect // 5, point[
            1] + point_vect_1 // 5 # Remake with line equation; Calculate new y using y = kx + b; where x = x + robot_size
        cv2.arrowedLine(field, (self.curr_x, self.curr_y), (self.robot_vect_x, self.robot_vect_y), (255, 0, 0), 5)
        return angle, dist
    
    def go(self, instruction):
        '''
        Move real robot with concret angle and distance via SPI communication with Arduino
        Warn! With current SPI library design this function will freeze code(spilib.move_robot function)
        Args:
            instruction(tuple): (angle_to_rotate, distance_to_move)
        Returns:
            Execution status and execution time
        '''
        
        if self.mode == 1: # Check if real mode selected
            angle, dist = instruction
            start_time = time.time()
            if angle != 0:
                # print("Rotate") # Force log
                direction = "right"
                if angle < 0:
                    direction = "left"
                spilib.move_robot(direction, False, distance=abs(int(angle * self.rotation_coeff)))
            spilib.move_robot("forward", interpreter_control_flag, distance=int(mm_coef * dist))
            going_time = time.time() - start_time
            self.route_analytics["motors_timing"] += going_time
            return (True, going_time)
        else:
            return (False, 0)

    def interpret_route(self, route):
        '''
        Go through each command in route and execute it
        '''
        for instruction in route:
            pass
