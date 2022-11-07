import socket
import json


class SocketService:
    def __init__(self, robot_id, route, server_host="localhost", server_port=7070):
        self.server_host = server_host
        self.server_port = server_port
        self.this_robot_id = robot_id
        self.route = route
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.server_host, self.server_port))
        self.this_robot_coordinates = (-1, -1)
        print("[DEBUG] Service init")

    def auth(self):
        self.send_packet({"action": 0, "robot_id": self.this_robot_id})

    def send_packet(self, data):
        dt_converted = json.dumps(data).encode("utf-8")
        self.sock.send(dt_converted)

    def run(self):
        self.auth()
        while True:
            data_raw = self.sock.recv(2028)
            try:
                data = json.loads(data_raw.decode("utf-8"))
                if data["action"] == 3:
                    GLOBAL_STATUS["ctd_coords"] = data["robots"].copy()
                    if GLOBAL_STATUS["step_executing"]:
                        print("Driving")
            except json.decoder.JSONDecodeError:
                print("Decoding error")
