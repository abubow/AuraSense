import cv2
import numpy as np
from transformers import DPTImageProcessor, DPTForDepthEstimation
import torch
from PIL import Image

# Load video 
cap = cv2.VideoCapture('https://sample-videos.com/video123/mp4/720/big_buck_bunny_720p_1mb.mp4')

# Output depth video
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = cap.get(cv2.CAP_PROP_FPS) 
out = cv2.VideoWriter('depth.mp4', cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height))

processor = DPTImageProcessor.from_pretrained("Intel/dpt-large")
model = DPTForDepthEstimation.from_pretrained("Intel/dpt-large")

while(cap.isOpened()):
    ret, frame = cap.read()
    
    if ret == True:

        # Convert to PIL Image
        pil_im = Image.fromarray(frame)
        
        # Get depth map
        inputs = processor(images=pil_im, return_tensors="pt")
        with torch.no_grad():
            outputs = model(**inputs)
            predicted_depth = outputs.predicted_depth

        prediction = torch.nn.functional.interpolate(
            predicted_depth.unsqueeze(1),
            size=pil_im.size[::-1],
            mode="bicubic",
            align_corners=False,
        )

        output = prediction.squeeze().cpu().numpy()
        depth_frame = (output * 255 / np.max(output)).astype("uint8")
        
        # Save frame to video
        depth_frame = cv2.applyColorMap(depth_frame, cv2.COLORMAP_JET)
        out.write(depth_frame)
        
    else:
        break
        
cap.release()
out.release()
cv2.destroyAllWindows()