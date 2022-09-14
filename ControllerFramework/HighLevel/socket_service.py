import socket
import json
import sys
sys.path.append("../../PathFinding") # Messy, but easy for develop
sys.path.append("../../PathFinding/theta*")
from planner import Planner

class SocketService:
    def __init__(self, server_host, server_port, robot_id):
        self.server_host = server_host
        self.server_port = server_port
        self.robot_id = robot_id
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.server_host, self.server_port))
        self.this_robot_coordinates = (-1, -1)
        self.planner = Planner(3.0, 2.0, 20) # FIXIT make configurable from SocketService init

    def update_share_data(self, share_data):
        self.share_data = share_data

    def auth(self):
        self.send_packet({"action": 0, "robot_id": self.robot_id})

    def listen_loop(self):
        while True:
            data_raw = self.sock.recv(2048)
            try:
                data = json.loads(data_raw.decode("utf-8"))
                
                if data["action"] == 3: # data action
                    if self.share_data["step_executing"]: # Robot is driving now
                        robots_coords = data["robots"]
                        self.this_robot_coordinates = robots_coords[self.robot_id]
                        robots_coords.pop(self.robot_id)
                        print("Going to:", self.share_data["goal_point"])
                        print("Current coords(from CTD):", self.this_robot_coordinates)
                        obstacle_on_the_way = self.planner.check_obstacle(robots_coords, self.this_robot_coordinates, (int(self.share_data["goal_point"]["point"][0] * self.planner.virtual_map_coeff), int(self.share_data["goal_point"]["point"][1] * self.planner.virtual_map_coeff)))
                        if obstacle_on_the_way:
                            print("Intersects")
                elif data["action"] == 0: # Start route execution(use from debugger)
                    self.share_data["execution_status"] = 1
                elif data["action"] == 1: # Stop robot
                    self.share_data["execution_status"] = 3
            except json.decoder.JSONDecodeError:
                pass


    def send_packet(self, data):
        dt_converted = json.dumps(data).encode("utf-8")
        self.sock.send(dt_converted)
