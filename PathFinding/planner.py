import os
import sys
sys.path.append(os.getcwd() + '/theta*') # Compiled version for linux
import LazyThetaStarPython
import time
from math import sqrt
import matplotlib.pyplot as plt
from Simulator import Simulator
from shapely.geometry import Polygon, LineString
from termcolor import colored

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
    def __init__(self, width, height, resolution, real_field_width=3000, virtual_map_px_width=1532):
        self.map_width_meter = width
        self.map_height_meter = height
        self.map_resolution = resolution # multiply coeff, so in result we will have 60x40 matrix. If we have field with size 3000x2000mm we will split all field to squares with 50mm side.
        self.value_non_obs = 0
        self.value_obs = 255
        self.create_base_map()
        self.coords_coeff = real_field_width / (self.map_width_meter * self.map_resolution)
        self.virtual_map_coeff = (self.map_width_meter * self.map_resolution) / virtual_map_px_width
        print(self.virtual_map_coeff)
        self.matrix_size = self.map_resolution * width + height * self.map_resolution # Temp value for time checking

    def create_base_map(self):
        '''
        Create map of field without obstacles
        '''
        self.simulator = Simulator(self.map_width_meter, self.map_height_meter, self.map_resolution, self.value_non_obs, self.value_obs)

    def update_obstacles(self, obstacles):
        '''
        Set obstacles on map
        Args:
            obstacles (list of tuples): list of obstacles to set on map
        Obstacle tuple contains 4 items:
            (left_bottom_corner_x, left_bottom_corner_y, x_width, y_height)
        '''
        self.create_base_map()
        for obst in obstacles:
            for y in range(obst[0], obst[0] + obst[2]):
                for x in range(obst[1], obst[1] + obst[3]):
                    self.simulator.map_array[x][y] = self.value_obs

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
        self.update_obstacles(obstacles)
        self.world_map = self.simulator.map_array.flatten().tolist()
        path_single, distance_single = LazyThetaStarPython.FindPath(start_point, dest_point, self.world_map, self.simulator.map_width, self.simulator.map_height)
        return path_single, [path_single[x: x + 2] for x in range(0, len(path_single), 2)], distance_single

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

        our_way = LineString([start_point, dest_point])
        for obstacle in obstacles:
            print(obstacle)
            if obstacle[0] != -1:
                obstacle_polygon = Polygon([(obstacle[0] - 1, obstacle[1] + 1), (obstacle[0] + 1, obstacle[1] - 1), (obstacle[0] + obstacle[2], obstacle[1]), (obstacle[0] + obstacle[2], obstacle[1] + obstacle[3])])
                if our_way.intersects(obstacle_polygon):
                    #print("Intersects with obstacle:", obstacle[0], obstacle[1])
                    return (True, (obstacle[0], obstacle[1]))
        return (False, False)


if __name__ == "__main__":
    print("[DEBUG] Testing Planner with local data")
    obstacles = [(5, 6, 3, 3), (22, 17, 3, 3), (30, 10, 3, 3)] # [(left_bottom_corner_x_y, size_x, size_y)]
    planner = Planner(3.0, 2.0, 20)
    start_point = (0, 8)
    dest_point = (10, 8)
    print(planner.check_obstacle(obstacles, start_point, dest_point))
    direct_length = (((start_point[0] - dest_point[0]) ** 2) + ((start_point[1] - dest_point[1]) ** 2)) ** 0.5
    t_0 = time.time()
    path_single, points, distance_single = planner.generate_way(start_point, dest_point, obstacles)
    t_1 = time.time()
    print("Calculation time:", f"{colored(t_1 - t_0, 'green')} ~ {colored(1 / (t_1 - t_0), 'yellow')} calculations per second")
    print("Field matrix items count:", len(planner.world_map))
    print("Obstacles count:", len(obstacles))
    print("Points to follow:", colored(points, "green"))
    print("Extra bypass points count:", len(points) - 2)
    print("Bypass route length:", distance_single)
    print("Direct length(line):", direct_length)
    print("Length diff:", colored(f"{distance_single / direct_length * 100 - 100}%", "red"))
    planner.visualize(path_single)
