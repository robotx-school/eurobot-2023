import cv2

cap = cv2.VideoCapture(0)



width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
print(width, height)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 19200)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 10800)

r, frame = cap.read()
print(frame)
cv2.imwrite("a.png", frame)

