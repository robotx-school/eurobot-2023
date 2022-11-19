import socket
import threading
import json
import time
from flask import Flask, render_template, jsonify, request
import tkinter as tk


class WebUI:
    def __init__(self, name, localizer, host='0.0.0.0', port='8080'):
        self.app = Flask(name)
        self.host = host
        self.port = port
        self.app.config["TEMPLATES_AUTO_RELOAD"] = True
        self.localizer = localizer

        @self.app.route('/')
        def __index():
            return self.index()

        @self.app.route('/api/update_coords', methods=['POST'])
        def update_coords():
            for robot_id in range(0, 4):
                self.localizer.robots_positions[robot_id] = eval(
                    request.form.get(f'coords{robot_id}'))
            return jsonify({"status": True})

    def index(self):
        #print(self.localizer.robots_positions)
        return render_template('index.html', coords=self.localizer.robots_positions)

    def run(self):
        self.app.run(host=self.host, port=self.port)


class Localization:
    '''
    Placeholder for localization module
    '''

    def __init__(self):
        # API emulation
        # Robots coordinates on field will be legacy
        self.robots_positions = [(-1, -1), (-1, -1), (-1, -1), (-1, -1)]

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
                if self.robot_id != -1:  # Robot part
                    if data["action"] == 0:  # Auth/change config
                        self.robot_id = int(data["robot_id"])
                        print("[DEBUG] Client auth packet")
                    elif data["action"] == 1:  # Dbg output
                        print(self.addr, self.robot_id)
                        print(CentralSocketServer.robots_connected)
                else:  # Debugger client part
                    #print("[DEBUG] From debugger")
                    if data["action"] in [0, 1]:
                        # self.send_packet({"action": 0}) # Start route
                        ctdsocket.send_to(
                            {"action": int(data["action"])}, data["to_addr"])
                    # change robot coordinates Only for dev without real CTD and localization alg
                    elif data["action"] == 3:
                        localizer.robots_positions[data["robot_id"]] = tuple(
                            data["new_coords"])
                    elif data["action"] == 10:
                        packet = []
                        for robot in ctdsocket.robots_connected:
                            packet.append(
                                [robot, ctdsocket.robots_connected[robot].robot_id])
                        self.send_packet({"data": packet})
                    elif data["action"] == 11:
                        self.send_packet({"data": localizer.robots_positions})
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
        self.robots_connected = {}  # client_host: robot class object
        print("[DEBUG] Socket server ready")

    def broadcast_coordinates(self):
        while True:
            for client in list(self.robots_connected):
                try:
                    if self.robots_connected[client].robot_id != -1:
                        self.robots_connected[client].send_packet(
                            {"action": 3, "robots": localizer.get_coords()})  # action - 3 is data action
                except KeyError:
                    pass
                time.sleep(0.02)  # Too fast without timing

    def work_loop(self):
        while True:
            conn, addr = self.socket.accept()
            print("[DEBUG] New client")
            formatted_addr = f"{addr[0]}:{addr[1]}"
            self.robots_connected[formatted_addr] = ConnectedRobot(
                formatted_addr, conn)
            threading.Thread(
                target=self.robots_connected[formatted_addr].listen_loop).start()

    def send_to(self, packet, addr):
        for client in self.robots_connected:
            if client == addr:
                #print("[DEBUG] Client found")
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
    threading.Thread(target=lambda: ctdsocket.work_loop()).start()

    #webui = WebUI(__name__, localizer)
    window = tk.Tk()
    window.title("coord")
    window.geometry("1000x1000")
    window.resizable(width=False, height=False)
    canvas = tk.Canvas(window, width=1000, height=1000, bg='white')
    canvas.pack()

    pos = [[0 for j in range(30)] for i in range(20)]

    robot1_pos = (10, 10)
    robot2_pos = (100, 100)

    def click(a):
        global robot1_pos, robot2_pos
        canvas.create_rectangle(0, 0, 1000, 1000, fill='white', width=1)
        x, y = robot1_pos
        print(a)
        if a.keycode == 113 and x > 0:
            x -= 10
        if a.keycode == 114 and x < 1000:
            x += 10
        if a.keycode == 111 and y > 0:
            y -= 10
        if a.keycode == 116 and y < 1000:
            y += 10
        robot1_pos = (x, y)
        localizer.robots_positions[1] = robot1_pos
        canvas.create_rectangle(x-10, y-10, x + 10, y + 10, fill='green')
        x, y = robot2_pos
        if a.keycode == 38 and x > 0:
            x -= 10
        if a.keycode == 40 and x < 1000:
            x += 10
        if a.keycode == 25 and y > 0:
            y -= 10
        if a.keycode == 39 and y < 1000:
            y += 10
        robot2_pos = (x, y)
        localizer.robots_positions[1] = robot2_pos
        print(localizer.robots_positions)
        canvas.create_rectangle(x - 10, y - 10, x + 10, y + 10, fill='blue')

    window.bind("<KeyPress>", click)
    #window.mainloop() # Hide UI
