from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from typing import List
import cv2
import numpy as np
import base64

from stitching import stitch_images
from detection import detect_heads_roboflow
from utils import divide_patches, estimate_yield

app = FastAPI()

@app.post("/yield-estimation/")
async def yield_estimation(files: List[UploadFile] = File(...)):
    # Step 1: Read and decode uploaded images
    images = [cv2.imdecode(np.frombuffer(await f.read(), np.uint8), cv2.IMREAD_COLOR) for f in files]

    # Step 2: Stitch them into one large field view
    stitched = stitch_images(images)
    if stitched is None:
        return JSONResponse(status_code=500, content={"error": "Image stitching failed"})

    # Step 3: Divide stitched image into patches
    patches, patch_coords = divide_patches(stitched, return_coords=True)

    total_heads = 0
    all_boxes = []

    # Step 4: Detect heads and gather adjusted bounding boxes
    for patch, (x_offset, y_offset) in zip(patches, patch_coords):
        head_count, boxes = detect_heads_roboflow(patch, conf_threshold=0.2)
        total_heads += head_count

        for x, y, w, h in boxes:
            x_full = int(x + x_offset)
            y_full = int(y + y_offset)
            all_boxes.append((x_full, y_full, int(w), int(h)))

    # Step 5: Draw bounding boxes on the stitched image
    for x, y, w, h in all_boxes:
        x1 = int(x - w / 2)
        y1 = int(y - h / 2)
        x2 = int(x + w / 2)
        y2 = int(y + h / 2)
        cv2.rectangle(stitched, (x1, y1), (x2, y2), (0, 255, 0), 2)

    # Step 6: Estimate yield
    yield_kg_per_ha = estimate_yield(total_heads)

    # Step 7: Encode stitched image with boxes to base64
    _, img_encoded = cv2.imencode('.jpg', stitched)
    img_base64 = base64.b64encode(img_encoded).decode('utf-8')

    return {
        "total_wheat_heads": total_heads,
        "estimated_yield_kg_per_ha": yield_kg_per_ha,
        "stitched_image_base64": img_base64
    }
