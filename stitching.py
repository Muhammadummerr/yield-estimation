import cv2

def stitch_images(images):
    stitcher = cv2.Stitcher_create()
    status, stitched = stitcher.stitch(images)
    return stitched if status == cv2.Stitcher_OK else None
