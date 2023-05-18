from spilib_lite import *
import spilib_lite_with_lid
import time
import threading
from RXselfCoords_module_nocv import RXselfCoords as rxsc_class
import math
import numpy
from CTD_client import *
import json



DEGUG = False
DEGUG_start_pos = []

obstacles = []
pos = [335, 1790]
current_path_length = 0
rot = 0
team = False
rot_lid = 0
lid_sleep_time = 0.2
stop_status = 0
#path = [(500, 1750), (785, 1750), (785, 1300), (1200, 1300), (1200, 1850), (785, 1850), (785, 1000), (500, 1000), (500, 1100), (335, 1875)]
#path = [(550, 1000),(1000, 1000),(550, 1000),(335, 1875),(550, 1000)]
#path = [(500, 1750),(780, 1750),(780, 1250),(1300, 1250),(1300, 720),(500, 720),(335, 1875)]

path = [(335, 1200), (335, 1790)]
di = 0
robot_number = 0
v = 950.0
cur_point = tuple()

ctd = CTD_client_class()
#rxsc = rxsc_class(None, 250, 5.71, pos, 180, False)
lid = spilib_lite_with_lid.lid_getter(conAngle=[25, 148])
#rot = rxsc.get_angle()

default_servo_lists = {"grabControl_start": [ [6, 8, 7],
                            [[80, 75, 14]]],

                       "grabControl_end": [[0, 1, 2, 3],
                            [[83,27,177,108],
                             [83,20,160,128]]],

                       "dropControl_start": [[7, 8, 6],
                            [[100, 25, 145]]],

                       "dropControl_end": [[0, 1, 2, 3],
                            [[83,22,73,145]]],

                       "closeGripper": [[4, 5],
                            [[100, 90]]],

                       "openGripper": [[4, 5],
                            [[30, 150]]],
                       "init": [[4, 5, 6, 7, 8],
                           [[20, 130, 150, 10, 30]]],
                       "up": [[8], [[65]]],

                       "dropGripper": [[3, 4, 5],
                            [[152, 65, 120]]]}


print("rot:", rot)

def pos_handler():
    global DEGUG
    global rxsc
    while True:
        try:
            global current_path_length
            global pos
            global v

            if current_path_length > 0:
                while current_path_length > 0:
                    time.sleep(1/10)
                    current_path_length -= v/10
                    rxsc.go(1*(v/10))
                    pos = rxsc.get_coords()
                    if DEGUG:
                        print(pos)
                current_path_length = 0
            elif current_path_length < 0:
                while current_path_length < 0:
                    time.sleep(1/10)
                    current_path_length += v/10
                    rxsc.go(-1*(v/10))
                    pos = rxsc.get_coords()
                    print(pos)
                current_path_length = 0
        except Exception as err:
            print(err)



            #for i in range(round(abs(current_path_length) / ( 920.967 / 100))):
            #    time.sleep(1/100)
            #    if current_path_length > 0:
            #        current_path_length -= 920.967/100
            #        rxsc.go(920.967/100)
            #    elif current_path_length < 0:
            #        current_path_length += 920.967/100
            #        rxsc.go(-1*(920.967/100))
            #    pos = rxsc.get_coords()
            #    print(i, pos)
            #current_path_length = 0




def calibration_handler(end = False):
    global DEGUG_start_pos
    global DEGUG
    global pos
    global ctd
    global cur_point
    global obstacles
    if end:
        time.sleep(0.1)
        if DEGUG_start_pos != []:
            gpos = DEGUG_start_pos
            end_get = True
        else:
            try:
                gpos = ctd.get_coords()[robot_number]
                end_get = True
            except:
                print("ERROR! Don't get data from CTD!")
                end_get = False


        if gpos != [-1, -1] and end_get:
            print(f"Calib...")
            spos = [((pos[0]*3 + gpos[0])/4), ((pos[1]*3 + gpos[1])/4)]
            print(f"pos: {pos} / gpos: {gpos}  ->  spos: {spos}")
            pos = spos
        else:
            print("Calib... FAIL!")
    else:
        while True:
            time.sleep(30)
            if DEGUG_start_pos != []:
                gpos = DEGUG_start_pos
            else:
                gpos = ctd.get_coords()[robot_number]


            if gpos != [-1, -1]:
                print(f"Calib...")
                spos = [((pos[0]*3 + gpos[0])/4), ((pos[1]*3 + gpos[1])/4)]
                print(f"pos: {pos} / gpos: {gpos}  ->  spos: {spos}")
                pos = spos
            else:
                print("Calib... FAIL!")




