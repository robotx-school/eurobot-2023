import socket
import json

class SocketService:
    def __init__(self, server_host, server_port, robot_id):
        self.server_host = server_host
        self.server_port = server_port
        self.robot_id = robot_id
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.server_host, self.server_port))

    def update_share_data(self, share_data):
        self.share_data = share_data

    def auth(self):
        self.send_packet({"action": 0, "robot_id": self.robot_id})

    def listen_loop(self):
        while True:
            data_raw = self.sock.recv(2048)
            #print("Data", data_raw)
            data = json.loads(data_raw.decode("utf-8"))
            
            if data["action"] == 3: # data action
                print(data["robots"])
            elif data["action"] == 0: # Start route execution(use from debugger)
                self.share_data["execution_status"] = 1
            elif data["action"] == 1: # Stop robot
                self.share_data["execution_status"] = 3
            

    def send_packet(self, data):
        dt_converted = json.dumps(data).encode("utf-8")
        self.sock.send(dt_converted)
    