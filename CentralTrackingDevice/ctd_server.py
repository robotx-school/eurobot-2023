import socket
import threading
import json
import time
from flask import Flask, render_template, jsonify, request
# import tkinter as tk
import time
import cv2
import numpy as np

class WebUI:
    def __init__(self, name, localizer, host='0.0.0.0', port='9090'):
        self.app = Flask(name)
        self.host = host
        self.port = port
        self.app.config["TEMPLATES_AUTO_RELOAD"] = True
        self.localizer = localizer

        @self.app.route('/')
        def __index():
            return self.index()

        @self.app.route('/api/off')
        def __off():
            return self.off()

        @self.app.route('/api/update_coords', methods=['POST'])
        def update_coords():
            for robot_id in range(0, 4):
                self.localizer.robots_positions[robot_id] = eval(
                    request.form.get(f'coords{robot_id}'))
            return jsonify({"status": True})

    def index(self):
        # print(self.localizer.robots_positions)
        return render_template('index.html', coords=self.localizer.robots_positions)

    def off(self):
        # Release camera, save recording and prepare to power off
        localizer.exit()
        return {"details": "Goodbye"}

    def run(self):
        self.app.run(host=self.host, port=self.port)


class Localization:
    '''
    Placeholder for localization module
    '''

    def __init__(self, camera_id: int = 0, use_camera: bool = True, save_recordings: bool = True, show_frame: bool = False):
        # API emulation
        # Robots coordinates on field will be legacy
        self.robots_positions = [(-1, -1), (-1, -1), (-1, -1), (-1, -1)]
        self.camera_id = camera_id
        self.use_camera = use_camera
        if self.use_camera:
            self.camera = cv2.VideoCapture(self.camera_id)
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
            self.save_recordings = save_recordings
            self.show_frame = show_frame
            self.recording_name = f"./Recordings/{int(time.time())}.avi"
            if self.save_recordings:
                fourcc = cv2.VideoWriter_fourcc('X', 'V', 'I', 'D')
                self.videoWriter = cv2.VideoWriter(
                    self.recording_name, fourcc, 24.0, (1920, 1080))

    def loop(self):
        while True:
            if self.use_camera:
                ret, frame = self.camera.read()
                if self.save_recordings:
                    self.videoWriter.write(frame)
            #if self.show_frame:
            #    cv2.imshow("Frame from cam", frame)

            # process
            # self.robots_positions = [...]

    def exit(self):
        self.camera.release()
        if self.save_recordings:
            self.videoWriter.release()


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
                    # print("[DEBUG] From debugger")
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
                            {"action": 3, "robots": localizer.robots_positions})  # action - 3 is data action
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
                # print("[DEBUG] Client found")
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
    localizer = Localization(use_camera=False)
    webui = WebUI(__name__, localizer)
    threading.Thread(target=lambda: webui.run()).start()
    #localizer = Localization(save_recordings=False, show_frame=True)
    threading.Thread(target=lambda: localizer.loop()).start()
    threading.Thread(target=lambda: ctdsocket.broadcast_coordinates()).start()
    threading.Thread(target=lambda: ctdsocket.work_loop()).start()
    localizer.robots_positions = [[885, 30], [-1, -1], [890, 1339], [-1, -1]]

    #[[885, 30], [890, 1339]]

    '''
    hand = [0, 0]
    savescreen = False
    get_aruco = [[(0, 0, 255), [141, 142, 139, 140], [0, 0], 0], [
        (255, 0, 0), [134, 146, 143, 144], [0, 0], 0]]
    path = "plane.png"
    plane_path = cv2.imread(path, cv2.IMREAD_COLOR)
    plane_path_raws, plane_path_cols, plane_path_ch = plane_path.shape


    def get_cords():
        return ([[get_aruco[0][2][0], get_aruco[0][2][1]], [get_aruco[1][2][0], get_aruco[1][2][1]]])


    def plane_show(get=True):
        plane_path_copy = plane_path.copy()
        plane_path_copy = cv2.resize(plane_path_copy, (3000, 2000))
        get_aruco_func = []
        for k in range(len(get_aruco)):
            get_aruco_func.append(
                [get_aruco[k][2][0], get_aruco[k][2][1], get_aruco[k][0]])
        for i in get_aruco_func:
            if get == True:
                cv2.circle(plane_path_copy, (i[0], i[1]), 0, i[2], 150)
        plane_path_copy = cv2.resize(plane_path_copy, (450, 300))
        cv2.imshow('plane', plane_path_copy)
        cv2.waitKey(1)


    def aruco_search(get_data_aruco_list):
        for marker in get_aruco[get_data_aruco_list][1]:
            if marker in res_aruco[1]:
                index = np.where(res_aruco[1] == marker)[0][0]
                pt0 = res_aruco[0][index][0][0].astype(np.int16)
                int(str(int((list(pt0)[1])*2.7)+170))
                get_aruco[get_data_aruco_list][2][1] = 2000 - \
                    int(str(int((list(pt0)[0])*1.05)))
                get_aruco[get_data_aruco_list][2][0] = int((list(pt0)[1])*2.7)+170
                get_aruco[get_data_aruco_list][3] = 0
            else:
                get_aruco[get_data_aruco_list][3] += 1
                if get_aruco[get_data_aruco_list][3] > 10:
                    get_aruco[get_data_aruco_list][2][0] = -1
                    get_aruco[get_data_aruco_list][2][1] = -1


    with open('lib.cv') as f:
        K = eval(f.readline())
        D = eval(f.readline())


    def undistort(img):
        DIM = img.shape[:2][::-1]
        map1, map2 = cv2.fisheye.initUndistortRectifyMap(
            K, D, np.eye(3), K, DIM, cv2.CV_16SC2)
        undistorted_img = cv2.remap(
            img, map1, map2, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
        return undistorted_img[::]


    x_cord = [0, 0, 0, 0]
    y_cord = [0, 0, 0, 0]
    middles = [0, 0, 0, 0]

    is_working = True
    camport = 3
    q = False

    dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_250)

    while True:
        while is_working:
            cap = cv2.VideoCapture(camport)

            cap.set(3, 1920)
            cap.set(4, 1080)
            cap.set(30, 0.1)
            if not cap.isOpened():
                print("USB port - not found")
            else:
                is_working = False
        _,img = cap.read()
        #img = cv2.imread("test.png")
        img = undistort(img)
        # print(img.shape)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        res = cv2.aruco.detectMarkers(gray, dictionary)
        height, width, _ = img.shape
        # cv2.circle(img, (200,32), 5, (50,100,200), -1)
        # cv2.circle(img, (420,32), 5, (50,100,200), -1)
        # cv2.circle(img, (18,415), 5, (50,100,200), -1)
        # cv2.circle(img, (590,390), 5, (50,100,200), -1)
        if res[1] is not None:

            kubs = [20, 21, 23, 22]
            if kubs[0] in res[1] and kubs[1] in res[1] and kubs[2] in res[1] and kubs[3] in res[1]:

                for a in range(4):
                    index = np.where(res[1] == kubs[a])[0][0]

                    x_middle = 0
                    y_middle = 0
                    coords = []

                    for i in range(4):
                        coords.append([int(res[0][index][0][i][0]),
                                    int(res[0][index][0][i][1])])
                        x_cord[i] = int(res[0][index][0][i][0])
                        y_cord[i] = int(res[0][index][0][i][1])
                        # cv2.circle(img, (x_cord[i],y_cord[i]), 5, (0,0,255), -1)
                        if a == i:
                            middles[a] = [x_cord[i], y_cord[i]]

                # print(middles)

                middles[0][0] = middles[0][0] + 360 + \
                    170 + 150 + 35 - 10 - 100  # bottom left
                middles[0][1] = middles[0][1] + 310 + 50 + 100 - 245 - 200
                # print("bottom left:", middles[0][0], middles[0][1])

                middles[1][0] = middles[1][0] - 290 - 100 - 150 - 25  # uper left
                middles[1][1] = middles[1][1] + 270 + 88 - 50 - 205

                # print("uper left:", middles[1][0], middles[1][1])

                middles[2][0] = middles[2][0] - 70 + \
                    35-40-35 - 30 + 15  # upper right
                middles[2][1] = middles[2][1] - 100 - 147+7
                # print("upper right:", middles[2][0], middles[2][1])

                middles[3][0] = middles[3][0] + 80 + 5 + 40 + 23  # bottom right
                middles[3][1] = middles[3][1] - 100 - 135 - 20  # + 15
                # print("bottom right:", middles[3][0], middles[3][1])

                input_pt = np.array(middles)
                output_pt = np.array(
                    [[0, 0], [width, 0], [width, height], [0, height]])
                h, _ = cv2.findHomography(input_pt, output_pt)
                res_img = cv2.warpPerspective(img, h, (width, height))

                # gray_aruco = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                # Edit 01.11.2022/17.29
                gray_aruco = cv2.cvtColor(res_img, cv2.COLOR_BGR2GRAY)

                res_aruco = cv2.aruco.detectMarkers(gray_aruco, dictionary)
                for j in range(len(get_aruco)):
                    aruco_search(j)
                plane_show()
                # print(res_aruco[0])
                COORDS = get_cords()
                print(COORDS)
                localizer.robots_positions[0] = COORDS[0]
                localizer.robots_positions[2] = COORDS[1] 
                cv2.imshow('b', cv2.rotate(cv2.rotate(cv2.resize(
                    res_img, (2340//3, 3550//3)), cv2.ROTATE_180), cv2.ROTATE_90_CLOCKWISE))

        # cv2.imshow('img1',cv2.resize(img, (1080//2, 1080//2)))
        cv2.imshow('img1', img)
        # display the captured image
        if savescreen == False:
            if cv2.waitKey(1) & 0xFF == ord('y'):  # save on pressing 'y'

                q = True
                cv2.destroyAllWindows()
                print("Screen saved!")
                break

    while (q):
        while is_working:
            cap = cv2.VideoCapture(camport)

            cap.set(3, 1920)
            cap.set(4, 1080)
            cap.set(30, 0.1)

        # n
            if not cap.isOpened():
                print("USB port - not found")
            else:
                is_working = False
        _, img = cap.read()
        img = undistort(img)
        gray_test = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        res_test = cv2.aruco.detectMarkers(gray_test, dictionary)
        res_img = cv2.warpPerspective(img, h, (width, height))
        gray_aruco = cv2.cvtColor(res_img, cv2.COLOR_BGR2GRAY)
        res_aruco = cv2.aruco.detectMarkers(gray_aruco, dictionary)
        for j in range(len(get_aruco)):
            aruco_search(j)
        plane_show()
        cv2.imshow('b', cv2.rotate(cv2.rotate(cv2.resize(
            res_img, (2340//3, 3550//3)), cv2.ROTATE_180), cv2.ROTATE_90_CLOCKWISE))
        # cv2.imshow('img1',cv2.resize(img, (1080//2, 1080//2)))
        cv2.imshow('img1', img)
        # display the captured image
        if savescreen == False:
            if cv2.waitKey(1) & 0xFF == ord('y'):  # save on pressing 'y'
                cv2.imwrite(f'c{str(i).rjust(5, "-")}.png', frame)
                cv2.destroyAllWindows()
                savescreen = True
                print("Screen saved!")
                break

    cap.release()

    webui = WebUI(__name__, localizer)
    webui.run()
    '''
