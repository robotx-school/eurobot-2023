import os
import sys
sys.path.append(os.getcwd() + '/theta*') # Compiled version for linux
import LazyThetaStarPython
import time
from math import sqrt
import matplotlib.pyplot as plt
from Simulator import Simulator


class Planner:
    def __init__(self, width, height, resolution):
        self.map_width_meter = width
        self.map_height_meter = height
        self.map_resolution = resolution # multiply coeff, so in result we will have 60x40 matrix. If we have field with size 3000x2000mm we will split all field to squares with 50mm side.
        self.value_non_obs = 0
        self.value_obs = 255
        self.create_base_map()

    def create_base_map(self):
        self.simulator = Simulator(self.map_width_meter, self.map_height_meter, self.map_resolution, self.value_non_obs, self.value_obs)

    def update_obstacles(self, obstacles):
        self.create_base_map()
        for obst in obstacles:
            for x in range(obst[0], obst[0] + obst[2]):
                for y in range(obst[1], obst[1] + obst[3]):
                    self.simulator.map_array[x][y] = self.value_obs

    def generate_way(self, start_point, dest_point, obstacles):
        self.update_obstacles(obstacles)
        world_map = self.simulator.map_array.flatten().tolist()
        path_single, distance_single = LazyThetaStarPython.FindPath(start_point, dest_point, world_map, self.simulator.map_width, self.simulator.map_height)
        return path_single, [path_single[x: x + 2] for x in range(0, len(path_single), 2)]

    def visualize(self, path_single):
        self.simulator.plot_single_path(path_single)
        plt.show()

if __name__ == "__main__":
    obstacles = [(5, 5, 3, 3), (17, 22, 3, 3), (10, 30, 3, 3)] # [(left_bottom_corner_x_y, size_x, size_y)]
    planner = Planner(3.0, 2.0, 20)
    t_0 = time.time()
    path_single, points = planner.generate_way((4, 0), (27, 22), obstacles)
    print(time.time() - t_0)
    planner.visualize(path_single)
