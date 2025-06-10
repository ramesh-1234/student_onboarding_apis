# app/utils/pan_extractor.py

import cv2
import numpy as np
import os
from pdf2image import convert_from_path
import face_recognition


def extract_pan_photo_signature(pan_image_path):
    """
    Load PAN image and detect the face using face_recognition.
    Detect the signature using contour detection (approx).
    Returns: pan_face_img, pan_signature_img
    """
    if pan_image_path.lower().endswith('.pdf'):
        images = convert_from_path(pan_image_path)
        if len(images) == 0:
            raise ValueError("No pages found in PDF.")
        temp_img_path = "temp_pan_image.png"
        images[0].save(temp_img_path, 'PNG')
        pan_img = cv2.imread(temp_img_path)
        os.remove(temp_img_path)
    else:
        pan_img = cv2.imread(pan_image_path)

    if pan_img is None:
        raise ValueError(f"Could not load image: {pan_image_path}")

    rgb = cv2.cvtColor(pan_img, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(rgb)

    if not face_locations:
        raise ValueError("No face found in PAN image.")

    top, right, bottom, left = face_locations[0]
    face_crop = pan_img[top:bottom, left:right]

    gray = cv2.cvtColor(pan_img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(
        thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    sig_crop = None
    height, width = gray.shape
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        if w > 200 and h < 150 and y > height * 0.6:
            sig_crop = pan_img[y:y + h, x:x + w]
            break

    if sig_crop is None:
        raise ValueError("Signature not detected.")

    return face_crop, sig_crop


# def extract_pan_photo_signature(pan_image_path):
#     import imghdr

#     if pan_image_path.lower().endswith('.pdf'):
#         images = convert_from_path(pan_image_path)
#         if len(images) == 0:
#             raise ValueError("No pages found in PDF.")
#         temp_img_path = "temp_pan_image.png"
#         images[0].save(temp_img_path, 'PNG')
#         pan_img = cv2.imread(temp_img_path)
#         os.remove(temp_img_path)
#     else:
#         if imghdr.what(pan_image_path) not in ['jpg', 'jpeg', 'png']:
#             raise ValueError("Unsupported image format")
#         pan_img = cv2.imread(pan_image_path)

#     if pan_img is None:
#         raise ValueError(f"Could not load image: {pan_image_path}")

#     # Face detection
#     rgb = cv2.cvtColor(pan_img, cv2.COLOR_BGR2RGB)
#     face_locations = face_recognition.face_locations(rgb)

#     if not face_locations:
#         raise ValueError(
#             "No face found in PAN image. Try uploading a clearer or uncropped image.")

#     top, right, bottom, left = face_locations[0]
#     face_crop = pan_img[top:bottom, left:right]

#     # Signature detection
#     gray = cv2.cvtColor(pan_img, cv2.COLOR_BGR2GRAY)
#     _, thresh = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY_INV)
#     contours, _ = cv2.findContours(
#         thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

#     sig_crop = None
#     height, width = gray.shape
#     for cnt in contours:
#         x, y, w, h = cv2.boundingRect(cnt)
#         print(f"Checking contour: x={x}, y={y}, w={w}, h={h}")
#         if 100 < w < 500 and 30 < h < 200 and y > height * 0.5:
#             sig_crop = pan_img[y:y + h, x:x + w]
#             break

#     if sig_crop is None:
#         raise ValueError(
#             "Signature not detected. Try a higher-resolution scan.")

#     return face_crop, sig_crop
