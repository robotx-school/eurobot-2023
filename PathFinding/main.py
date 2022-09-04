import os
import sys
sys.path.append(os.getcwd()+'/theta*')
import LazyThetaStarPython
import time
from math import sqrt
import matplotlib.pyplot as plt
from Simulator import Simulator


if __name__ == "__main__":
    # define the world
    map_width_meter = 3.0
    map_height_meter = 2.0
    map_resolution = 20 # ml coeff
    value_non_obs = 0 # the cell is empty
    value_obs = 255 # the cell is blocked
    obstacles = [(5, 5, 3, 3), (17, 22, 3, 3), (10, 30, 3, 3)] # [(left_bottom_corner_x_y, size_x, size_y)]
    # create a simulator
    MySimulator = Simulator(map_width_meter, map_height_meter, map_resolution, value_non_obs, value_obs)
    # add obstacles
    for obst in obstacles:
        for x in range(obst[0], obst[0] + obst[2]):
            for y in range(obst[1], obst[1] + obst[3]):
                MySimulator.map_array[x][y] = value_obs

    # convert 2D numpy array to 1D list
    world_map = MySimulator.map_array.flatten().tolist() # final world map

    # Points
    start = [4, 0]
    targets = [27, 22]
    # Solve task
    t0 = time.time()
    path_single, distance_single = LazyThetaStarPython.FindPath(start, targets, world_map, MySimulator.map_width, MySimulator.map_height)
    t1 = time.time()
    print("Time used for a single path is [sec]: " + str(t1-t0))
    print("This is the path.")
    print("Total distance: " + str(distance_single))
    distance_check = 0.0
    for idx in range(0,len(path_single), 2):
        str_print = str(path_single[idx]) + ', ' + str(path_single[idx+1])
        print(str_print)
        if idx > 0:
            distance_check = distance_check + sqrt((path_single[idx]-path_single[idx-2])**2 + (path_single[idx+1]-path_single[idx-1])**2)
    print("Distance computed afterwards: " + str(distance_check))
    # visualization
    MySimulator.plot_single_path(path_single)
    plt.show()
