import cv2
import numpy as np


img = cv2.imread("img.png")
# (760, 130) (864, 158)
# (396, 364) (472, 488)
# img_2 = img[382:494, 1176:1254]
img_2 = img[364:488, 396:472]

hsv = cv2.cvtColor(img_2, cv2.COLOR_BGR2HSV )
h1, s1, v1, h2, s2, v2 = 16, 0, 0, 255, 255, 255

h_min = np.array((h1, s1, v1), np.uint8)
h_max = np.array((h2, s2, v2), np.uint8)
thresh = cv2.inRange(hsv, h_min, h_max)

kernel = np.ones((1, 1), 'uint8')
thresh = cv2.erode(thresh, kernel, iterations=5)
thresh = cv2.dilate(thresh, kernel, iterations=5)

contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

res = False
for contour in contours:
    area = cv2.contourArea(contour)
    # print(area)
    if area > 5000:
        res = True
        break
        # print("YES")
        # exit()
        
cv2.imshow('image', thresh)
cv2.waitKey(0)

