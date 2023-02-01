import threading
import socket
import json


class TaskManager:
    def __init__():
        pass

class MapServer:
    '''
    MapServer - Service to store and fetch actual info of field from CTD. Store 4 points - 4 robots coords.
    robot_coords = [(this_robot), (second_robot), (enemy_0), (enemy_1)]
    '''
    def __init__(self, camera_tcp_host="localhost", camera_tcp_port=7070, updater_autorun=True):
        self.robots_coords = [[-1, -1], [-1, -1], [-1, -1], [-1, -1]] # INIT STATE; -1; -1; no robots on map
        self.camera_host = camera_tcp_host
        self.camera_port = camera_tcp_port
        self.camera_socket = None
        self.connect_ctd() # Connect to tcp camera socket
        self.updater_enabled = True
        if updater_autorun:
            self.updater_thread = threading.Thread(target=lambda: self.updater())
            self.updater_thread.start()


    def send_payload(self, data):
        '''
        High-level wrapper of socket send to support json payload. Serialize json/dict to string and encode to binary utf-8.
        '''
        dt_converted = json.dumps(data).encode("utf-8")
        self.camera_socket.send(dt_converted)

    def camera_auth(self):
        '''
        This methods sends data to CTD to get permission to get robots coords. Send this packet before others.
        '''
        self.send_payload({"action": 0, "robot_id": 0}) # no realtime robot id

    def connect_ctd(self):
        '''
        Connect to CTD camera tcp socket and store connection in self. 
        WARN! Run in __init__, before updater thread run!
        '''
        self.camera_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.camera_socket.connect((self.camera_host, self.camera_port))
        self.camera_auth()
    def updater(self):
        while self.updater_enabled:
            data_raw = self.camera_socket.recv(2048)
            try:
                data = json.loads(data_raw.decode("utf-8"))
            except:
                data = {}  # null data; for error handling on corrupted json payload
            if data and data["action"] == 3: 
                self.robots_coords = data["robots"].copy()

    def __str__(self):
        '''
        Pretty print for debug 
        FIXIT
        ''' 
        return f"This robot: {self.robots_coords[0][0]}, {self.robots_coords[0][1]}"
if __name__ == "__main__":
    map_server = MapServer()
    while True:
        print(map_server.robots_coords)