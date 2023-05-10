### Robot configuration file ###

class Config:
    ROUTE_PATH = "variables_1.json"  # path to route file
    # base size of robot in px (everything, but non zero). This only used to calculate robot vector direction. And visualization in PathMaker
    ROBOT_SIZE = 50
    # start point of the robot. it can be overwritten by route config (step with -1 action)
    START_POINT = (3000, 900)
    MM_COEF = 5.602241176470588#9.52381  # Steps to go one millimeter
    ROTATION_COEFF = 11.1  # Steps to rotate to one degree
    ONE_PX = 1.95822454308094  # OLD, not used. Convert map image px to real millimeters
    STRATEGY_ID = 0  # id of strategy, if load from ./strategies directory
    MASTER_PASSWORD = "1"  # to protect webui endpoints, that can change config
    ROBOT_ID = 0  # Id of current robot. 0 or 1
    USE_STRATEGY_ID = False  # Load strategy by robot id
    SIDE = 0  # Not used in current rules.
    # 90 degree axes binded to real world navigation. E - East, W - West, N - North, S - South
    ROBOT_DIRECTION = "E"
    '''
    Left top corner of the field.
       ^ N
    W < > E
     S v
   
    About global coordinate system:
            3 meters
            ---------
    2 meters|(0,0)  |
            |  (3,2)|
            ---------
    '''

    # WebUI config
    FLASK_HOST = "0.0.0.0"  # listen from
    # Warn: port 80 require root access(insecure); to use port 80 you can use iptables port redirect
    FLASK_PORT = "8080"
    JS_POLLING_INTERVAL = 3000  # milliseconds, webui realtime info fetch interval

    # Socket service (CTD) config
    SOCKET_SERVER_HOST = "192.168.0.14" # ip of ctd socket server
    SOCKET_SERVER_PORT = 7070 # port of tcp socket

    #SOCKET_SERVER_HOST = "localhost"  # ip of ctd socket server
    #SOCKET_SERVER_PORT = 7070  # port of tcp socket

    # Logging config
    LOGS_DIRECTORY = "./Logs"  # directory to save logs

    # Local robot camera config
    CAMERA_SUPPORTED = True  # Does the robot have a separate camera
    CAMERA_ID = 0  # Id of this camera

    # Debug console for cli
    DBG_CONSOLE_ENABLED = True
