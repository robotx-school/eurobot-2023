import numpy as np
from flask import Flask, jsonify
from threading import Thread
import cv2
import os
import time
import datetime


class Detector:
    def is_available(self):
        read_ok, image = self.capture.read()
        return read_ok

    def get_image(self):
        img = cv2.imread('1.jpg')
        return img

    def get_quantity(self):
        image23 = cv2.imread('13.jpg')
        cv2.imwrite("23.jpg",image23)
        if True:
            img_bin, image23 = balls(image23)
            cv2.imwrite("223.jpg",img_bin)
            img_bin1, image1 = pre_clear(img_bin, image23)
            sas, _, pre_count = find_coun(img_bin1, image1)
            cv2.imwrite("bobishka.jpg",sas)
            cv2.imwrite("bobishka2.jpg",img_bin)
            #print(pre_count)
            if pre_count>0:
                img_bin, image23 = clear(img_bin, image23)
                img_bin, image23, count = find_coun(img_bin, image23)
                return count
            else:
                return 0

    def close_camera(self):
        self.capture.release()

def pre_clear(img_bin, image):
    kernel = np.ones((5, 5), 'uint8')

    img_bin = cv2.erode(img_bin, kernel, iterations=4)
    img_bin = cv2.dilate(img_bin, kernel, iterations=10)
    return img_bin, image

def clear(img_bin, image):
    cv2.imwrite(f"b.jpg", img_bin)
    kernel = np.ones((5, 5), 'uint8')
    img_bin = cv2.erode(img_bin, kernel, iterations=3)
    img_bin = cv2.dilate(img_bin, kernel, iterations=12)
    cv2.imwrite(f"m.jpg", img_bin)
    #img_bin = cv2.dilate(img_bin, kernel, iterations=1)
    img_bin = cv2.erode(img_bin, kernel, iterations=1)
    cv2.imwrite(f"a.jpg", img_bin)
    return img_bin, image

def find_coun(img_bin, image):
    img_bin,image = img_bin,image
    coords = []
    contours, hierarchy = cv2.findContours(img_bin,cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(image, contours, -1, (255, 0, 0), 3, cv2.LINE_AA, hierarchy, 1)
    return img_bin, image, len(contours)

def balls(img,save:bool = True):
    #print(img)
    h,w,_ = img.shape
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV )

    h1 = 173
    s1 = 55
    v1 = 98
    h2 = 180
    s2 = 255
    v2 = 255

    h_min = np.array((h1, s1, v1), np.uint8)
    h_max = np.array((h2, s2, v2), np.uint8)
    img_bin = cv2.inRange(hsv, h_min, h_max)

    return img_bin, img

"""def list_int_to_bytes(input_list):
    # Split list int values to list ready for transfer by SPI
    # every value from -32768 to 32767
    # will be replaced two values from -255 to 255
    # Original values must be collected by Arduino after transfer
    output_list = []
    for int_data in input_list:
        output_list.append(int_data >> 8)
        output_list.append(int_data & 255)
    return output_list


def spi_send(txData):
    # Send and recieve 40 bytes
    N = 40
    spi = spidev.SpiDev()
    spi.open(1, 0)
    spi.max_speed_hz = 1000000
    txData = list_int_to_bytes(txData)
    txData = txData+[0]*(N-len(txData))
    rxData = []
    _ = spi.xfer2([240])  # 240 - b11110000 - start byte
    for i in range(40):
        rxData.append(spi.xfer2([txData[i]])[0])
    spi.close()
    return rxData

"""

class WebServer:
    def __init__(self, name, host='0.0.0.0', port=8000) -> None:
        self.app = Flask(name)
        self.count_chery = 0
        self.port = port
        self.host = host

        @self.app.route('/')
        def index():
            try:
                return jsonify({'ok': True, 'status': "SUCCES", 'result': self.count_chery})
            except Exception as e:
                return jsonify({'ok': False, 'status': 'error', 'result': str(e)})
        
    def update(self, count_chery):
        self.count_chery = count_chery
    
    def run(self):
        self.app.run(host=self.host, port=self.port)
            



if __name__ == "__main__":
    server = WebServer(__name__)
    Thread(target=server.run).start()

    while 1:
        n = int(input())
        server.update(n)


    # detector = Detector()
    # nonsave_timer = time.time()

    


    # save_timer = time.time()
    # while True:
    #     #img = detector.get_image()
    #     cherry = detector.get_quantity()
    #     print(cherry)
    #     #spi_send([cherry])
    #     time.sleep(1)