def lid_check(angle, end_point):
    global planner
    global pos
    global rot
    global rot_lid
    global lid
    global lid_sleep_time
    global stop_status
    global obstacles
    lid.lid_angle(angle)
    time.sleep(1)
    get_data = lid.lid_get()
    cangle = abs((((lid.conAngle[0]+30) - (lid.conAngle[1]-30))/2) + min((lid.conAngle[0]+30),(lid.conAngle[1]-30)))
    oangle = angle - cangle
    dangle = oangle + rot
    fx = pos[0] + get_data[0]*10*numpy.cos(numpy.radians(dangle))
    fy = pos[1] + get_data[0]*10*numpy.sin(numpy.radians(dangle))
    bx = pos[0] + get_data[1]*10*numpy.cos(numpy.radians(dangle+180))
    by = pos[1] + get_data[1]*10*numpy.sin(numpy.radians(dangle+180))
    if fx >= 0 and fx <= 3000 and fy >= 0 and fy <= 2000:
        obstacles.append([fx, fy])
        start_point = pos
        dest_point = end_point
        path_single, points, distance_single = planner.generate_way(start_point, dest_point, obstacles)
        print("Points:", points)
    print(f"front: {fx}/{fy} | back: {bx}/{by}")

def lid_handle():
    global pos
    global rot
    global rot_lid
    global lid
    global stop_status
    for angle in range(lid.conAngle[0]+30, lid.conAngle[1]-30, 9):
        pass
    for angle in range(lid.conAngle[1]-30, lid.conAngle[0]+30, -9):
        pass




CTD_thread = threading.Thread(target=ctd.handler)
CTD_thread.start()

#calib_thread = threading.Thread(target=calibration_handler)
#calib_thread.start()

pos_thread = threading.Thread(target=pos_handler)
pos_thread.start()


def move_robot_forward(distance : int = 1000):
    global current_path_length
    move_robot("forward", None, distance = distance, accel=5710)
    current_path_length = distance

def move_robot_back(distance : int =5710):
    global current_path_length
    move_robot("back", None, distance = distance, accel=5710)
    current_path_length = -1 * distance

def rotate_robot(angle  : int = -45):
    global rot
    #против час. стрелки
    angle_temp = float(angle)
    distance = angle_temp * 10.83333333333
    distance = int(round(distance))
    move_robot("right", None, distance = distance, accel=5710)
    rxsc.rotate(angle)
    rot = rxsc.get_angle()

def move_robot_stop():
    global current_path_length
    stop_robot()
    current_path_length = 0
    print("STOP!")

def get_arduino_sync_lid_angle() -> int:
    return int(spi_send()[8])

def V2_angle_V2(a : tuple = (0, 1), b : tuple = (1, 0)) -> float:
    v = math.degrees(math.acos( (a[0]*b[0] + a[1]*b[1])/ (math.sqrt(a[0]**2 + a[1]**2) * math.sqrt(b[0]**2+ b[1]**2))))
    return v

def angle_rot_to_90():
    global rot
    rot = rxsc.get_angle()
    rot = rot % 360
    go_rot = 90+90-rot
    return int(round(go_rot))


