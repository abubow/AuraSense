import cv2
from ultralytics import YOLO

# Load the pre-trained YOLOv8 model
model = YOLO("yolov8n.pt")

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

        # Convert the frame to RGB for YOLOv8
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Predict objects using YOLOv8
        results = model.predict(frame_rgb)

        # Plot the bounding boxes and labels on the frame
        frame_with_bboxes = results[0].plot(boxes=True, labels=True, conf=True)

        # Calculate FPS and add FPS text overlay on the frame
        current_time = cv2.getTickCount()
        fps = cv2.getTickFrequency() / (current_time - prev_time)
        prev_time = current_time
        fps_text = f"FPS: {fps:.2f}"
        cv2.putText(frame_with_bboxes, fps_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        # Display the frame with bounding boxes
        cv2.imshow("Object Detection", frame_with_bboxes)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    except KeyboardInterrupt:
        break

cap.release()
cv2.destroyAllWindows()