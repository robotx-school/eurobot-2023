import numpy as np

from flask import Flask, jsonify, render_template, request
from threading import Thread
import cv2
import os
import time
import datetime
import spidev

FIXED = None # inital value is to use default pred

'''
import telebot

TOKEN = "6253877500:AAEFB2bIi1yNBDnwYcPmeKRX9rqJxmoxLDU"
FIXED = None

bot = telebot.TeleBot(TOKEN)
@bot.message_handler(commands = ['start'])
def start(message):
    bot.send_message(message.from_user.id, "AA")

@bot.message_handler(commands = ['fix'])
def fix(message):
    FIXED = -1
    bot.send_message(message.from_user.id, "Fix")
Thread(target=lambda: bot.polling(none_stop=True, interval=0)).start()

@bot.message_handler(content_types=["text"])
def upd(message):

    global FIXED
    try:
        if message.text.lower() != "None":
            FIXED = int(message.text)
        else:
            FIXED = None
        bot.send_message(message.from_user.id, "Ok")
    except:
        pass

'''

class Detector:
    def __init__(self, camera_path=0):
        self.capture = cv2.VideoCapture(camera_path)
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        self.capture.set(cv2.CAP_PROP_FPS, 30)

    def is_available(self):
        read_ok, image = self.capture.read()
        return read_ok

    def get_image(self):
        read_ok, image = self.capture.read()
        if read_ok:
            return image
        else:
            return None

    def get_quantity(self):
        read_ok, image23 = self.capture.read()
        if read_ok:
            img_bin, image23 = balls(image23)
            img_bin, image23 = clear(img_bin, image23)
            img_bin, image23, count = find_coun(img_bin, image23)
            return count
        else:
            return False

    def close_camera(self):
        self.capture.release()

def clear(img_bin, image):
    #cv2.imwrite("1.jpg", img_bin)
    kernel = np.ones((5, 5), 'uint8')
    
    img_bin = cv2.erode(img_bin, kernel, iterations=2)
    #cv2.imwrite("2.jpg", img_bin)
    img_bin = cv2.dilate(img_bin, kernel, iterations=5)
    #cv2.imwrite("3.jpg", img_bin)
    #img_bin = cv2.dilate(img_bin, kernel, iterations=2)
    #cv2.imwrite("4.jpg", img_bin)
    #img_bin = cv2.erode(img_bin, kernel, iterations=2)
    #cv2.imwrite("5.jpg", img_bin)
    #img_bin = cv2.dilate(img_bin, kernel, iterations=3)
    #img_bin = cv2.erode(img_bin, kernel, iterations=2)
    #img_bin = cv2.dilate(img_bin, kernel, iterations=2)
    #cv2.imwrite("a.jpg", img_bin)
    return img_bin, image

def find_coun(img_bin, image):
    img_bin,image = img_bin,image
    coords = []
    _, contours, hierarchy = cv2.findContours(img_bin,cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(image, contours, -1, (255, 0, 0), 3, cv2.LINE_AA, hierarchy, 1)
    areas = []
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > 1200:
            areas.append(area)
    #print(sorted(areas))
    return img_bin, image, len(areas)

def balls(img,save:bool = True):
    #print(img)
    h,w,_ = img.shape
    #img=cv2.resize(img,(w,h))
    #img = img[93:961, 317:1579]
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV )

    h1 = 171
    s1 = 132
    v1 = 19
    h2 = 180
    s2 = 255
    v2 = 255

    h_min = np.array((h1, s1, v1), np.uint8)
    h_max = np.array((h2, s2, v2), np.uint8)
    img_bin = cv2.inRange(hsv, h_min, h_max)

    return img_bin, img

def list_int_to_bytes(input_list):
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

        @self.app.route('/upd')
        def update():
            global FIXED
            cnt = request.args.get("cnt", default=None)
            if cnt.lower() == "none":
                FIXED = None
            elif cnt.lower() == "fix":
                FIXED = -1
            else:
                FIXED = int(cnt)
            return f"Setting FIXED to {FIXED}"
        
        @self.app.route("/ui")
        def ui():
            return render_template("index.html", fixed=FIXED)
    

    def run(self):
        self.app.run(host=self.host, port=self.port)
        
server = WebServer(__name__)
Thread(target=server.run).start()

link = "/dev/" + os.readlink(r"/dev/v4l/by-path/platform-5311000.usb-usb-0:1:1.0-video-index0")[-6:]
path = "/home/orangepi/net/"

detector = Detector(link)
nonsave_timer = time.time()


while True:
    if detector.is_available == False:
        if time.time() - nonsave_timer > 10:
            spi_send([484587])
            print("negr")
        else:
            print(23)
    else:
        break
    


print(1053)
save_timer = time.time()
while True:
    img = detector.get_image()
    cherry = detector.get_quantity()
    print(cherry)
    if FIXED == -1:
        FIXED = cherry
    if FIXED is not None:
        print("Ok")
        cherry = FIXED
    
    server.update(cherry)
    spi_send([cherry])
    if time.time() - save_timer > 2:
        #cv2.imwrite("new.jpg", img)
        print("save")
        save_timer = time.time()
    time.sleep(0.5)