def go_to_point_tr(point : tuple = (335, 1875), abs_size = 30):
    global rot
    global pos
    global v
    global cur_point
    rot_angle = angle_rot_to_90()
    rotate_robot(rot_angle)
    time.sleep(round((abs(rot_angle) * 11)/v)+1)
    if pos[0] <= point[0] and pos[1] <= point[1] and pos != point:
        angle_plane = 3
    elif pos[0] >= point[0] and pos[1] <= point[1 and pos != point]:
        angle_plane = 4
    elif pos[0] >= point[0] and pos[1] >= point[1] and pos != point:
        angle_plane = 1
    elif pos[0] <= point[0] and pos[1] >= point[1] and pos != point:
        angle_plane = 2
    else:
        angle_plane = 0
        print("got_to_point_tr/angle_plane:", pos, point)
    print(f"got_to_point_tr / angle_plane: {angle_plane}")


    if angle_plane == 1 or angle_plane == 2:
        rotate_robot(0)
        time.sleep(round((abs(0) * 11)/v)+1)
        cur_point = (pos[0], point[1])
        while cur_point != ():
            move_robot_forward(round((max(point[1], pos[1]) - min(point[1], pos[1]))*5.71))
            time.sleep(0.07)
            was_stopped = False
            while not current_path_length == 0:
                get_data = lid.lid_get()
                time.sleep(0.07)
                angle = get_arduino_sync_lid_angle()
                cangle = abs((((lid.conAngle[0]+30) - (lid.conAngle[1]-30))/2) + min((lid.conAngle[0]+30),(lid.conAngle[1]-30)))
                oangle = angle - cangle
                dangle = oangle + rot
                fx = pos[0] + get_data[0]*10*numpy.cos(numpy.radians(dangle))
                fy = pos[1] + get_data[0]*10*numpy.sin(numpy.radians(dangle))
                bx = pos[0] + get_data[1]*10*numpy.cos(numpy.radians(dangle+180))
                by = pos[1] + get_data[1]*10*numpy.sin(numpy.radians(dangle+180))
                if fx >= 0+100 and fx <= 3000-100 and fy >= 0+100 and fy <= 2000-100 and get_data[0] < 30:
                    print("LIDS: ", fx, fy, get_data)
                    print("STOP BY LIDS!")
                    move_robot_stop()
                    was_stopped = True
                    if (fx >= point[0]-abs_size and fx <= point[0]+abs_size) and (fy >= point[1]-abs_size and fy <= point[1]+abs_size):
                        print("OBS IN POINT!!!")
                time.sleep(0.1)
            if not was_stopped:
                cur_point = ()
            else:
                lock = 30
                while lock > 0:
                    get_data = lid.lid_get()
                    if get_data[0] >= 40:
                        lock -= 2
                    else:
                        if lock < 50-18:
                            lock += 18
                    print(f"lid lock: {lock}")
                    time.sleep(0.07)

        if angle_plane == 1:
            rotate_robot(90)
            time.sleep(round((abs(90) * 11)/v)+1)
            cur_point = (point[0], pos[1])
            while cur_point != ():
                move_robot_forward(round((max(point[0], pos[0]) - min(point[0], pos[0]))*5.71))
                time.sleep(0.07)
                was_stopped = False
                while not current_path_length == 0:
                    get_data = lid.lid_get()
                    time.sleep(0.07)
                    angle = get_arduino_sync_lid_angle()
                    cangle = abs((((lid.conAngle[0]+30) - (lid.conAngle[1]-30))/2) + min((lid.conAngle[0]+30),(lid.conAngle[1]-30)))
                    oangle = angle - cangle
                    dangle = oangle + rot
                    fx = pos[0] + get_data[0]*10*numpy.cos(numpy.radians(dangle))
                    fy = pos[1] + get_data[0]*10*numpy.sin(numpy.radians(dangle))
                    bx = pos[0] + get_data[1]*10*numpy.cos(numpy.radians(dangle+180))
                    by = pos[1] + get_data[1]*10*numpy.sin(numpy.radians(dangle+180))
                    if fx >= 0+100 and fx <= 3000-100 and fy >= 0+100 and fy <= 2000-100 and get_data[0] < 30:
                        print("LIDS: ", fx, fy, get_data)
                        print("STOP BY LIDS!")
                        move_robot_stop()
                        was_stopped = True
                        if (fx >= point[0]-abs_size and fx <= point[0]+abs_size) and (fy >= point[1]-abs_size and fy <= point[1]+abs_size):
                            print("OBS IN POINT!!!")
                    time.sleep(0.1)
                if not was_stopped:
                    cur_point = ()
                else:
                    lock = 30
                    while lock > 0:
                        get_data = lid.lid_get()
                        if get_data[0] >= 40:
                            lock -= 2
                        else:
                            if lock < 50-18:
                                lock += 18
                        print(f"lid lock: {lock}")
                        time.sleep(0.07)

        if angle_plane == 2:
            rotate_robot(-90)
            time.sleep(round((abs(-90) * 11)/v)+1)
            cur_point = (point[0], pos[1])
            while cur_point != ():
                move_robot_forward(round((max(point[0], pos[0]) - min(point[0], pos[0]))*5.71))
                time.sleep(0.07)
                was_stopped = False
                while not current_path_length == 0:
                    get_data = lid.lid_get()
                    time.sleep(0.07)
                    angle = get_arduino_sync_lid_angle()
                    cangle = abs((((lid.conAngle[0]+30) - (lid.conAngle[1]-30))/2) + min((lid.conAngle[0]+30),(lid.conAngle[1]-30)))
                    oangle = angle - cangle
                    dangle = oangle + rot
                    fx = pos[0] + get_data[0]*10*numpy.cos(numpy.radians(dangle))
                    fy = pos[1] + get_data[0]*10*numpy.sin(numpy.radians(dangle))
                    bx = pos[0] + get_data[1]*10*numpy.cos(numpy.radians(dangle+180))
                    by = pos[1] + get_data[1]*10*numpy.sin(numpy.radians(dangle+180))
                    if fx >= 0+100 and fx <= 3000-100 and fy >= 0+100 and fy <= 2000-100 and get_data[0] < 30:
                        print("LIDS: ", fx, fy, get_data)
                        print("STOP BY LIDS!")
                        move_robot_stop()
                        was_stopped = True
                        if (fx >= point[0]-abs_size and fx <= point[0]+abs_size) and (fy >= point[1]-abs_size and fy <= point[1]+abs_size):
                            print("OBS IN POINT!!!")
                    time.sleep(0.1)
                if not was_stopped:
                    cur_point = ()
                else:
                    lock = 30
                    while lock > 0:
                        get_data = lid.lid_get()
                        if get_data[0] >= 40:
                            lock -= 2
                        else:
                            if lock < 50-18:
                                lock += 18
                        print(f"lid lock: {lock}")
                        time.sleep(0.07)



    elif angle_plane == 3 or angle_plane == 4:
        rotate_robot(180)
        time.sleep(round((abs(180) * 11)/v)+1)
        cur_point = (pos[0], point[1])
        while cur_point != ():
            move_robot_forward(round((max(point[1], pos[1]) - min(point[1], pos[1]))*5.71))
            time.sleep(0.07)
            was_stopped = False
            while not current_path_length == 0:
                get_data = lid.lid_get()
                time.sleep(0.07)
                angle = get_arduino_sync_lid_angle()
                cangle = abs((((lid.conAngle[0]+30) - (lid.conAngle[1]-30))/2) + min((lid.conAngle[0]+30),(lid.conAngle[1]-30)))
                oangle = angle - cangle
                dangle = oangle + rot
                fx = pos[0] + get_data[0]*10*numpy.cos(numpy.radians(dangle))
                fy = pos[1] + get_data[0]*10*numpy.sin(numpy.radians(dangle))
                bx = pos[0] + get_data[1]*10*numpy.cos(numpy.radians(dangle+180))
                by = pos[1] + get_data[1]*10*numpy.sin(numpy.radians(dangle+180))
                if fx >= 0+100 and fx <= 3000-100 and fy >= 0+100 and fy <= 2000-100 and get_data[0] < 30:
                    print("LIDS: ", fx, fy, get_data)
                    print("STOP BY LIDS!")
                    move_robot_stop()
                    was_stopped = True
                    if (fx >= point[0]-abs_size and fx <= point[0]+abs_size) and (fy >= point[1]-abs_size and fy <= point[1]+abs_size):
                        print("OBS IN POINT!!!")
                time.sleep(0.1)
            if not was_stopped:
                cur_point = ()
            else:
                lock = 30
                while lock > 0:
                    get_data = lid.lid_get()
                    if get_data[0] >= 40:
                        lock -= 2
                    else:
                        if lock < 50-18:
                            lock += 18
                    print(f"lid lock: {lock}")
                    time.sleep(0.07)

        if angle_plane == 3:
            rotate_robot(90)
            time.sleep(round((abs(90) * 11)/v)+1)
            cur_point = (point[0], pos[1])
            while cur_point != ():
                move_robot_forward(round((max(point[0], pos[0]) - min(point[0], pos[0]))*5.71))
                time.sleep(0.07)
                was_stopped = False
                while not current_path_length == 0:
                    get_data = lid.lid_get()
                    time.sleep(0.07)
                    angle = get_arduino_sync_lid_angle()
                    cangle = abs((((lid.conAngle[0]+30) - (lid.conAngle[1]-30))/2) + min((lid.conAngle[0]+30),(lid.conAngle[1]-30)))
                    oangle = angle - cangle
                    dangle = oangle + rot
                    fx = pos[0] + get_data[0]*10*numpy.cos(numpy.radians(dangle))
                    fy = pos[1] + get_data[0]*10*numpy.sin(numpy.radians(dangle))
                    bx = pos[0] + get_data[1]*10*numpy.cos(numpy.radians(dangle+180))
                    by = pos[1] + get_data[1]*10*numpy.sin(numpy.radians(dangle+180))
                    if fx >= 0+100 and fx <= 3000-100 and fy >= 0+100 and fy <= 2000-100 and get_data[0] < 30:
                        print("LIDS: ", fx, fy, get_data)
                        print("STOP BY LIDS!")
                        move_robot_stop()
                        was_stopped = True
                        if (fx >= point[0]-abs_size and fx <= point[0]+abs_size) and (fy >= point[1]-abs_size and fy <= point[1]+abs_size):
                            print("OBS IN POINT!!!")
                    time.sleep(0.1)
                if not was_stopped:
                    cur_point = ()
                else:
                    lock = 30
                    while lock > 0:
                        get_data = lid.lid_get()
                        if get_data[0] >= 40:
                            lock -= 2
                        else:
                            if lock < 50-18:
                                lock += 18
                        print(f"lid lock: {lock}")
                        time.sleep(0.07)

        if angle_plane == 4:
            rotate_robot(-90)
            time.sleep(round((abs(-90) * 11)/v)+1)
            cur_point = (point[0], pos[1])
            while cur_point != ():
                move_robot_forward(round((max(point[0], pos[0]) - min(point[0], pos[0]))*5.71))
                time.sleep(0.07)
                was_stopped = False
                while not current_path_length == 0:
                    get_data = lid.lid_get()
                    time.sleep(0.07)
                    angle = get_arduino_sync_lid_angle()
                    cangle = abs((((lid.conAngle[0]+30) - (lid.conAngle[1]-30))/2) + min((lid.conAngle[0]+30),(lid.conAngle[1]-30)))
                    oangle = angle - cangle
                    dangle = oangle + rot
                    fx = pos[0] + get_data[0]*10*numpy.cos(numpy.radians(dangle))
                    fy = pos[1] + get_data[0]*10*numpy.sin(numpy.radians(dangle))
                    bx = pos[0] + get_data[1]*10*numpy.cos(numpy.radians(dangle+180))
                    by = pos[1] + get_data[1]*10*numpy.sin(numpy.radians(dangle+180))
                    if fx >= 0+100 and fx <= 3000-100 and fy >= 0+100 and fy <= 2000-100 and get_data[0] < 30:
                        print("LIDS: ", fx, fy, get_data)
                        print("STOP BY LIDS!")
                        move_robot_stop()
                        was_stopped = True
                        if (fx >= point[0]-abs_size and fx <= point[0]+abs_size) and (fy >= point[1]-abs_size and fy <= point[1]+abs_size):
                            print("OBS IN POINT!!!")
                    time.sleep(0.1)
                if not was_stopped:
                    cur_point = ()
                else:
                    lock = 30
                    while lock > 0:
                        get_data = lid.lid_get()
                        if get_data[0] >= 40:
                            lock -= 2
                        else:
                            if lock < 50-18:
                                lock += 18
                        print(f"lid lock: {lock}")
                        time.sleep(0.07)
    calibration_handler(True)

