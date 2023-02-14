import numpy as np
import cv2
import sys
import argparse
import time

def relativePosition(rvec1, tvec1, rvec2, tvec2):
    rvec1, tvec1 = rvec1.reshape((3, 1)), tvec1.reshape(
        (3, 1))
    rvec2, tvec2 = rvec2.reshape((3, 1)), tvec2.reshape((3, 1))

    # Inverse the second marker, the right one in the image
    invRvec, invTvec = inversePerspective(rvec2, tvec2)

    orgRvec, orgTvec = inversePerspective(invRvec, invTvec)
    # print("rvec: ", rvec2, "tvec: ", tvec2, "\n and \n", orgRvec, orgTvec)

    info = cv2.composeRT(rvec1, tvec1, invRvec, invTvec)
    composedRvec, composedTvec = info[0], info[1]

    composedRvec = composedRvec.reshape((3, 1))
    composedTvec = composedTvec.reshape((3, 1))
    return composedRvec, composedTvec


def inversePerspective(rvec, tvec):
    R, _ = cv2.Rodrigues(rvec)
    R = np.matrix(R).T
    invTvec = np.dot(-R, np.matrix(tvec))
    invRvec, _ = cv2.Rodrigues(R)
    return invRvec, invTvec


def pose_esitmation(frame, aruco_dict_type, matrix_coefficients, distortion_coefficients):

    '''
    frame - Frame from the video stream
    matrix_coefficients - Intrinsic matrix of the calibrated camera
    distortion_coefficients - Distortion coefficients associated with your camera

    return:-
    frame - The frame with the axis drawn on it
    '''

    #gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    #cv2.aruco_dict = cv2.aruco.Dictionary_get(aruco_dict_type)
    #parameters = cv2.aruco.DetectorParameters_create()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_250)
    #parameters = cv2.aruco.DetectorParameters_create()
    parameters =  cv2.aruco.DetectorParameters()
    detector = cv2.aruco.ArucoDetector(aruco_dict, parameters)


    corners, ids, rejected_img_points = detector.detectMarkers(gray)
    vectors = {}
    if len(corners) > 0:
        for i in range(0, len(ids)):
            print(ids)
            if ids[i] in [140, 134, 142, 20]:
                # Estimate pose of each marker and return the values rvec and tvec---(different from those of camera coefficients)
                if ids[i] == 20:
                    size = 100
                else:
                    size = 60
                rvec, tvec, markerPoints = cv2.aruco.estimatePoseSingleMarkers(corners[i], 60, matrix_coefficients,
                                                                       distortion_coefficients)
                #print(rvec)
                V = tvec[0][0][1]
                dist = tvec[0][0][2]
                distance = dist ** 2 - V ** 2
                #print(tvec[0][0][0])
                print(f"MARKER {ids[i]}")
                print("Transform:", tvec)
                vectors[ids[i][0]] = [rvec, tvec]
                #print("Distance:", int(distance ** 0.5))
                
                #print("Dist:", int(tvec[0][0][2] / 10), "X:", tvec[0][0][1])
                #print("With height correction:", int(tvec[0][0][2] / 10))

                # Draw a square around the markers
                cv2.aruco.drawDetectedMarkers(frame, corners) 

                # Draw Axis
                cv2.drawFrameAxes(frame, matrix_coefficients, distortion_coefficients, rvec, tvec, 1000)  
        #print(np.linalg.norm(vectors[142][1] - vectors[20][1])) 
        #cv2.drawFrameAxes(frame, matrix_coefficients, distortion_coefficients, composedRvec, composedTvec, 50)
        print("----")
    return frame


def undistort(img):
    DIM = img.shape[:2][::-1]
    map1, map2 = cv2.fisheye.initUndistortRectifyMap(k, d, np.eye(3), k, DIM, cv2.CV_16SC2)
    undistorted_img = cv2.remap(img, map1, map2, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
    return undistorted_img[::]


if __name__ == '__main__':

    ap = argparse.ArgumentParser()
    ap.add_argument("-k", "--K_Matrix", required=False, help="Path to calibration matrix (numpy file)")
    ap.add_argument("-d", "--D_Coeff", required=False, help="Path to distortion coefficients (numpy file)")
    ap.add_argument("-t", "--type", type=str, default="DICT_4X4_250", help="Type of ArUCo tag to detect")
    args = vars(ap.parse_args())

    aruco_dict_type = "fix"
    calibration_matrix_path = args["K_Matrix"]
    distortion_coefficients_path = args["D_Coeff"]
    
    k = np.array([[896.128972098295, 0.0, 959.6108625623755], [0.0, 901.0779296900218, 534.4228432183535], [0.0, 0.0, 1.0]]) #np.array([[615.5265089586733, 0.0, 309.3014206158378], [0.0, 616.3145552040991, 234.92170696626567], [0.0, 0.0, 1.0]]) #np.load(calibration_matrix_path)
    d = np.array([[-0.04048025498479023], [0.061095515746160366], [-0.06836476062818098], [0.024622705491456814]]) #np.array([[0.5834358848094446], [-3.892195415621445], [24.02626662491725], [-55.15598762358913]]) #np.load(distortion_coefficients_path)
    #k = np.array([[1049.4673314874963, 0.0, 643.9792663692622], [0.0, 1051.6357264680573, 477.3588523460414], [0.0, 0.0, 1.0]])
    #d = np.array([[0.2310480513659108, -1.6001552027121113, 0.0024900052672389055, 0.00032059014442499577, 3.982962371776458]])
    #k = np.array([[507.29625375090217, 0.0, 317.5497198412449], [0.0, 507.34905473494405, 234.20842109977096], [0.0, 0.0, 1.0]])
    #d = np.array([[0.11152212236108483, -0.4399806948019915, 0.0017316181561854562, 0.0009066819524684486, 0.6733576472184958]])
    #video = cv2.VideoCapture("/home/stephan/Progs/eurobot-2023/CoordsDetection/old.mp4")
    video = cv2.VideoCapture(3)
    video.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    video.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    video.set(3,1920)
    video.set(4, 1080)
    video.set(30,0.1)

    #time.sleep(2.0)

    while True:
        ret, frame = video.read()
        #ret = 1
        #frame = cv2.imread("test.png")
        frame = undistort(frame)


        if not ret:
            break
        
        output = pose_esitmation(frame, aruco_dict_type, k, d)
        #output = cv2.resize((0, 0), frame, fx=0.6, fy=0.6)
        output = cv2.resize(output, (640, 480))

        cv2.imshow('Estimated Pose', output)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break

    video.release()
    cv2.destroyAllWindows()

