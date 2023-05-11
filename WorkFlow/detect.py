import cv2
import numpy as np

image = cv2.imread("one.png")
mtx = np.array([[896.128972098295, 0.0, 959.6108625623755], [0.0, 901.0779296900218, 534.4228432183535], [0.0, 0.0, 1.0]])
distor = np.array([[-0.04048025498479023], [0.061095515746160366], [-0.06836476062818098], [0.024622705491456814]])
dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_250)
corners, ids, rejectedImgPoints = cv2.aruco.detectMarkers(image, dictionary)
print(corners)
image = cv2.aruco.drawDetectedMarkers(image, corners)
rvec, tvec ,_ = cv2.aruco.estimatePoseSingleMarkers(corners, 0.05, mtx, distor)
for i in range(0, ids.size):
    #rr, thet = ra.rArea(corners)
    cv2.aruco.drawFrameAxis(image, mtx, distor, rvec[0], tvec[0], 0.06) #
cv2.imshow("Ca", image)
cv2.waitKey(0)
