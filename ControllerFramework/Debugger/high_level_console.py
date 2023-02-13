import socket
import json
import threading
import time
from hl_config import *


class DbgClient:
    def __init__(self, server_host, server_port):
        self.server_host = server_host
        self.server_port = server_port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.server_host, self.server_port))

    def listen_loop(self):
        while True:
            data = self.sock.recv(2048)
            print(data)

    def send_packet(self, data):
        self.sock.send(json.dumps(data).encode("utf-8"))


if __name__ == "__main__":
    print("Dbg for high-level")
    dbg_instance = DbgClient(CTD_HOST, CTD_PORT)
    dbg_instance.send_packet({"action": 0, "robot_id": -1})
    threading.Thread(target=dbg_instance.listen_loop).start()
    while True:
        raw_inp = input("$>")
        if raw_inp:
            raw_split = raw_inp.split()
            cmd = raw_split[0]
            args = raw_split[1:]
            if cmd in ["0", "1"]:
                dbg_instance.send_packet(
                    {"action": int(cmd), "to_addr": args[0]})
            elif cmd == "3":
                # 0 - robot_id
                # 1 - new X
                # 2 - new Y
                dbg_instance.send_packet({"action": int(cmd), "robot_id": int(
                    args[0]), "new_coords": (int(args[1]), int(args[2]))})
            elif cmd == "4":
                # full command example: `4 900 0 0 356 4`
                print("[DEBUG] Fake coords changing")
                for delta_x in range(int(args[2]), int(args[2]) + int(args[0])):
                    dbg_instance.send_packet({"action": 3, "robot_id": int(
                        args[1]), "new_coords": (delta_x, int(args[3]))})
                    time.sleep(int(args[4]))
            elif cmd in ["10", "11"]:
                dbg_instance.send_packet({"action": int(cmd)})
