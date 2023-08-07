import cv2
import requests
import numpy as np
import dlib

# Load the pre-trained face detection model
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

# Load the pre-trained face recognition model
face_recognizer = dlib.face_recognition_model_v1("shape_predictor_68_face_landmarks.dat")

# ESP32-CAM streaming URL
url = "http://192.168.18.179/"

# Create VideoCapture object
cap = cv2.VideoCapture(url)

# Initialize FPS variables
fps = 0.0
prev_time = 0

# Load a sample face image for comparison
sample_image = cv2.imread("sample_face.jpg")
sample_face_encoding = face_recognizer.compute_face_descriptor(sample_image)

while True:
    try:
        # Read a frame from the video stream
        ret, frame = cap.read()

        if not ret:
            print("Failed to receive a frame from the video stream.")
            break

        # Convert the frame to grayscale for face detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect faces in the frame
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        for (x, y, w, h) in faces:
            # Extract the face region
            face = frame[y:y + h, x:x + w]

            # Convert the face to grayscale for face recognition
            face_gray = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)

            # Perform face recognition
            face_encoding = face_recognizer.compute_face_descriptor(face_gray)

            # Calculate the Euclidean distance between the sample face encoding and the current face encoding
            distance = np.linalg.norm(np.array(face_encoding) - np.array(sample_face_encoding))

            # Draw the bounding box around the detected face
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # Display the uniqueness as a number
            uniqueness_text = f"Uniqueness: {distance:.2f}"
            cv2.putText(frame, uniqueness_text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

        # Calculate FPS
        current_time = cv2.getTickCount()
        fps = cv2.getTickFrequency() / (current_time - prev_time)
        prev_time = current_time

        # Add FPS text overlay on the frame
        fps_text = f"FPS: {fps:.2f}"
        cv2.putText(frame, fps_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        # Display the frame
        cv2.imshow("Face Detection", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    except KeyboardInterrupt:
        break

cap.release()
cv2.destroyAllWindows()