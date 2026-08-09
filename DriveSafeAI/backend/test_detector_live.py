import cv2
import time
import mediapipe as mp
import numpy as np
from detection.eye_detection import EyeDetector
from detection.head_pose import HeadPoseDetector
from detection.yawn_detection import YawnDetector

print("Initializing detectors...")
eye_det = EyeDetector()
head_det = HeadPoseDetector()
yawn_det = YawnDetector()

print("Opening webcam (camera index 0)...")
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("❌ Webcam could not be opened directly via OpenCV (camera in use by browser).")
    print("Testing with a blank / sample RGB frame instead...")
    sample_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    # Draw simple facial features
    cv2.circle(sample_frame, (320, 240), 100, (200, 200, 200), -1)
    rgb = cv2.cvtColor(sample_frame, cv2.COLOR_BGR2RGB)
    mp_res = eye_det._face_mesh.process(rgb)
    landmarks = mp_res.multi_face_landmarks[0].landmark if mp_res.multi_face_landmarks else None
    print(f"Face mesh result on sample frame: {landmarks is not None}")
    eye_res = eye_det.detect(sample_frame, face_landmarks=landmarks)
    head_res = head_det.detect(sample_frame, face_landmarks=landmarks)
    yawn_res = yawn_det.detect(sample_frame, face_landmarks=landmarks)
    print("Eye result:", eye_res)
    print("Head result:", head_res)
    print("Yawn result:", yawn_res)
else:
    print("[SUCCESS] Webcam opened successfully! Reading 5 test frames...")
    for i in range(5):
        ret, frame = cap.read()
        if not ret:
            print(f"Frame {i+1} read failed.")
            continue
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_res = eye_det._face_mesh.process(rgb)
        landmarks = mp_res.multi_face_landmarks[0].landmark if mp_res.multi_face_landmarks else None
        
        eye_res = eye_det.detect(frame, face_landmarks=landmarks)
        head_res = head_det.detect(frame, face_landmarks=landmarks)
        yawn_res = yawn_det.detect(frame, face_landmarks=landmarks)
        
        print(f"\n--- Frame {i+1} ---")
        print(f"Face Detected: {landmarks is not None}")
        print(f"Eye Status   : {eye_res.get('eye_status')} (Confidence: {eye_res.get('confidence'):.2f})")
        print(f"Head Pose    : {head_res.get('direction')} (Yaw: {head_res.get('yaw'):.1f}, Pitch: {head_res.get('pitch'):.1f})")
        print(f"MAR (Yawn)   : {yawn_res.get('mar')} (Is Yawning: {yawn_res.get('is_yawning')})")
        time.sleep(0.3)
    cap.release()
print("\nTest completed successfully!")
