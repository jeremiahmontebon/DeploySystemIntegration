import cv2
import numpy as np
import face_recognition
import os
from datetime import datetime

# Global flag to control whether the attendance process should continue
attendance_process_running = True

# Path to the images directory
path = 'C:/Users/Denisse Claire/Documents/Automated-Facial-Recognition-Attendance-System-for-Classroom-Use/FacialRecognitionAttendance/ImageAttendance'
classImages = []
classNames = []
classList = os.listdir(path)

# Get the names of the photos from the filepath (ImageAttendance) without the .jpg
for cl in classList:
    currentImage = cv2.imread(f'{path}/{cl}')
    classImages.append(currentImage)
    classNames.append(os.path.splitext(cl)[0])

# Marking of attendance and showing it in a csv file
def markAttendance(name, attendance_set):
    if name not in attendance_set:
        attendance_set.add(name)
        now = datetime.now()
        dtString = now.strftime('%Y-%m-%d,%H:%M:%S')  # Add date and time

        # Read existing attendance data
        with open('C:/Users/Denisse Claire/Documents/Automated-Facial-Recognition-Attendance-System-for-Classroom-Use/FacialRecognitionAttendance/Attendance.csv', 'r') as f:
            lines = f.readlines()
        
        # Update attendance data
        with open('C:/Users/Denisse Claire/Documents/Automated-Facial-Recognition-Attendance-System-for-Classroom-Use/FacialRecognitionAttendance/Attendance.csv', 'w') as f:
            found = False
            for line in lines:
                if line.split(',')[0] == name:
                    f.write(f'{name},{dtString}\n')
                    found = True
                else:
                    f.write(line)
            if not found:
                f.write(f'{name},{dtString}\n')

# Converts images for computer processing
def findEncodings(classImages):
    encodeList = []
    for img in classImages:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList

encodeListKnown = findEncodings(classImages)
print('Encoding Complete!')

# Initializes video capture from the default camera
cap = cv2.VideoCapture(0)

# Set to keep track of attendance during the session
attendance_set = set()

# The matching of faces from the path file and webcam 
# (If match, it will display the rectangle with the name of the student and mark the attendance)
while attendance_process_running:
    success, img = cap.read()
    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    facesCurFrame = face_recognition.face_locations(imgS)
    encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)

    for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
        matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
        faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
        matchIndex = np.argmin(faceDis)

        if matches[matchIndex]:
            name = classNames[matchIndex]
            print(name)
            y1, x2, y2, x1 = faceLoc
            y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4

            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
            cv2.putText(img, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
            markAttendance(name, attendance_set)

    cv2.imshow('Attendance Checker', img)
    
    # Check for key press event to stop the application
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release video capture and close all OpenCV windows
cap.release()
cv2.destroyAllWindows()
