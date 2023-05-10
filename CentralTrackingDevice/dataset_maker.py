import cv2, numpy

class MakeScreenshots:
    def __init__(self, localizer, save_dir="./dataset/ok", cords=[((412, 376), (466, 474)), ((828, 133), (856, 183)), ((1188, 383), (1247, 487))]):
        self.localizer = localizer
        self.cords = cords
        self.save_index = 0
        self.save_dir = save_dir

    def get(self):
        res = {}
        for n, cord in enumerate(self.cords):
            _, frame = self.localizer.camera.read()
            box_img = frame[cord[0][1]:cord[1][1], cord[0][0]:cord[1][0]]
            cv2.imwrite(f"{self.save_dir}/{self.save_index}.png")
            self.save_index += 1

class Camera:
    def __init__(self):
        self.camera = cv2.VideoCapture(0)

cam = Camera()
screenshoter = MakeScreenshots(cam)
