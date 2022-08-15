import cv2
import numpy as np
from math import degrees, atan2
from termcolor import colored
import json


HOTKEYS = [ord("s"), ord("c"), ord("p")]  # save file, c array; preview way in creator
START_POINT = (0, 0)
SIDE = 0  # 0 - left side; 1 - right side (blue and yellow)


def recreate_path_side(path):
    # right side converter
    converted_path = []
    for i in path:
        converted_path.append((903 - i[0], i[1]))
    return converted_path

def rotate_image(image, angle):
    image_center = tuple(np.array(image.shape[1::-1]) / 2)
    rot_mat = cv2.getRotationMatrix2D(image_center, angle, 1.0)
    result = cv2.warpAffine(image, rot_mat, image.shape[1::-1], flags=cv2.INTER_LINEAR)
    return result


def draw_circle(event, x, y, flags, param):
    global path_curr
    if event == cv2.EVENT_LBUTTONDBLCLK:
        cv2.circle(field, (x, y), 5, (255, 0, 0), -1)
        print("New point:", x, y)
        path_curr.append((x, y))
    if mode == 2:  # for interactive mode
        generate_path((x, y))


def interactive_mode_cv(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDBLCLK:
        cv2.circle(field, (x, y), 5, (255, 0, 0), -1)
        print("New point:", x, y)
        generate_path((x, y))
    elif event == cv2.EVENT_MBUTTONDOWN:
        cv2.rectangle(field, (x, y), (x + obstacle_size, y + obstacle_size), (0, 0, 0), -1)
        obstacles.append((x, y))



def save_path(path, path_name):
    with open(f'{path_name}.json', 'w') as f:
        json.dump(path, f)


def load_path(file_name):
    with open(f'{file_name}.json') as f:
        return json.load(f)


# Vector math
def vect_from_4points(x, y, x1, y1):
    return x1 - x, y1 - y


def angle_between_2vectors(ax, ay, bx, by):
    return degrees(atan2(ax * by - ay * bx, ax * bx + ay * by))


def generate_path(point):
    global curr_x, curr_y, obstacle_name, robot_vect_x, robot_vect_y, points_dest, curr_point_ind, field

    robot_vect, robot_vect_1 = vect_from_4points(curr_x, curr_y, robot_vect_x, robot_vect_y)
    point_vect, point_vect_1 = vect_from_4points(curr_x, curr_y, point[0], point[1])

    angle = angle_between_2vectors(robot_vect, robot_vect_1, point_vect, point_vect_1)
    dist = round(one_px * (((curr_x - point[0]) ** 2 + (curr_y - point[1]) ** 2) ** 0.5))
    route_analytics["dist"] += dist
    if int(angle) != 0:
        route_analytics["rotations"] += 1
    print(colored(f"Angle to rotate: {angle}", "blue"))
    print(colored(f"Distance in millimetrs: {dist}", "yellow"))
    print("---" * 10)
    cv2.arrowedLine(field, (curr_x, curr_y), (point[0], point[1]), (0, 255, 0), 2)

    curr_x, curr_y = point[0], point[1]

    robot_vect_x, robot_vect_y = point[0] + point_vect // 5, point[
        1] + point_vect_1 // 5  # Remake with line equation; Calculate new y using y = kx + b; where x = x + robot_size
    cv2.arrowedLine(field, (curr_x, curr_y), (robot_vect_x, robot_vect_y), (255, 0, 0), 5)


def save_path_frontend():
    path_name = input(colored("Name for path file>", "yellow"))
    try:
        save_path(path_curr, path_name)
        print(colored("Path saved!", "green"))
    except Exception as e:
        print(e)
        print(colored("Error during writing path", "red"))


