from flask import Flask, render_template, jsonify, request
import socket

class WebUI:
    def __init__(self, name, host, port):
        self.app = Flask(name, template_folder="webui/templates",
                         static_url_path='', static_folder='webui/static')
        self.host = host
        self.port = port
        self.app.config["TEMPLATES_AUTO_RELOAD"] = True

        @self.app.route('/')
        def __index():
            return self.index()

        @self.app.route("/joystick")
        def __joystick():
            return self.joystick()

        @self.app.route('/api/start_route')
        def __start():
            return self.start()

        @self.app.route('/api/poll_robot_status')
        def __robot_data():
            return self.robot_data()

        @self.app.route('/api/emergency_stop')
        def __stop():
            return self.stop()

        @self.app.route('/api/dev/tmgr')
        def __tmgr():
            return self.tmgr()

        @self.app.route('/api/dev/spi')
        def __spi():
            return self.spi_dev()

        @self.app.route('/api/controll')
        def __controll():
            return self.controll(request.args.get("dir"), int(request.args.get("steps")))

    def index(self):
        # return f'Execution status: {self.share_data["execution_status"]}'
        return render_template("index.html", route_path=self.share_data["current_route_data"]["route_path"], start_point=self.share_data["current_route_data"]["start_point"], strategy_id=self.share_data["current_route_data"]["strategy_id"],
                               execution_status=self.share_data["execution_status"], use_strategy_id=self.share_data["current_route_data"]["use_strategy_id"], side=self.share_data["current_route_data"]["side"],
                               robot_id=self.share_data["current_route_data"]["robot_id"], local_ip=socket.gethostbyname(socket.gethostname()), polling_interval="3000(?)",
                               web_port="8080(?)", robot_direction=self.share_data["current_route_data"]["robot_dir"])

    def start(self):
        self.share_data["execution_status"] = 1
        return jsonify({"status": True})

    def stop(self):
        self.share_data["execution_status"] = 3
        print("Stopping robot")
        return jsonify({"status": True})

    def update_share_data(self, share_data):
        self.share_data = share_data

    def robot_data(self):
        return jsonify({"status": True, "execution_status": self.share_data["execution_status"]})

    def tmgr(self):
        return jsonify({"share_data": dict(self.share_data)})

    def joystick(self):
        return render_template("joystick.html")

    def controll(self, dir_, steps):
        self.share_data["step_executing"] = True
        if dir_ == "backward":
            dir_ = "forward"
            steps *= -1
        spilib.move_robot(dir_, False, distance=steps)
        self.share_data["step_executing"] = False
        return jsonify({"status": True})

    def run(self):
        self.app.run(host=self.host, port=self.port)
