# Robot default configuration
ROUTE_PATH = "variables.json" # path to route file
ROBOT_SIZE = 50 # base size of robot in px(everything, but non zero) 
START_POINT = (0, 0) # start point of the robot
MM_COEF = 9.52381 # dev robot const data
ROTATION_COEFF = 12.1 # dev robot const coeff
ONE_PX = 1.95822454308094 # const; don't change
STRATEGY_ID = 0 # number of
MASTER_PASSWORD = "1"
ROBOT_ID = 0 # Edit manualy
USE_STRATEGY_ID = False
SIDE = 0
ROBOT_DIRECTION = "E"

# WebUI conf
FLASK_HOST = "0.0.0.0" # listen from
FLASK_PORT = "8080" # Warn: port 80 require root access(insecure); to use port 80 you can use iptables port redirect
JS_POLLING_INTERVAL = 3000 # ms

# Socket service (CTD) config
SOCKET_SERVER_HOST = "localhost"
SOCKET_SERVER_PORT = 7070
