#np.array([[615.5265089586733, 0.0, 309.3014206158378], [0.0, 616.3145552040991, 234.92170696626567], [0.0, 0.0, 1.0]])
#np.array([[0.5834358848094446], [-3.892195415621445], [24.02626662491725], [-55.15598762358913]])
# Testing
import numpy as np
import cv2
import sys
from utils import ARUCO_DICT
import argparse
import time


def pose_esitmation(frame, aruco_dict_type, matrix_coefficients, distortion_coefficients):

    '''
    frame - Frame from the video stream
    matrix_coefficients - Intrinsic matrix of the calibrated camera
    distortion_coefficients - Distortion coefficients associated with your camera

    return:-
    frame - The frame with the axis drawn on it
    '''

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    cv2.aruco_dict = cv2.aruco.Dictionary_get(aruco_dict_type)
    parameters = cv2.aruco.DetectorParameters_create()


    corners, ids, rejected_img_points = cv2.aruco.detectMarkers(gray, cv2.aruco_dict,parameters=parameters)

        # If markers are detected
    if len(corners) > 0:
        for i in range(0, len(ids)):
            if ids[i] == 42:
                # Estimate pose of each marker and return the values rvec and tvec---(different from those of camera coefficients)
                rvec, tvec, markerPoints = cv2.aruco.estimatePoseSingleMarkers(corners[i], 54, matrix_coefficients,
                                                                       distortion_coefficients)
                #print(rvec)
                V = tvec[0][0][1]
                dist = tvec[0][0][2]
                distance = dist ** 2 - V ** 2
                #print(tvec[0][0][0])
                print("Distance:", int(distance ** 0.5))
                #print("Dist:", int(tvec[0][0][2] / 10), "X:", tvec[0][0][1])
                print(int(tvec[0][0][2] / 10))
                # Draw a square around the markers
                cv2.aruco.drawDetectedMarkers(frame, corners) 

                # Draw Axis
                cv2.drawFrameAxes(frame, matrix_coefficients, distortion_coefficients, rvec, tvec, 0.01)  
        print("----")
    return frame

if __name__ == '__main__':

    ap = argparse.ArgumentParser()
    ap.add_argument("-k", "--K_Matrix", required=False, help="Path to calibration matrix (numpy file)")
    ap.add_argument("-d", "--D_Coeff", required=False, help="Path to distortion coefficients (numpy file)")
    ap.add_argument("-t", "--type", type=str, default="DICT_4X4_250", help="Type of ArUCo tag to detect")
    args = vars(ap.parse_args())

    
    if ARUCO_DICT.get(args["type"], None) is None:
        print(f"ArUCo tag type '{args['type']}' is not supported")
        sys.exit(0)

    aruco_dict_type = ARUCO_DICT[args["type"]]
    calibration_matrix_path = args["K_Matrix"]
    distortion_coefficients_path = args["D_Coeff"]
    
    #k = np.array([[896.128972098295, 0.0, 959.6108625623755], [0.0, 901.0779296900218, 534.4228432183535], [0.0, 0.0, 1.0]]) #np.array([[615.5265089586733, 0.0, 309.3014206158378], [0.0, 616.3145552040991, 234.92170696626567], [0.0, 0.0, 1.0]]) #np.load(calibration_matrix_path)
    #d = np.array([[-0.04048025498479023], [0.061095515746160366], [-0.06836476062818098], [0.024622705491456814]]) #np.array([[0.5834358848094446], [-3.892195415621445], [24.02626662491725], [-55.15598762358913]]) #np.load(distortion_coefficients_path)
    #k = np.array([[1049.4673314874963, 0.0, 643.9792663692622], [0.0, 1051.6357264680573, 477.3588523460414], [0.0, 0.0, 1.0]])
    #d = np.array([[0.2310480513659108, -1.6001552027121113, 0.0024900052672389055, 0.00032059014442499577, 3.982962371776458]])
    k = np.array([[507.29625375090217, 0.0, 317.5497198412449], [0.0, 507.34905473494405, 234.20842109977096], [0.0, 0.0, 1.0]])
    d = np.array([[0.11152212236108483, -0.4399806948019915, 0.0017316181561854562, 0.0009066819524684486, 0.6733576472184958]])
    #video = cv2.VideoCapture("/home/stephan/Progs/eurobot-2023/CoordsDetection/old.mp4")
    video = cv2.VideoCapture("http://192.168.1.4:4747/video?640x480")
    #time.sleep(2.0)

    while True:
        ret, frame = video.read()

        if not ret:
            break
        
        output = pose_esitmation(frame, aruco_dict_type, k, d)

        cv2.imshow('Estimated Pose', output)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break

    video.release()
    cv2.destroyAllWindows()
