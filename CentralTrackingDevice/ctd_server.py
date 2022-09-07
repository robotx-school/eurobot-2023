import socket
import threading
import json
import time

class Localization:
    '''
    Placeholder for localization module
    '''
    def __init__(self):
        # API emulation
        self.robots_positions = [(-1, -1), (-1, -1), (-1, -1), (-1, -1)] # Robots coordinates on field will be legacy

    def get_coords(self):
        # API emulation
        return self.robots_positions

class ConnectedRobot:
    '''
    Unique thread worker for each robot and debugger connected
    '''
    def __init__(self, addr, connectcion, robot_id=None):
        self.robot_id = robot_id
        self.addr = addr
        self.connection = connectcion

    def send_packet(self, data):
        try:
            self.connection.send(json.dumps(data).encode("utf-8"))
        except BrokenPipeError:
            print(f"[DEBUG] Client {self.addr} disconnected")
            ctdsocket.delete_client(self.addr)
                
    def listen_loop(self):
        while True:
            try:
                data_raw = self.connection.recv(2048)
            except ConnectionResetError:
                ctdsocket.delete_client(self.addr)
            if data_raw:
                data = json.loads(data_raw.decode("utf-8"))
                if self.robot_id != -1: # Robot part
                    if data["action"] == 0: # Auth/change config
                        self.robot_id = int(data["robot_id"])
                        print("[DEBUG] Client auth packet")
                    elif data["action"] == 1: # Dbg output
                        print(self.addr, self.robot_id)
                        print(CentralSocketServer.robots_connected)
                else: # Debugger client part 
                    #print("[DEBUG] From debugger")
                    if data["action"] in [0, 1]:
                        #self.send_packet({"action": 0}) # Start route
                        ctdsocket.send_to({"action": int(data["action"])}, data["to_addr"])
                    elif data["action"] == 3: # change robot coordinates Only for dev without real CTD and localization alg
                        localizer.robots_positions[data["robot_id"]] = tuple(data["new_coords"])
                    elif data["action"] == 10:
                        packet = []
                        for robot in ctdsocket.robots_connected:
                            packet.append([robot, ctdsocket.robots_connected[robot].robot_id])
                        self.send_packet({"data": packet})
            else:
                print(f"[DEBUG] Client {self.addr} disconnected")
                ctdsocket.delete_client(self.addr)
                break

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


    def broadcast_coordinates(self):
        while True:
            for client in list(self.robots_connected):
                try:
                    if self.robots_connected[client].robot_id != -1:
                        self.robots_connected[client].send_packet({"action": 3, "robots": localizer.get_coords()}) # action - 3 is data action
                except KeyError:
                    pass
                time.sleep(0.02) # Too fast without timing
        
    def work_loop(self):
        while True: 
            conn, addr = self.socket.accept()
            print("[DEBUG] New client")
            formatted_addr = f"{addr[0]}:{addr[1]}"
            self.robots_connected[formatted_addr] = ConnectedRobot(formatted_addr, conn)
            threading.Thread(target=self.robots_connected[formatted_addr].listen_loop).start()
    
    def send_to(self, packet, addr):
        for client in self.robots_connected:
            if client == addr:
                print("[DEBUG] Client found")
                self.robots_connected[client].send_packet(packet)
    
    def delete_client(self, addr):
        try:
            del self.robots_connected[addr]
            return 1
        except KeyError:
            return -1

# Global status variables
# 0 - no execution
# 1 - execution starting request
# 2 - execution is going
# 3 - execution stop request



if __name__ == "__main__":
    print("[DEBUG] Testing mode")
    ctdsocket = CentralSocketServer()
    localizer = Localization()
    threading.Thread(target=lambda: ctdsocket.broadcast_coordinates()).start()
    ctdsocket.work_loop()
