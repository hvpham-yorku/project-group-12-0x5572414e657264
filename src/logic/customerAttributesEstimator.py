"""
Customer check-out age, sex, and race estimator.
"""

from __future__ import annotations
from src.database.model_managers import get_customer_by_id, update_customer

import cv2



ageList=['(0-2)', '(4-6)', '(8-12)', '(15-20)', '(25-32)', '(38-43)', '(48-53)', '(60-100)']
# Age categories predicted by the pretrained age model
genderList=['Male','Female']
# Gender categories predicted by the pretrained gender model

MODEL_MEAN_VALUES=(78.4263377603, 87.7689143744, 114.895847746)
# BGR values

faceProto="src/assets/opencv_face_detector.pbtxt"
faceModel="src/assets/opencv_face_detector_uint8.pb"
ageProto="src/assets/age_deploy.prototxt"
ageModel="src/assets/age_net.caffemodel"
genderProto="src/assets/gender_deploy.prototxt"
genderModel="src/assets/gender_net.caffemodel"

faceNet=cv2.dnn.readNet(faceModel,faceProto)
ageNet=cv2.dnn.readNet(ageModel,ageProto)
genderNet=cv2.dnn.readNet(genderModel,genderProto)
# Loading the pretrained neural network models into OpenCV






def highlightFace(net, frame, conf_threshold=0.7):
    # Function detects faces in the given frame using a pretrained face detection model.

    frameHeight=frame.shape[0]
    frameWidth=frame.shape[1]
    # Image dimensions (height and width)

    blob=cv2.dnn.blobFromImage(frame, 1.0, (300, 300), [104, 117, 123], True, False)
    # Converting image into a "blob" as required by OpenCV's DNN module.
    # Parameters:
    # 1.0 => scaling factor
    # (300,300) => resize image to model input size
    # [104,117,123] => mean subtraction values used for normalization
    # True => swap red/blue channels
    # False => do not crop image

    net.setInput(blob)
    detections=net.forward()
    # get face detection results

    faceBoxes=[]
    # List to store coordinates of detected face bounding boxes

    for i in range(detections.shape[2]):
        # Loop through all detected objects returned by the model

        confidence=detections[0,0,i,2]
        # Confidence score for the detection

        if confidence>conf_threshold:
            # Only keep detections above the confidence threshold

            x1=int(detections[0,0,i,3]*frameWidth)
            y1=int(detections[0,0,i,4]*frameHeight)
            x2=int(detections[0,0,i,5]*frameWidth)
            y2=int(detections[0,0,i,6]*frameHeight)
            # onvert  bounding box coordinates to pixel coordinates

            faceBoxes.append([x1,y1,x2,y2])
            # Save the bounding box

    return faceBoxes

# -----------------------------------------

def estimateAttributes(image_path, id):

    frame = cv2.imread(image_path)

    if frame is None:
        print("Image loading fail")
        exit(1)

    faceBoxes=highlightFace(faceNet,frame)
    
    if not faceBoxes:
        print("No face detected")
        return None
    
    faceBox = faceBoxes[0]
    
    padding = 20
    # Extra pixels to add around the detected face before running age/gender prediction

    face=frame[max(0,faceBox[1]-padding):
                min(faceBox[3]+padding,frame.shape[0]-1),max(0,faceBox[0]-padding)
                :min(faceBox[2]+padding, frame.shape[1]-1)]
    # Crop the face region from the image with the padding

    blob=cv2.dnn.blobFromImage(face, 1.0, (227,227), MODEL_MEAN_VALUES, swapRB=False)
    # Convert the cropped face image into a blob

    genderNet.setInput(blob)
    genderPreds=genderNet.forward()
    # Gender prediction

    gender=genderList[genderPreds[0].argmax()]
    # Select gender with the highest probability
    ageNet.setInput(blob)
    agePreds=ageNet.forward()
    # Age prediction

    age=ageList[agePreds[0].argmax()]
    # Select age group with the highest probability

    #Upate age and gender attributes in database by searching with given id
    customer = get_customer_by_id(id)
    if customer is not None:
        customer.age = age[1:-1]
        customer.sex = gender
        updated_customer = update_customer(customer)


    return age, gender #temporarily return age and gender for testing