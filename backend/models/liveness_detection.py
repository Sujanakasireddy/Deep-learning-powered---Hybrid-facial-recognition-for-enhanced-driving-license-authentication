import cv2
import numpy as np
from scipy.spatial import distance as dist
import traceback
from pathlib import Path
from config import Config

class LivenessDetectionModel:
    """
    Liveness detection using Eye Aspect Ratio (EAR) for blink detection
    Optional: Requires dlib shape predictor file
    """
    
    def __init__(self):
        """Initialize liveness detector (optional)"""
        self.available = False
        
        if not Config.LIVENESS_ENABLED:
            print("⚠️ Liveness detection disabled in config")
            return
        
        try:
            import dlib
            
            self.detector = dlib.get_frontal_face_detector()
            
            # Check for shape predictor file
            predictor_path = "shape_predictor_68_face_landmarks.dat"
            
            if not Path(predictor_path).exists():
                print("⚠️ shape_predictor_68_face_landmarks.dat not found")
                print("   Download from: http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2")
                print("   Liveness detection will be disabled")
                return
            
            self.predictor = dlib.shape_predictor(predictor_path)
            
            # Eye landmarks indices (68-point facial landmarks)
            self.LEFT_EYE_POINTS = list(range(42, 48))
            self.RIGHT_EYE_POINTS = list(range(36, 42))
            
            # Thresholds from config
            self.EYE_AR_THRESH = Config.EYE_AR_THRESHOLD
            self.EYE_AR_CONSEC_FRAMES = Config.EYE_AR_CONSEC_FRAMES
            self.BLINK_THRESHOLD = Config.LIVENESS_BLINK_THRESHOLD
            
            self.blink_counter = 0
            self.total_blinks = 0
            self.available = True
            
            print("✅ LivenessDetectionModel initialized")
            print(f"   EAR Threshold: {self.EYE_AR_THRESH}")
            print(f"   Blink Threshold: {self.BLINK_THRESHOLD}")
            
        except ImportError:
            print("⚠️ dlib not installed, liveness detection disabled")
        except Exception as e:
            print(f"⚠️ Liveness detector initialization failed: {e}")
            traceback.print_exc()
    
    def eye_aspect_ratio(self, eye):
        """
        Calculate Eye Aspect Ratio (EAR)
        Formula: EAR = (||p2 - p6|| + ||p3 - p5||) / (2 * ||p1 - p4||)
        """
        # Vertical eye distances
        A = dist.euclidean(eye[1], eye[5])
        B = dist.euclidean(eye[2], eye[4])
        
        # Horizontal eye distance
        C = dist.euclidean(eye[0], eye[3])
        
        # Calculate EAR
        ear = (A + B) / (2.0 * C)
        return ear
    
    def detect_blinks(self, frame):
        """
        Detect blinks in a single video frame
        Returns: (total_blinks, blink_detected_in_frame)
        """
        if not self.available:
            return 0, False
        
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.detector(gray, 0)
            
            if len(faces) == 0:
                return self.total_blinks, False
            
            # Take first detected face
            face = faces[0]
            landmarks = self.predictor(gray, face)
            landmarks = self._shape_to_np(landmarks)
            
            # Extract eye coordinates
            left_eye = landmarks[self.LEFT_EYE_POINTS]
            right_eye = landmarks[self.RIGHT_EYE_POINTS]
            
            # Calculate EAR for both eyes
            left_ear = self.eye_aspect_ratio(left_eye)
            right_ear = self.eye_aspect_ratio(right_eye)
            
            # Average EAR
            ear = (left_ear + right_ear) / 2.0
            
            # Check for blink
            blink_detected = False
            if ear < self.EYE_AR_THRESH:
                self.blink_counter += 1
            else:
                # If eyes were closed for enough frames, count as blink
                if self.blink_counter >= self.EYE_AR_CONSEC_FRAMES:
                    self.total_blinks += 1
                    blink_detected = True
                self.blink_counter = 0
            
            return self.total_blinks, blink_detected
            
        except Exception as e:
            print(f"❌ Error detecting blinks: {e}")
            return self.total_blinks, False
    
    def check_liveness(self, video_frames):
        """
        Check liveness across multiple video frames
        Returns: dict with live status and confidence
        """
        if not self.available:
            print("⚠️ Liveness detection not available, returning default pass")
            return {
                "live": True,
                "confidence": 0.5,
                "blinks": 0,
                "note": "Liveness check disabled or unavailable"
            }
        
        try:
            print(f"🔄 Checking liveness across {len(video_frames)} frames...")
            
            # Reset counters
            self.blink_counter = 0
            self.total_blinks = 0
            
            # Process frames
            for i, frame in enumerate(video_frames):
                blinks, blink_detected = self.detect_blinks(frame)
                if blink_detected:
                    print(f"  👁️ Blink detected in frame {i}")
            
            print(f"📊 Total blinks detected: {self.total_blinks}")
            
            # Determine liveness based on blink count
            if self.total_blinks >= self.BLINK_THRESHOLD:
                confidence = min(self.total_blinks / 5.0, 1.0)
                return {
                    "live": True,
                    "confidence": confidence,
                    "blinks": self.total_blinks,
                    "note": "Sufficient blinks detected"
                }
            else:
                return {
                    "live": False,
                    "confidence": 0.3,
                    "blinks": self.total_blinks,
                    "note": f"Insufficient blinks (need {self.BLINK_THRESHOLD}, got {self.total_blinks})"
                }
                
        except Exception as e:
            print(f"❌ Error checking liveness: {e}")
            traceback.print_exc()
            # Return pass on error (graceful degradation)
            return {
                "live": True,
                "confidence": 0.5,
                "blinks": 0,
                "note": f"Error occurred: {str(e)}"
            }
    
    def _shape_to_np(self, shape, dtype="int"):
        """Convert dlib shape object to numpy array"""
        coords = np.zeros((68, 2), dtype=dtype)
        for i in range(0, 68):
            coords[i] = (shape.part(i).x, shape.part(i).y)
        return coords
