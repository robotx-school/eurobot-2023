import cv2
import numpy as np

with open('lib.cv') as f:
    K = eval(f.readline())
    D = eval(f.readline())




dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_250)

cap = cv2.VideoCapture(1)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 19200)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 10800)

while True:
    _, img = cap.read()
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    corners, ids, rejected = cv2.aruco.detectMarkers(gray, dictionary)
    cv2.aruco.drawDetectedMarkers(img, corners)
    PX_COORDS = (-1, -1)
    if np.all(ids is not None):
        for i in range(0, len(ids)):
            marker_id = ids[i][0]
            #print(marker_id)
            if marker_id in [82, 84]:
                corner = corners[i]
                centerX = (corner[0][0][0] + corner[0][1][0] + corner[0][2][0] + corner[0][3][0]) / 4
                centerY = (corner[0][0][1] + corner[0][1][1] + corner[0][2][1] + corner[0][3][1]) / 4
                center = (int(centerX), int(centerY))
                PX_COORDS = center

                #print(_centerX, _centerY)
                # print(corners[i])
                rvec, tvec, markerPoints = cv2.aruco.estimatePoseSingleMarkers(corners[i], 55, K, D)
                x = tvec[0][0][2]
                y = tvec[0][0][0]
                if y >= 0:
                    y += 1390
                    if y > 2000:
                        y = 2000
                elif y < 0:
                    y = 1390 - abs(y)
                    if y < 0:
                        y = 0
                    
                print("Dist:", x, y)

    cv2.imshow("A", img)
    pressedKey = cv2.waitKey(1) & 0xFF

    if pressedKey == ord('q'):
        break
    elif pressedKey == ord('s'):
        print(PX_COORDS)
        with open("dataset.txt", "a+") as fd:
            fd.write(f"{PX_COORDS[0]} {PX_COORDS[1]}\n")
            

cv2.waitKey(0)

