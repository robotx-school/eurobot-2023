from termcolor import colored
from shapely.geometry import Polygon, LineString
from Simulator import Simulator
import matplotlib.pyplot as plt
from math import sqrt
import time
import sys
# sys.path.append('./Lazy-Theta-with-optimization-any-angle-pathfinding/build') # Compiled version for linux
sys.path.append("../../PathFinding")
sys.path.append("../../PathFinding/theta*")
sys.path.append("../")
sys.path.append("./theta*")
# RPi
<<<<<<< HEAD
sys.path.append(
    "/home/pi/EB/eurobot-2023/PathFinding/Lazy-Theta-with-optimization-any-angle-pathfinding/build")
=======
sys.path.append("/home/pi/net/eurobot-2023/PathFinding/Lazy-Theta-with-optimization-any-angle-pathfinding/build")
>>>>>>> 8f62586ce5467b9bb41916c2e1378854fd1653e6
import LazyThetaStarPython
'''
Important note!
Planner works in local coordinates system and coordinates are not the same as robot controller. So you have to careful;
'''


class Planner:
    '''
    Local Planner class. Local Planner is a system to recreate route considering obstacles
    It have 2 parts:
    * Obstacles checker - check if current route(line between start point and dest point) intersects with obstacles
    * Route recreator - create route between to points if obstacles checker returned, that we can bump into obstacle.
    '''

    def __init__(self, width, height, resolution, logger=None, real_field_width=3000, virtual_map_px_width=1532):
        self.map_width_meter = width
        self.map_height_meter = height
        # multiply coeff, so in result we will have 60x40 matrix. If we have field with size 3000x2000mm we will split all field to squares with 50mm side.
        self.map_resolution = resolution
        self.value_non_obs = 0
        self.value_obs = 255
        self.create_base_map()
        self.virtual_map_coeff = real_field_width / \
            (self.map_resolution * width)
        print(self.virtual_map_coeff)
        # print(self.map_width_meter * self.map_resolution, self.map_height_meter * self.map_resolution)
        self.matrix_size = self.map_resolution * width + height * \
            self.map_resolution  # Temp value for time checking
        # logger.write("PLANNER", "INFO", "Planner ready!")

    def create_base_map(self):
        '''
        Create map of field without obstacles
        '''
        self.simulator = Simulator(self.map_width_meter, self.map_height_meter,
                                   self.map_resolution, self.value_non_obs, self.value_obs)

    def new_obstacles_updater(self, obstacles):
        OBST_BASE_SIZE = 20  # In squares
        self.create_base_map()
        for obst in obstacles:
            if obst != [-1, -1]:
                # One row
                left_top_corner = obst[0] - \
                    OBST_BASE_SIZE  # - OBST_BASE_SIZE # - 4
                right_top_corner = obst[0] + \
                    OBST_BASE_SIZE  # + OBST_BASE_SIZE #+ 7
                # Columns count
                column_top = obst[1] - OBST_BASE_SIZE  # - 7
                column_bottom = obst[1] + OBST_BASE_SIZE  # + 7
                for row in range(column_top, column_bottom + 1):
                    for sq in range(left_top_corner, right_top_corner + 1):
                        if row >= 0 and sq >= 0:
                            try:
                                self.simulator.map_array[int(
                                    self.map_height_meter * self.map_resolution) - row][sq] = self.value_obs
                            except IndexError:
                                pass

    def update_obstacles(self, obstacles):
        '''
        OLD
        Set obstacles on map
        Args:
            obstacles (list of tuples): list of obstacles to set on map
        Obstacle tuple contains 4 items:
            (left_bottom_corner_x, left_bottom_corner_y, x_width, y_height)
        '''
        self.create_base_map()
        for obst in obstacles:
            if obst[0][0] != -1 and obst[0][1] != -1:
                for i in range(len(obst)):
                    self.simulator.map_array[int(
                        self.map_height_meter * self.map_resolution - obst[i][1])][obst[i][0]] = self.value_obs

    def generate_way(self, start_point, dest_point, obstacles):
        '''
        Create route between 2 points considering obstacles
        Args:
            start_point(tuple): point from robot start (x, y)
            dest_point(tuple): point robot dest (x, y)
            obstacles(tuple): obstacles on field for current moment(declaration of obstacles you can see in function `update_obstacles`)
        Returns:
            path_single(list): points coords in 1D array(the one who wrote lib was apparently drunk)
            points to follow(list of tuples): converted points for robot to go
            distance_single(float): theta* calculated path length
        '''
        print(colored(
            f"[DEBUG][PLANNER] Calc for: {start_point, dest_point, obstacles}", "magenta"))
        # self.update_obstacles(obstacles)
        self.new_obstacles_updater(obstacles)
        self.world_map = self.simulator.map_array.flatten().tolist()
        # print(start_point, dest_point)
        start_point = list(start_point)
