# Robot def conf
ROUTE_PATH = "side_changer.json"
ROBOT_SIZE = 50
START_POINT = (0, 0)
MM_COEF = 9.52381 # Dev robot
ROTATION_COEFF = 12.1 # Dev robot
ONE_PX = 1.95822454308094 # Const
STRATEGY_ID = 0
MASTER_PASSWORD = "1"
ROBOT_ID = 0 # Edit manualy
USE_STRATEGY_ID = False
SIDE = 0
ROBOT_DIRECTION = "E"

# WebUI conf
FLASK_HOST = "0.0.0.0" # listen from
FLASK_PORT = "8080" # Warn: port 80 require root access(insecure); to use port 80 you can use iptables port redirect
JS_POLLING_INTERVAL = 3000 # ms


# Socket conf
SOCKET_SERVER_HOST = "localhost"
SOCKET_SERVER_PORT = 7070