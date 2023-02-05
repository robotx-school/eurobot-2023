### Robot configuration file ###

class Config:
    ROUTE_PATH = "./strategies/dev/mms.json" # path to route file
    ROBOT_SIZE = 50 # base size of robot in px (everything, but non zero). This only used to calculate robot vector direction. And visualization in PathMaker
    START_POINT = (0, 1000) # start point of the robot. it can be overwritten by route config (step with -1 action)
    MM_COEF = 9.52381 # Steps to go one millimeter
    ROTATION_COEFF = 12.1 # Steps to rotate to one degree
    ONE_PX = 1.95822454308094 # OLD, not used. Convert map image px to real millimeters
    STRATEGY_ID = 0 # id of strategy, if load from ./strategies directory
    MASTER_PASSWORD = "1" # to protect webui endpoints, that can change config
    ROBOT_ID = 0 # Id of current robot. 0 or 1
    USE_STRATEGY_ID = False # Load strategy by robot id
    SIDE = 0 # Not used in current rules. 
    ROBOT_DIRECTION = "E" # 90 degree axes binded to real world navigation. E - East, W - West, N - North, S - South
    '''
    Left top corner of the field

       ^ N
    W < > E
     S v 
    '''

    # WebUI config
    FLASK_HOST = "0.0.0.0" # listen from
    FLASK_PORT = "8080" # Warn: port 80 require root access(insecure); to use port 80 you can use iptables port redirect
    JS_POLLING_INTERVAL = 3000 # milliseconds, webui realtime info fetch interval

    # Socket service (CTD) config
    SOCKET_SERVER_HOST = "localhost" # ip of ctd socket server
    SOCKET_SERVER_PORT = 7070 # port of tcp socket

    # Logging config
    LOGS_DIRECTORY = "./Logs" # directory to save logs

    # Local robot camera config
    CAMERA_SUPPORTED = True # Does the robot have a separate camera
    CAMERA_ID = 0 # Id of this camera

    # Debug console
    DBG_CONSOLE_ENABLED = True