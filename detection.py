from inference_sdk import InferenceHTTPClient
import cv2
import tempfile

CLIENT = InferenceHTTPClient(
    api_url="https://detect.roboflow.com",
    api_key="e9wUdW3vYMtL5zvI6ERC"
)

def detect_heads_roboflow(image, conf_threshold=0.1):
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp:
        cv2.imwrite(temp.name, image)
        result = CLIENT.infer(temp.name, model_id="global-wheat-2021/1")

    boxes = []
    for pred in result["predictions"]:
        if pred["confidence"] >= conf_threshold:
            x, y, w, h = pred["x"], pred["y"], pred["width"], pred["height"]
            boxes.append((x, y, w, h))
    
    return len(boxes), boxes
