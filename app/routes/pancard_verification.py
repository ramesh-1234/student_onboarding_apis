import cv2
import numpy as np
import face_recognition
import tkinter as tk
from tkinter import filedialog
from skimage.metrics import structural_similarity as ssim
from pdf2image import convert_from_path
import os
import tempfile
import webbrowser
import time


def extract_pan_photo_signature(pan_image_path):
    """
    Load PAN image and detect the face using face_recognition.
    Detect the signature using contour detection (approx).
    Returns: pan_face_img, pan_signature_img
    """
    # Handle PDF: convert first page to image
    if pan_image_path.lower().endswith('.pdf'):
        images = convert_from_path(pan_image_path)
        if len(images) == 0:
            print("No pages found in PDF.")
            exit(1)
        # Save first page as temporary PNG
        temp_img_path = "temp_pan_image.png"
        images[0].save(temp_img_path, 'PNG')
        pan_img = cv2.imread(temp_img_path)
        # Remove temp image after loading
        os.remove(temp_img_path)
    else:
        pan_img = cv2.imread(pan_image_path)

    if pan_img is None:
        print(f"Could not load image: {pan_image_path}")
        exit(1)

    # --- Face Detection ---
    rgb = cv2.cvtColor(pan_img, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(rgb)

    if not face_locations:
        print("No face found in PAN image.")
        exit(1)

    # Assume first detected face is the correct one
    top, right, bottom, left = face_locations[0]
    face_crop = pan_img[top:bottom, left:right]

    # --- Signature Detection via Contours ---
    gray = cv2.cvtColor(pan_img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY_INV)

    contours, _ = cv2.findContours(
        thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    sig_crop = None
    height, width = gray.shape
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        # Heuristics: signature is usually a wide, short region near bottom
        if w > 200 and h < 150 and y > height * 0.6:
            sig_crop = pan_img[y:y+h, x:x+w]
            break

    if sig_crop is None:
        print("Signature not detected.")
        exit(1)

    # Optional: draw rectangles for debug (commented out because no imshow)
    # cv2.rectangle(pan_img, (left, top), (right, bottom), (0, 255, 0), 2)
    # if sig_crop is not None:
    #     cv2.rectangle(pan_img, (x, y), (x + w, y + h), (255, 0, 0), 2)

    # We don't show images because of your environment

    return face_crop, sig_crop


def capture_live_photo():
    """
    Capture one frame from webcam for live photo and save it.
    Automatically opens the image in the default viewer.
    """
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Cannot access webcam.")
        exit(1)

    print("Capturing live photo. Please look at the camera...")
    ret, frame = cap.read()
    cap.release()

    if not ret:
        print("Failed to capture frame from webcam.")
        exit(1)

    photo_path = "live_photo.jpg"
    cv2.imwrite(photo_path, frame)
    print(f"Live photo saved as {photo_path}")

    # Open image with default viewer
    try:
        abs_path = os.path.abspath(photo_path)
        webbrowser.open(abs_path)
    except Exception as e:
        print("Failed to open image viewer:", e)

    return frame


def capture_live_signature():
    """
    Wait 5 seconds, then capture signature image and show it.
    """
    print("Get ready to show your signature to the webcam in 5 seconds...")
    time.sleep(5)

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Cannot access webcam.")
        exit(1)

    print("Capturing signature...")
    ret, frame = cap.read()
    cap.release()

    if not ret:
        print("Failed to capture frame from webcam.")
        exit(1)

    sig_path = "live_signature.jpg"
    cv2.imwrite(sig_path, frame)
    print(f"Live signature saved as {sig_path}")

    # Open image with default viewer
    try:
        abs_path = os.path.abspath(sig_path)
        webbrowser.open(abs_path)
    except Exception as e:
        print("Failed to open image viewer:", e)

    return frame


def compare_faces(face_img1, face_img2):
    """
    Compare two face images and return True if they match.
    """
    try:
        # Ensure BGR to RGB conversion
        face_img1_rgb = cv2.cvtColor(face_img1, cv2.COLOR_BGR2RGB)
        # Ensure uint8 type and 3 channels
        face_img1_rgb = face_img1_rgb.astype(np.uint8)

        encodings1 = face_recognition.face_encodings(face_img1_rgb)
        if len(encodings1) == 0:
            print("No face found in PAN image.")
            return False
        enc1 = encodings1[0]

    except Exception as e:
        print(f"Error processing PAN face image: {e}")
        return False

    try:
        face_img2_rgb = cv2.cvtColor(face_img2, cv2.COLOR_BGR2RGB)
        face_img2_rgb = face_img2_rgb.astype(np.uint8)

        encodings2 = face_recognition.face_encodings(face_img2_rgb)
        if len(encodings2) == 0:
            print("No face found in live photo.")
            return False
        enc2 = encodings2[0]

    except Exception as e:
        print(f"Error processing live face image: {e}")
        return False

    # Compute distance and compare
    distance = np.linalg.norm(enc1 - enc2)
    print(f"Face distance: {distance:.3f}")
    threshold = 0.6
    return distance < threshold


def compare_signatures(sig_img1, sig_img2):
    """
    Compare two signature images using SSIM.
    Return similarity score and True if above threshold.
    """
    gray1 = cv2.cvtColor(sig_img1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(sig_img2, cv2.COLOR_BGR2GRAY)
    # Resize both to same shape
    gray2 = cv2.resize(gray2, (gray1.shape[1], gray1.shape[0]))

    score = ssim(gray1, gray2)
    print(f"Signature Similarity Score: {score:.2f}")
    threshold = 0.4
    return score, score > threshold


def check_sunglasses(face_img):
    """
    Detect if person is wearing sunglasses by eye brightness analysis.
    Returns True if sunglasses detected.
    """
    gray = cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY)
    eyes_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + 'haarcascade_eye.xml')
    eyes = eyes_cascade.detectMultiScale(gray, 1.1, 4)
    for (ex, ey, ew, eh) in eyes:
        eye_roi = gray[ey:ey+eh, ex:ex+ew]
        brightness = np.mean(eye_roi)
        if brightness < 50:  # Threshold may need tuning
            return True
    return False


def select_pan_image():
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    file_path = filedialog.askopenfilename(
        title="Select PAN Card Image (Image or PDF)",
        filetypes=[("Image and PDF Files", "*.jpg *.jpeg *.png *.pdf")]
    )
    return file_path


if __name__ == "__main__":
    pan_path = select_pan_image()
    if not pan_path:
        print("No file selected. Exiting.")
        exit()

    # Extract face and signature from the uploaded PAN card (image or pdf)
    pan_face, pan_sig = extract_pan_photo_signature(pan_path)

    # Capture live photo
    live_face = capture_live_photo()

    # Check sunglasses on live photo
    if check_sunglasses(live_face):
        print("Warning: Sunglasses detected in live photo. Face recognition accuracy may be affected.")

    # Compare faces
    face_match = compare_faces(pan_face, live_face)

    # Capture live signature
    live_sig = capture_live_signature()

    # Compare signatures
    sig_match = compare_signatures(pan_sig, live_sig)

    print("\n--- Verification Results ---")
    print(f"Face Match: {'Match' if face_match else 'Mismatch'}")
    print(f"Signature Match: {'Match' if sig_match else 'Mismatch'}")

    if face_match and sig_match:
        print("PAN verification successful!")
    else:
        print("PAN verification failed.")
