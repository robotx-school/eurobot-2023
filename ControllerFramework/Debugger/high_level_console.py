import socket
import json
import threading

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
    dbg_instance = DbgClient("localhost", 7070)
    dbg_instance.send_packet({"action": 0, "robot_id": -1})
    threading.Thread(target=dbg_instance.listen_loop).start()
    while True:
        raw_inp = input("$>")
        if raw_inp:
            raw_split = raw_inp.split()
            cmd = raw_split[0]
            args = raw_split[1:]
            if cmd in ["0", "1"]:
                dbg_instance.send_packet({"action": int(cmd), "to_addr": args[0]})
            elif cmd in ["10"]:
                dbg_instance.send_packet({"action": int(cmd)})
