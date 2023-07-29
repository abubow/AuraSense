import cv2
import numpy as np
import serial.tools.list_ports

# Find the Bluetooth serial port
bluetooth_port = None
for port in serial.tools.list_ports.comports():
    if "Bluetooth" in port.description:
        bluetooth_port = port.device
        break

if not bluetooth_port:
    print("Bluetooth device not found.")
    exit(1)

# Open the Bluetooth serial port
ser = serial.Serial(bluetooth_port, baud_rate)

while True:
    try:
        # Read the data from the Bluetooth serial port
        data = ser.read(1024)

        # Convert the received data to a NumPy array
        np_array = np.frombuffer(data, dtype=np.uint8)

        # Decode the JPEG image using OpenCV
        frame = cv2.imdecode(np_array, cv2.IMREAD_COLOR)

        # Display the frame
        cv2.imshow("Video Stream", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    except KeyboardInterrupt:
        break

ser.close()
cv2.destroyAllWindows()