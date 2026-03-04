"""
Customer check-out age, sex, and race estimator.
"""
from __future__ import annotations










#A Gender and Age Detection program by Mahesh Sawant   # [OG COMMENT]

import cv2                 # [NEW COMMENT] OpenCV library used for image processing and neural network inference
import argparse            # [NEW COMMENT] Used to read command-line arguments (e.g., passing an image path)

def highlightFace(net, frame, conf_threshold=0.7):
    # [NEW COMMENT] This function detects faces in the given frame using a pretrained face detection model.
    # net: the loaded face detection neural network
    # frame: image/frame to process
    # conf_threshold: minimum confidence required to consider a detection as a face

    frameOpencvDnn=frame.copy()
    # [NEW COMMENT] Copy the original frame so rectangles can be drawn without modifying the original image

    frameHeight=frameOpencvDnn.shape[0]
    frameWidth=frameOpencvDnn.shape[1]
    # [NEW COMMENT] Get image dimensions (height and width)

    blob=cv2.dnn.blobFromImage(frameOpencvDnn, 1.0, (300, 300), [104, 117, 123], True, False)
    # [NEW COMMENT] Convert the image into a "blob" which is the format required by OpenCV's DNN module.
    # Parameters:
    # 1.0 → scaling factor
    # (300,300) → resize image to model input size
    # [104,117,123] → mean subtraction values used for normalization
    # True → swap red/blue channels
    # False → do not crop image

    net.setInput(blob)
    # [NEW COMMENT] Provide the blob as input to the face detection neural network

    detections=net.forward()
    # [NEW COMMENT] Run a forward pass through the network to get face detection results

    faceBoxes=[]
    # [NEW COMMENT] List that will store coordinates of detected face bounding boxes

    for i in range(detections.shape[2]):
        # [NEW COMMENT] Loop through all detected objects returned by the model

        confidence=detections[0,0,i,2]
        # [NEW COMMENT] Extract the confidence score for this detection

        if confidence>conf_threshold:
            # [NEW COMMENT] Only keep detections above the confidence threshold

            x1=int(detections[0,0,i,3]*frameWidth)
            y1=int(detections[0,0,i,4]*frameHeight)
            x2=int(detections[0,0,i,5]*frameWidth)
            y2=int(detections[0,0,i,6]*frameHeight)
            # [NEW COMMENT] Convert normalized bounding box coordinates to pixel coordinates

            faceBoxes.append([x1,y1,x2,y2])
            # [NEW COMMENT] Save the bounding box for later processing

            cv2.rectangle(frameOpencvDnn, (x1,y1), (x2,y2), (0,255,0), int(round(frameHeight/150)), 8)
            # [NEW COMMENT] Draw a green rectangle around the detected face

    return frameOpencvDnn,faceBoxes
    # [NEW COMMENT] Return the image with rectangles + list of face coordinates


parser=argparse.ArgumentParser()
# [NEW COMMENT] Create argument parser object

parser.add_argument('--image')
# [NEW COMMENT] Allows user to pass an image path using: python detect.py --image path.jpg

args=parser.parse_args()
# [NEW COMMENT] Parse command-line arguments

faceProto="opencv_face_detector.pbtxt"
faceModel="opencv_face_detector_uint8.pb"
ageProto="age_deploy.prototxt"
ageModel="age_net.caffemodel"
genderProto="gender_deploy.prototxt"
genderModel="gender_net.caffemodel"
# [NEW COMMENT] File paths for pretrained neural network models used in detection

MODEL_MEAN_VALUES=(78.4263377603, 87.7689143744, 114.895847746)
# [NEW COMMENT] Mean values used to normalize images before feeding into the age/gender networks

ageList=['(0-2)', '(4-6)', '(8-12)', '(15-20)', '(25-32)', '(38-43)', '(48-53)', '(60-100)']
# [NEW COMMENT] Age categories predicted by the pretrained age model

genderList=['Male','Female']
# [NEW COMMENT] Gender categories predicted by the pretrained gender model

faceNet=cv2.dnn.readNet(faceModel,faceProto)
ageNet=cv2.dnn.readNet(ageModel,ageProto)
genderNet=cv2.dnn.readNet(genderModel,genderProto)
# [NEW COMMENT] Load the pretrained neural network models into OpenCV

video=cv2.VideoCapture(args.image if args.image else 0)
# [NEW COMMENT]
# If an image path is provided → load that image
# Otherwise → open the webcam (device index 0)

padding=20
# [NEW COMMENT] Adds extra pixels around the detected face before running age/gender prediction

while cv2.waitKey(1)<0 :
    # [NEW COMMENT] Loop continuously while frames are available

    hasFrame,frame=video.read()
    # [NEW COMMENT] Capture the next frame from the webcam or image

    if not hasFrame:
        cv2.waitKey()
        break
        # [NEW COMMENT] Stop if no frame was captured

    resultImg,faceBoxes=highlightFace(faceNet,frame)
    # [NEW COMMENT] Detect faces in the frame

    if not faceBoxes:
        print("No face detected")
        # [NEW COMMENT] If no faces found, print message

    for faceBox in faceBoxes:
        # [NEW COMMENT] Process each detected face individually

        face=frame[max(0,faceBox[1]-padding):
                   min(faceBox[3]+padding,frame.shape[0]-1),max(0,faceBox[0]-padding)
                   :min(faceBox[2]+padding, frame.shape[1]-1)]
        # [NEW COMMENT] Crop the face region from the image with some padding

        blob=cv2.dnn.blobFromImage(face, 1.0, (227,227), MODEL_MEAN_VALUES, swapRB=False)
        # [NEW COMMENT] Convert the cropped face image into a blob for the neural networks

        genderNet.setInput(blob)
        genderPreds=genderNet.forward()
        # [NEW COMMENT] Run gender prediction

        gender=genderList[genderPreds[0].argmax()]
        # [NEW COMMENT] Select the predicted gender with the highest probability

        print(f'Gender: {gender}')
        # [NEW COMMENT] Print gender prediction to console

        ageNet.setInput(blob)
        agePreds=ageNet.forward()
        # [NEW COMMENT] Run age prediction

        age=ageList[agePreds[0].argmax()]
        # [NEW COMMENT] Select the predicted age group with the highest probability

        print(f'Age: {age[1:-1]} years')
        # [NEW COMMENT] Print age prediction (removes parentheses from label)

        cv2.putText(resultImg, f'{gender}, {age}', (faceBox[0], faceBox[1]-10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,255), 2, cv2.LINE_AA)
        # [NEW COMMENT] Draw predicted age and gender label above the face

        cv2.imshow("Detecting age and gender", resultImg)
        # [NEW COMMENT] Display the result image with bounding boxes and predictions
