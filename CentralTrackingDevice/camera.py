import cv2
import numpy as np


class Camera:
    def __init__(self):
        with open('lib.cv') as f:
            self.K = eval(f.readline())
            self.D = eval(f.readline())
        self.hand = [0, 0]
        self.savescreen = False
        self.get_aruco = [141, 142, 139, 140]
        self.x_cord = [0, 0, 0, 0]
        self.y_cord = [0, 0, 0, 0]
        self.middles = [0, 0, 0, 0]
        self.is_working = True
        self.camport = 0
        self.keysym = False

        self.dictionary = cv2.aruco.getPredefinedDictionary(
            cv2.aruco.DICT_4X4_250)
        self.cap = cv2.VideoCapture(2)
        self.cap.set(3, 1920)
        self.cap.set(4, 1080)
        self.cap.set(30, 0.1)

    def undistort(self, img):
        DIM = img.shape[:2][::-1]
        map1, map2 = cv2.fisheye.initUndistortRectifyMap(
            self.K, self.D, np.eye(3), self.K, DIM, cv2.CV_16SC2)
        undistorted_img = cv2.remap(
            img, map1, map2, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
        return undistorted_img[::]

    def loop(self):
        while True:
        
            _, img = self.cap.read()
            img = self.undistort(img)
            gray_test = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            res_test = cv2.aruco.detectMarkers(gray_test, self.dictionary)
            res_img = cv2.warpPerspective(img, img.shape[0], (img.shape[1], img.shape[0]))
            gray_aruco = cv2.cvtColor(res_img, cv2.COLOR_BGR2GRAY)
            res_aruco = cv2.aruco.detectMarkers(gray_aruco, self.dictionary)
            for marker in get_aruco:
                if marker in res_aruco[1]:
                    #print(11111, marker)
                    # print(222222,res_aruco[1])
                    index = np.where(res_aruco[1] == marker)[0][0]
                    # print(333333,index)
                    pt0 = res_aruco[0][index][0][0].astype(np.int16)
                    # coords.append(list(pt0))
                    print("arUco:", marker, "("+str(index)+")", "|", "Cords on image:", "X", list(pt0)[0], "/", "Y", list(pt0)[1], "|", "Real cords:", "X", str(
                        int((list(pt0)[1])*2.7)+170), "Y", str(int((list(pt0)[0])*1.05)), "|", "Max image cords:", res_img.shape[1], "/", res_img.shape[0])
            cv2.imshow('b', cv2.rotate(cv2.rotate(cv2.resize(
                res_img, (2340//3, 3550//3)), cv2.cv2.ROTATE_180), cv2.cv2.ROTATE_90_CLOCKWISE))

            #cv2.imshow('img1',cv2.resize(img, (1080//2, 1080//2)))
            cv2.imshow('img1', img)
            # display the captured image
            if savescreen == False:
                if cv2.waitKey(1) & 0xFF == ord('y'):  # save on pressing 'y'

                    cv2.imwrite(f'c{str(i).rjust(5, "-")}.png', frame)

                    cv2.destroyAllWindows()
                    savescreen = True
                    print("Screen saved!")
                    break

        cap.release()


if __name__ == "__main__":
    cam = Camera()
    cam.loop()
