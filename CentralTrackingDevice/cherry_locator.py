import cv2
import numpy as np


cap = cv2.VideoCapture(0)


cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

ret, frame = cap.read()


# (766, 115) (864, 166)
# (396, 364) (472, 488)
# img_2 = img[382:494, 1176:1254]
# img_2 = img[364:488, 396:472]
cords = [((412, 376), (466, 474)), 
        ((828, 133), (856, 183)), 
        ((1188, 383), (1247, 487))]



cord = cords[1]
box_img = frame[cord[0][1]:cord[1][1], cord[0][0]:cord[1][0]]


# hsv = cv2.cvtColor(img_2, cv2.COLOR_BGR2HSV )
# h1, s1, v1, h2, s2, v2 = 16, 0, 0, 255, 255, 255

# h_min = np.array((h1, s1, v1), np.uint8)
# h_max = np.array((h2, s2, v2), np.uint8)
# thresh = cv2.inRange(hsv, h_min, h_max)

# kernel = np.ones((1, 1), 'uint8')
# thresh = cv2.erode(thresh, kernel, iterations=5)
# thresh = cv2.dilate(thresh, kernel, iterations=5)

# contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

# res = False
# for contour in contours:
#     area = cv2.contourArea(contour)
#     # print(area)
#     if area > 5000:
#         res = True
#         break
#         # print("YES")
#         # exit()
        
cv2.imshow('image', box_img)
cv2.waitKey(0)