def gripper_servo(servo_list : list,
               pos_list : list,
               spDelay : float = 0.7):

    time.sleep(0.07)
    for servo_pos in pos_list:
        for i in range(len(servo_list)):
            move_servo(servo_list[i], 0, servo_pos[i], 10)
            #time.sleep(0.03)
        time.sleep(spDelay)


def go_to_point(point : tuple = (335, 1875), stopper = 1, sstopper = 2, abs_size = 250, zn = False):
    #не проверял
    global di
    global cur_point
    global pos
    global rot
    global v
    global cur_point
    global path
    global lid
    global obstacles
    cur_point = point
    rot = rxsc.get_angle()
    rot = rot % 360
    pos2v = (numpy.cos(numpy.radians(rot)), numpy.sin(numpy.radians(rot)))
    point2v = ((point[0] - pos[0]), (point[1] - pos[1]))
    distance = math.sqrt( abs(pos[0]-point[0])**2 + abs(pos[1]-point[1])**2 )
    delta_angle = V2_angle_V2(point2v) + 90
    rot_angle = (V2_angle_V2(pos2v) - delta_angle) * -1
    if rot_angle >= 350:
        rot_angle = 0
        print("Error! >350")
    elif rot_angle >= 182 and rot_angle <= 225:
        rot_angle -= 180
        print("Error >182 <225 (265)!")
    if round(rot_angle/10)*10 > 90 and round(rot_angle/10)*10 < 135:
        print("Cor:", rot_angle)
        rot_angle = 90 - (rot_angle-90)
    elif round(rot_angle/10)*10 >= 135 and round(rot_angle/10)*10 < 180:
        print("Cor:", rot_angle)
        rot_angle = rot_angle + 90.0/4
    elif round(rot_angle/10)*10 < -90 and round(rot_angle/10)*10 > -135:
        print("Idk 1")
    elif round(rot_angle/10)*10 <= -135 and round(rot_angle/10)*10 > -180:
        print("Idk 2")
    print(delta_angle, rot_angle)
    if ((rot > 174 and rot < 186) or (rot > -6 and rot < 6)) and rot != 180 and delta_angle != 180:
        rot_angle  = delta_angle
        print("Error 180/!180")
    print(f"dst: {distance} | a: {rot_angle} / da: {delta_angle} | rot: {rot}")
    cur_point = point
    if not zn:
        rotate_robot(round(rot_angle))
    time.sleep(round((abs(rot_angle) * 11)/v)+1)
    move_robot_forward(round(distance*5.71))
    time.sleep(0.1)
    was_stopped = False
    while not current_path_length == 0:
        get_data = lid.lid_get()
        time.sleep(0.07)
        angle = get_arduino_sync_lid_angle()
        cangle = abs((((lid.conAngle[0]+30) - (lid.conAngle[1]-30))/2) + min((lid.conAngle[0]+30),(lid.conAngle[1]-30)))
        oangle = angle - cangle
        dangle = oangle + rot
        fx = pos[0] + get_data[0]*10*numpy.cos(numpy.radians(dangle))
        fy = pos[1] + get_data[0]*10*numpy.sin(numpy.radians(dangle))
        bx = pos[0] + get_data[1]*10*numpy.cos(numpy.radians(dangle+180))
        by = pos[1] + get_data[1]*10*numpy.sin(numpy.radians(dangle+180))
        if fx >= 0+350 and fx <= 3000-350 and fy >= 0+350 and fy <= 2000-350 and get_data[0] < 30:
            print(fx, fy, get_data)
            print("STOP BY LIDS!")
            move_robot_stop()
            was_stopped = True
            if (fx >= point[0]-abs_size and fx <= point[0]+abs_size) and (fy >= point[1]-abs_size and fy <= point[1]+abs_size):
                print("OBS IN POINT!!!")
                stopper = sstopper
        time.sleep(0.1)
    if not was_stopped:
        cur_point = ()
    else:
        if stopper == 0:
           cur_point = ()
        elif stopper == 1:
            move_robot_back(round(200*5.71))
            while not current_path_length == 0:
                get_data = lid.lid_get()
                time.sleep(0.07)
                angle = get_arduino_sync_lid_angle()
                if bx >= 0+50 and bx <= 3000-50 and by >= 0+50 and by <= 2000-50 and get_data[1] < 30:
                    print("STOP BY BACK LIDS!")
                    move_robot_stop()
                time.sleep(0.1)
            rotate_robot(-90)
            time.sleep(round((abs(-90) * 11)/v)+1)
            move_robot_back(round(350*5.71))
            while not current_path_length == 0:
                get_data = lid.lid_get()
                time.sleep(0.07)
                angle = get_arduino_sync_lid_angle()
                if bx >= 0+50 and bx <= 3000-50 and by >= 0+50 and by <= 2000-50 and get_data[1] < 30:
                    print("STOP BY BACK LIDS!")
                    move_robot_stop()
                time.sleep(0.1)
            rotate_robot(90)
            time.sleep(round((abs(90) * 11)/v)+1)
        elif stopper == 2:
            lock = 30
            while lock > 0:
                get_data = lid.lid_get()
                if get_data[0] >= 40:
                    lock -= 2
                else:
                    if lock < 50-18:
                        lock += 18
                print(f"lid lock: {lock}")
                time.sleep(0.07)



    #time.sleep(round((distance*5.71)/v)+2)


