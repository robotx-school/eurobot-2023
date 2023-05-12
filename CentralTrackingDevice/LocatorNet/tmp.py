import cv2
import numpy as np

with open('lib.cv') as f:
    K = eval(f.readline())
    D = eval(f.readline())


def undistort(img):
    DIM = img.shape[:2][::-1]
    map1, map2 = cv2.fisheye.initUndistortRectifyMap(K, D, np.eye(3), K, DIM, cv2.CV_16SC2)
    undistorted_img = cv2.remap(img, map1, map2, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
    return undistorted_img[::]

dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_250)

img = cv2.imread("center.png")
#img = undistort(img)

#print(K, D)
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
corners, ids, rejected = cv2.aruco.detectMarkers(gray, dictionary)
cv2.aruco.drawDetectedMarkers(img, corners)

if np.all(ids is not None):
    for i in range(0, len(ids)):
        marker_id = ids[i][0]
        print(marker_id)
        if marker_id in [82, 84]:
            rvec, tvec, markerPoints = cv2.aruco.estimatePoseSingleMarkers(corners[i], 55, K, D)
            x = tvec[0][0][2] - 400
            print("Dist:", tvec)
        #cv2.aruco.drawAxis(img, K, D, rvec, tvec, 0.01)
cv2.imshow("Original", img)
#cv2.imshow("Gray", gray)
cv2.waitKey(0)