<<<<<<< HEAD
        # start_point[0] = start_point[0]
        dest_point = list(dest_point)
        # dest_point[0] = 210 - dest_point[0]
        if start_point[0] == 210:
            start_point[0] = 209
        if dest_point[0] == 210:
            dest_point[0] = 209

        print(start_point, dest_point)
        start_point[1] = int(self.map_height_meter *
                             self.map_resolution - start_point[1])
        dest_point[1] = int(self.map_height_meter *
                            self.map_resolution - dest_point[1])
        path_single, distance_single = LazyThetaStarPython.FindPath(
            start_point, dest_point, self.world_map, self.simulator.map_width, self.simulator.map_height)
=======
        #start_point[0] = start_point[0]
        dest_point = list(dest_point)
        #dest_point[0] = 210 - dest_point[0]
        if start_point[0] == 210:
            start_point[0] = 209

        print(start_point, dest_point)
        start_point[1] = int(self.map_height_meter * self.map_resolution - start_point[1])
        dest_point[1] = int(self.map_height_meter * self.map_resolution - dest_point[1])
        path_single, distance_single = LazyThetaStarPython.FindPath(start_point, dest_point, self.world_map, self.simulator.map_width, self.simulator.map_height)
>>>>>>> 8f62586ce5467b9bb41916c2e1378854fd1653e6
        return path_single, [[path_single[x] * self.virtual_map_coeff, (140 - path_single[x + 1]) * self.virtual_map_coeff] for x in range(2, len(path_single), 2)], distance_single

    def visualize(self, path_single):
        '''
        Visualize bypass route
        Args:
            path_single(list): points coords in 1D array
        '''
        self.simulator.plot_single_path(path_single)
        plt.show()

    def check_obstacle(self, obstacles, start_point, dest_point):
        '''
        Check if current route path(line path between two points) intersects with any obstacle.
        !Note! This function will return the first intersectable obstacle
        Args:
            obstacles(list of tuples): obstacles list
            start_point(tuple): coordinates of start point
            dest_point(tuple): coordinates of dest point
        Retruns:
            intersects(tuple): [0] - is there an obstacle on our way; [1] - coordinates of intersectable obstacle
        '''
        # print(obstacles, start_point, dest_point)
        our_way = LineString([start_point, dest_point])
        for obstacle in obstacles:
            if obstacle[0] != -1 and obstacle[1] != -1:
                obstacle_polygon = Polygon([(obstacle[0] - 200, obstacle[1] - 200), (obstacle[0] + 200, obstacle[1] - 200),
                                           (obstacle[0] + 200, obstacle[1] + 200), (obstacle[0] - 200, obstacle[1] + 200)])
                # obstacle_polygon = Polygon([(obstacle[0] - 1, obstacle[1] + 1), (obstacle[0] + 1, obstacle[1] - 1), (obstacle[0] + obstacle[2], obstacle[1]), (obstacle[0] + obstacle[2], obstacle[1] + obstacle[3])])
                if our_way.intersects(obstacle_polygon):
                    # print("Intersects with obstacle:", obstacle[0], obstacle[1])
                    return (True, (obstacle[0], obstacle[1]))
        return (False, False)

    def convert_controller_to_mm(self, other_robots, this_robot_coordinates, dest_point):
        converted_obstacles = [[int(obstacle[0] / planner.virtual_map_coeff), int(
            obstacle[1] / planner.virtual_map_coeff)] for obstacle in other_robots]
        dt_for_planner = [int(this_robot_coordinates[0] / planner.virtual_map_coeff), int(this_robot_coordinates[1] / planner.virtual_map_coeff)], [
            int(dest_point[0] / planner.virtual_map_coeff), int(dest_point[1] / planner.virtual_map_coeff)]

        return converted_obstacles, dt_for_planner


