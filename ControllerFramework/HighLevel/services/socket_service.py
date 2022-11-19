import sys
# Top-level includes
sys.path.append("../../PathFinding") 
sys.path.append("../../PathFinding/theta*")
sys.path.append("../")
from sync import *
import socket
import json
from planner import Planner
from termcolor import colored


class SocketService:
    def __init__(self, server_host, server_port, robot_id, route):
        self.server_host = server_host
        self.server_port = server_port
        self.robot_id = robot_id
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.server_host, self.server_port))
        self.this_robot_coordinates = (-1, -1)
        # FIXIT make configurable from SocketService init
        self.planner = Planner(3.0, 2.0, 70)
        self.route = route

    def auth(self):
        self.send_packet({"action": 0, "robot_id": self.robot_id})

    def convert_coords(coord):
        data = coord.copy()

    def run(self, one_px):
        print(colored("[INFO][SOCKET] Started", "green"))
        self.one_px = one_px
        self.auth()
        while True:
            data_raw = self.sock.recv(2048)
            flag = False
            try:
                data = json.loads(data_raw.decode("utf-8"))
                if data["action"] == 3:  # data action
                    GLOBAL_STATUS["ctd_coords"] = data["robots"].copy()
                    if GLOBAL_STATUS["step_executing"]:  # Robot is driving now
                        #print("Driving now")
                        robots_coords = data["robots"].copy()
                        self.this_robot_coordinates = robots_coords[self.robot_id]
                        robots_coords.pop(self.robot_id)
                        #print("Going to:", GLOBAL_STATUS["goal_point"])
                        #print("Current coords(from CTD):", self.this_robot_coordinates)
                        obstacle_on_the_way = self.planner.check_obstacle(
                            robots_coords, self.this_robot_coordinates, GLOBAL_STATUS["goal_point"])
                        if obstacle_on_the_way[0] and not flag:
                            distance_to_obstacle = ((self.this_robot_coordinates[0] - obstacle_on_the_way[1][0]) ** 2 + (
                                self.this_robot_coordinates[1] - obstacle_on_the_way[1][1]) ** 2) ** 0.5
                            #print("Obstacles on the way\nDistance to obstacle:", distance_to_obstacle * self.one_px)
                            converted_obstacles = [[int(obstacle[0] * self.planner.virtual_map_coeff), int(
                                obstacle[1] * self.planner.virtual_map_coeff)] for obstacle in robots_coords]
                            dt_for_planner = [int(self.this_robot_coordinates[0] * self.planner.virtual_map_coeff), int(self.this_robot_coordinates[1] * self.planner.virtual_map_coeff)], [
                                int(GLOBAL_STATUS["goal_point"][0] * self.planner.virtual_map_coeff), int(GLOBAL_STATUS["goal_point"][1] * self.planner.virtual_map_coeff)]
                            bp = self.planner.generate_way(
                                *dt_for_planner, converted_obstacles)
                            # print(converted_obstacles)
                            tmp = []
                            for el in bp[1]:
                                tmp.append({
                                    "action": 1,
                                    "point": el
                                })
                            # flag = True stop flag
                            GLOBAL_STATUS["bypass"] = tmp
                        else:
                            # print("Clear")
                            pass
                        # print(obstacle_on_the_way)
                        '''
                        obstacle_on_the_way = self.planner.check_obstacle(robots_coords, self.this_robot_coordinates, (int(self.share_data["goal_point"]["point"][0] * self.planner.virtual_map_coeff), int(self.share_data["goal_point"]["point"][1] * self.planner.virtual_map_coeff)))
                        if obstacle_on_the_way:
                            print("Intersects")
                        '''
                # FIXIT Patch for new arch
                # Start route executio    n(use from debugger)
                elif data["action"] == 0:
                    self.share_data["execution_status"] = 1
                elif data["action"] == 1:  # Stop robot
                    self.share_data["execution_status"] = 3
            except json.decoder.JSONDecodeError:
                pass

    def send_packet(self, data):
        dt_converted = json.dumps(data).encode("utf-8")
        self.sock.send(dt_converted)
