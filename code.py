import cv2
import requests
import numpy as np

# ESP32-CAM streaming URL
url = "http://192.168.18.179/"

# Create VideoCapture object
cap = cv2.VideoCapture(url)

# Initialize FPS variables
fps = 0.0
prev_time = 0

while True:
    try:
        # Read a frame from the video stream
        ret, frame = cap.read()

        if not ret:
            print("Failed to receive a frame from the video stream.")
            break

        # Calculate FPS
        current_time = cv2.getTickCount()
        fps = cv2.getTickFrequency() / (current_time - prev_time)
        prev_time = current_time

        # Add FPS text overlay on the frame
        fps_text = f"FPS: {fps:.2f}"
        cv2.putText(frame, fps_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        # Display the frame
        cv2.imshow("Video Stream", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    except KeyboardInterrupt:
        break

cap.release()
cv2.destroyAllWindows()