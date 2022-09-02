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
            if data["action"] == 0: # Auth/change config
                self.robot_id = int(data["robot_id"])
                print("[DEBUG] Client auth packet")
            elif data["action"] == 1: # Dbg output
                print(self.addr, self.robot_id)
                print(CentralSocketServer.robots_connected)


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
            print("[DEBUG] New client")
            self.robots_connected[addr] = ConnectedRobot(addr, conn)
            threading.Thread(target=self.robots_connected[addr].listen_loop).start()

# Global status variables
# 0 - no execution
# 1 - execution starting request
# 2 - execution is going
# 3 - execution stop request



if __name__ == "__main__":
    print("[DEBUG] Testing mode")
    ctdsocket = CentralSocketServer()
    ctdsocket.work_loop()