#go_to_point((550, 1000))
#time.sleep(3)
#go_to_point((1000, 1000))
#time.sleep(3)
#go_to_point((550, 1000))
#time.sleep(3)
#go_to_point((335, 1875))
#time.sleep(3)
#go_to_point((550, 1000))

#move_robot_forward(4000)
#time.sleep(0.5)
#move_robot_stop()

def wait_for_stop():
    #data = spi_send([])
    while True:
        recieved = spi_send([])
        if (recieved[0] == 0 and recieved[1] == 0):
            break

if __name__ == "__main__":

    led_clear()
    #move_robot_forward(100)
    #exit(1)

    gripper_servo(default_servo_lists["init"][0], default_servo_lists["init"][1])
    #gripper_servo(default_servo_lists["grabControl_start"][0], default_servo_lists["grabControl_start"][1])
    gripper_servo(default_servo_lists["closeGripper"][0], default_servo_lists["closeGripper"][1])
    #gripper_servo(default_servo_lists["up"][0], default_servo_lists["up"][1])
    gripper_servo(default_servo_lists["dropControl_start"][0], default_servo_lists["dropControl_start"][1])
    #move_robot_forward(100)
    #exit(1)


    with open('path.part.txt') as file:
        path_from_file = json.loads(str(file.read()))


    time.sleep(3)
    team = bool(int(input(">")))
    while True:
        time.sleep(0.3)
        #team = bool(low_digitalRead_echo(24))
        #team = bool(input("Сторона 1 - сторона синий; 0 - зелененый"))
        print(team)
        if team:
            led_fill(0, 92, 230, True)
        else:
            led_fill(0, 230, 92, True)
        time.sleep(0.3)
        if bool(low_digitalRead_echo(25)):
            print("Start!")
            break

    if team:
        path = path_from_file["blue"]["path"]
        pos = [335, 1790]
        rxsc = rxsc_class(None, 250, 5.71, pos, 180, False)
        rot = rxsc.get_angle()
    else:
        path = path_from_file["green"]["path"]
        pos = [335, 210]
        rxsc = rxsc_class(None, 250, 5.71, pos, 360, False)
        rot = rxsc.get_angle()

    #move_robot_forward(100)
    #exit()
    for i in path:
        print(f"go to: {i} (tr)")

        if isinstance(i, tuple) or (isinstance(i, list) and isinstance(i[0], int)):
            if len(i) == 2:
                go_to_point(i)
            elif len(i) == 3:
                if i[2] == "tr":
                    go_to_point_tr((i[0], i[1]))
                else:
                    print('WARN in path: tuple -> len == 3 -> i[2] NOT "tr"')
            else:
                print('WARN in path: tuple -> len NOT == 2 or 3 ')
        elif isinstance(i, list):
            if i[0] == "to90":
                if len(i) == 1:
                    rot_angle = angle_rot_to_90()
                    rotate_robot(rot_angle)
                    #time.sleep(round((abs(rot_angle) * 11)/v)+1)
                    wait_for_stop()
                    time.sleep(0.5)

                else:
                    print('WARN in path: list -> to90 -> len NOT == 1')
            elif i[0] == "back":
                if len(i) == 2:
                    move_robot_back(i[1])
                    wait_for_stop()
                    time.sleep(1.5)
                    #time.sleep(round((i[1]*3)/v))
                else:
                    print('WARN in path: list -> back -> len NOT == 2')
            elif i[0] == "forward":
                print("Forward")
                if len(i) == 2:
                    move_robot_forward(i[1])
                    wait_for_stop()
                    time.sleep(1.5)
                    #time.sleep(round((i[1] * 3)/v))
                else:
                    print('WARN in path: list -> forward -> len NOT == 2')
            elif i[0] == "rotate":
                print("Rotate")
                if len(i) == 2:
                    rotate_robot(i[1])
                    wait_for_stop()
                    time.sleep(0.5)
                    #time.sleep(round((i[1]*6)/v))
                else:
                    print('WARN in path: list -> rotate -> len NOT == 2')
            elif i[0] == "servo":
                if len(i) == 3:
                    gripper_servo(i[1], i[2])
                    time.sleep(0.5)
                else:
                    print('WARN in path: list -> rotate -> len NOT == 3')
            elif i[0] == "delay":
                if len(i) == 2:
                    time.sleep(i[1] / 1000)
                else:
                    print('WARN in path: list -> delay -> len NOT == 2')
            elif i[0] == "open_gripper":
                gripper_servo(default_servo_lists["openGripper"][0], default_servo_lists["openGripper"][1])
            elif i[0] == "close_gripper":
                gripper_servo(default_servo_lists["closeGripper"][0], default_servo_lists["closeGripper"][1])
            elif i[0] == "gripper_init":
                gripper_servo(default_servo_lists["init"][0], default_servo_lists["init"][1])
            elif i[0] == "gripper_grab_start":
                gripper_servo(default_servo_lists["grabControl_start"][0], default_servo_lists["grabControl_start"][1])
            elif i[0] == "update_prediction":
                spi_send([10, i[1]])

        else:
            print('WARN in path: NOT type')
        #time.sleep(0.5)
        if not bool(low_digitalRead_echo(25)):
            print("Stop!")
            break
        time.sleep(0.07)


        #rot_angle = angle_rot_to_90() + 90
        #rotate_robot(rot_angle)
        #time.sleep(round((abs(rot_angle) * 11)/v)+1)

    if team:
        led_fill(0, 92, 230)
    else:
        led_fill(0, 230, 92)