if __name__ == "__main__":
    #field = cv2.imread("a.jpg")
    #field = cv2.imread("correct_map.jpg")
    field = cv2.imread("field.png")
    #field = cv2.resize(field, (3000, 2000))
    #field = cv2.resize(field, (1533, 1022))  # consts
    #field = rotate_image(field, 180) # View like from camera
    #field = field[::-1]3
    #cv2.imwrite("correct_map.jpg", field)
    
    
    print("Field size: ", field.shape)
    one_px = 3000 / field.shape[1]
    print("Px in mms: ", one_px)
    robot_size = 50  # Robot is not a point, it is a non zero vector
    mode = int(input("Mode (0 - create path; 1 - calculate path; 2 - interactive mode)>"))

    if mode == 1:
        name = input(colored("Name for path file>", "yellow"))
        points_dest = load_path(name)
        route_analytics = {"dist": 0, "rotations": 0}
        curr_x, curr_y = START_POINT[0], START_POINT[1]  # start
        # Fix it(image size incorrect)
        if SIDE == 1:
            robot_size = -1 * robot_size
            curr_x = 903 - curr_x
            points_dest = recreate_path_side(points_dest)
            print(points_dest)
        robot_vect_x, robot_vect_y = curr_x + robot_size, curr_y

        cv2.arrowedLine(field, (curr_x, curr_y), (robot_vect_x, robot_vect_y), (0, 0, 255), 5)
        curr_point_ind = 0
        while len(points_dest) > curr_point_ind:
            generate_path(points_dest[curr_point_ind])
            curr_point_ind += 1
        print(colored(
            f"Summary:\nDistance: {route_analytics['dist']}mm\nRotations: {route_analytics['rotations']}\nFinal coordinates: {curr_x, curr_y}",
            "green"))
        cv2.imshow("Path Gen - Calculated image way", field)
        while True:
            k = cv2.waitKey(20) & 0xFF
            if k == 27:
                exit()
                cv2.destroyAllWindows()
    elif mode == 2:
        path_curr = []
        route_analytics = {"dist": 0, "rotations": 0}
        curr_x, curr_y = START_POINT # start
        robot_vect_x, robot_vect_y = curr_x + robot_size, curr_y
        cv2.arrowedLine(field, (curr_x, curr_y), (robot_vect_x, robot_vect_y), (0, 0, 255), 5)
        cv2.namedWindow('Interactive mode')
        cv2.setMouseCallback('Interactive mode', interactive_mode_cv)
        while True:
            cv2.imshow('Interactive mode', field)
            k = cv2.waitKey(20) & 0xFF
            if k == 27:
                cv2.destroyAllWindows()
                break
            elif k == ord("g"):
                for row in range(50, 969, 51):
                    cv2.line(field, (0, row), (field.shape[1], row), (0, 0, 0), 1)
                for column in range(52, 1484, 51):
                    cv2.line(field, (column, 0), (column, field.shape[0]), (0, 0, 0), 1)
                

            elif k == ord("s"):
                save_path() # FIX IT

    else:
        print(
            f"Hotkeys:\nSave path: {colored(chr(HOTKEYS[0]), 'green')}\nConvert to cpp array: {colored(chr(HOTKEYS[1]), 'green')}")
        path_curr = []
        cv2.circle(field, START_POINT, 5, (0, 0, 255), -1)
        cv2.namedWindow('Path creator')
        cv2.setMouseCallback('Path creator', draw_circle)
        cv2.arrowedLine(field, START_POINT, (START_POINT[0] + robot_size, START_POINT[1]), (0, 0, 255), 3)
        while True:
            cv2.imshow('Path creator', field)
            k = cv2.waitKey(20) & 0xFF
            if k == 27:
                exit_confirmation = input(colored("Do you want to save changes?(y/n/c)>", "yellow"))
                if exit_confirmation == "y":
                    save_path_frontend()
                elif exit_confirmation == "c":
                    print("Canceling...")
                else:
                    print("Goodbye")
                    break
            elif k == HOTKEYS[0]:
                save_path_frontend()
            elif k == HOTKEYS[2]:
                cv2.line(field, (START_POINT[0] + robot_size, START_POINT[1]), path_curr[0], (255, 0, 0), 2)
                if len(path_curr) > 2:
                    for pnt in range(len(path_curr) - 1):
                        try:
                            cv2.line(field, path_curr[pnt], path_curr[pnt + 1], (255, 0, 0), 2)
                        finally:
                            pass
