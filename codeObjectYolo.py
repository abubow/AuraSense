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

average = 0
sum = 0
count = 0
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

        # Plot the masks on the frame
        frame_with_masks = results[0].plot(masks=True, conf=True, img=frame)

        # Calculate FPS and add FPS text overlay on the frame
        current_time = cv2.getTickCount()
        fps = cv2.getTickFrequency() / (current_time - prev_time)
        prev_time = current_time
        fps_text = f"FPS: {fps:.2f}"
        if count < 20 and count >= 0:
            sum += fps
            count += 1
        else:
            average = sum/count
            sum = 0
            count = 0
        average_text = f"Average: {average:.2f}"
        cv2.putText(frame_with_masks, fps_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        cv2.putText(frame_with_masks, average_text, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        # Display the frame with masks
        cv2.imshow("Object Detection with Masks", frame_with_masks)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    except KeyboardInterrupt:
        break

cap.release()
cv2.destroyAllWindows()