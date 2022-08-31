import socket
import threading
import json

class ConnectedRobot:
    def __init__(self, addr, connectcion, robot_id=None):
        self.robot_id = robot_id
        self.addr = addr
        self.connection = connectcion
    
    def listen_loop(self):
        while True:
            data_raw = self.connection.recv(2048)
            data = json.loads(data_raw.decode("utf-8"))
            if data["action"] == 0: # Config
                self.robot_id = int(data["robot_id"])
            elif data["action"] == 1:
                print("Test")


class CentralSocketServer:
    def __init__(self, host='', port=7070, max_clients=3):
        self.host = host
        self.port = port
        self.max_clients = max_clients
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.host, self.port))
        self.socket.listen(self.max_clients)
        self.robots_connected = {} # client_host: robot class object
        print("[DEBUG] Socket server ready")

    def work_loop(self):
        while True:
            conn, addr = self.socket.accept()
            self.robots_connected[addr] = ConnectedRobot(addr, conn)
            
