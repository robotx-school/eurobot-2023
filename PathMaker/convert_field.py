import cv2
import numpy as np

field = cv2.imread("map.jpg")
field = cv2.resize(field, (1530, 1020))
cv2.imwrite("a.jpg", field)