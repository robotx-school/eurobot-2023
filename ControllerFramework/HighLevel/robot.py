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
        self.robot_direction = robot_direction
        self.generate_vector()

        self.mode = mode  # (0 - virtual mode; 1 - real mode)
        self.field_side_real = field_side_real
        self.field_size_px = field_size_px

    def generate_vector(self):
        if self.robot_direction == "E":
            self.robot_vect_x, self.robot_vect_y = self.curr_x + \
                self.robot_size, self.curr_y  # Right(East)
        elif self.robot_direction == "W":
            self.robot_vect_x, self.robot_vect_y = self.curr_x - \
                self.robot_size, self.curr_y  # Left(West)
        elif self.robot_direction == "N":
            self.robot_vect_x, self.robot_vect_y = self.curr_x, self.curr_y - \
                self.robot_size  # Top(North)
        elif self.robot_direction == "S":
            self.robot_vect_x, self.robot_vect_y = self.curr_x, self.curr_y + \
                self.robot_size  # Bottom(South)

    def calculate_robot_start_vector(self, robot_coords, direction):
        self.start_point = robot_coords
        self.curr_x, self.curr_y = robot_coords
        self.robot_direction = direction
        self.generate_vector()

    def compute_point(self, point, field, append_point=True, visualize=True, visualize_color=(0, 255, 0), visualize_vector_color=(255, 0, 0), change_vector=True):
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
            self.curr_path_points.append({"action": 1, "point": point})
        robot_vect, robot_vect_1 = vect_from_4points(
            self.curr_x, self.curr_y, self.robot_vect_x, self.robot_vect_y)
        point_vect, point_vect_1 = vect_from_4points(
            self.curr_x, self.curr_y, point[0], point[1])

        angle = angle_between_2vectors(
            robot_vect, robot_vect_1, point_vect, point_vect_1)
        dist = (((self.curr_x -
                     point[0]) ** 2 + (self.curr_y - point[1]) ** 2) ** 0.5)

        self.route_analytics["dist"] += dist

        if int(angle) != 0:
            self.route_analytics["rotations"] += 1

        # print(colored(f"Angle to rotate: {angle}", "blue"))
        # print(colored(f"Distance in millimetrs: {dist}", "yellow"))
        # print("---" * 10)
        if visualize:
            cv2.arrowedLine(field, (int(self.curr_x), int(self.curr_y)),
                            (int(point[0]), int(point[1])), visualize_color, 2)
        self.curr_x, self.curr_y = point[0], point[1]

        if change_vector:
            self.robot_vect_x, self.robot_vect_y = point[0] + point_vect // 5, point[
                1] + point_vect_1 // 5  # Remake with line equation; Calculate new y using y = kx + b; where x = x + robot_size
        if visualize:
            cv2.arrowedLine(field, (self.curr_x, self.curr_y),
                            (self.robot_vect_x, self.robot_vect_y), visualize_vector_color, 5)
        return angle, dist

    def stop_robot(self):
        spilib.stop_robot()