if __name__ == "__main__":
    print("[DEBUG] Testing Planner with local data")
<<<<<<< HEAD
    # obstacles = [[(12, 47), (14, 47), (14, 49), (12, 49), (13, 48)]] # [(left_bottom_corner_x_y, size_x, size_y)]
    # obstacles = [[-1, -1], [21, 69], [-1, -1]] #[[10, 69], [-1, -1], [-1, -1]]
    obstacles = [[-1, -1], [105, 100], [50, 50]]
    
=======
    #obstacles = [[(12, 47), (14, 47), (14, 49), (12, 49), (13, 48)]] # [(left_bottom_corner_x_y, size_x, size_y)]
    #obstacles = [[-1, -1], [21, 69], [-1, -1]] #[[10, 69], [-1, -1], [-1, -1]]
    obstacles = [[-1, -1], [61, 49], [-1, -1]]
    #([61, 2], [61, 105], [[0, 0], [61, 49], [0, 0]])
    planner = Planner(3.0, 2.0, 70)
    start_point = (61, 2)
    dest_point = (61, 105)
>>>>>>> 8f62586ce5467b9bb41916c2e1378854fd1653e6

    planner = Planner(3.0, 2.0, 70)
    #print(planner.convert_controller_to_mm([[-1, -1], [1500, 1000],[-1, -1]], [0, 1000], [3000, 1000]))
    # converted_obstacles = [[int(obstacle[0] / planner.virtual_map_coeff), int(
    #                    obstacle[1] / planner.virtual_map_coeff)] for obstacle in other_robots]
    # dt_for_planner = [int(this_robot_coordinates[0] / planner.virtual_map_coeff), int(this_robot_coordinates[1] / planner.virtual_map_coeff)], [
    #    int(point[0] / planner.virtual_map_coeff), int(point[1] / planner.virtual_map_coeff)]

    start_point = (0, 90)
    dest_point = (210, 90)

    # print(planner.check_obstacle(obstacles, start_point, dest_point))
    direct_length = (((start_point[0] - dest_point[0]) ** 2) +
                     ((start_point[1] - dest_point[1]) ** 2)) ** 0.5
    t_0 = time.time()
    path_single, points, distance_single = planner.generate_way(
        start_point, dest_point, obstacles)
    t_1 = time.time()
    print("Calculation time:",
          f"{colored(t_1 - t_0, 'green')} ~ {colored(1 / (t_1 - t_0), 'yellow')} calculations per second")
    print("Field matrix items count:", len(planner.world_map))
    print("Obstacles count:", len(obstacles))
    print("Points to follow:", colored(points, "green"))
    print("Extra bypass points count:", len(points) - 1)
    print("Bypass route length:", distance_single)
    print("Direct length(line):", direct_length)
    print("Length diff:", colored(
        f"{distance_single / direct_length * 100 - 100}%", "red"))
    planner.visualize(path_single)
<<<<<<< HEAD
=======


>>>>>>> 8f62586ce5467b9bb41916c2e1378854fd1653e6
