import socket

class DbgClient:
    def __init__(self, server_host, server_port):
        self.server_host = server_host
        self.server_port = server_port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.server_host, self.server_port))

    def listen_loop(self):
        while True:
            pass

    def send_packet(self): 
        pass

if __name__ == "__main__":
    print("Dbg for high-level")
    dbg_instance = DbgClient("localhost", 7070)
    while True:
        raw_inp = input("$>")
        raw_split = raw_inp.split()
        cmd = raw_split[0]
        args = raw_split[1:]
        