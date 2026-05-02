import cv2
import numpy as np
import os
import traceback
from config import Config
from database import store_face_embedding, get_all_face_embeddings

class FaceRecognitionModel:
    """
    Simple and reliable face recognition using OpenCV
    No TensorFlow, no DeepFace, no compilation needed!
    Perfect for Apple Silicon Macs
    """
    
    def __init__(self):
        # Load OpenCV's pre-trained face detector
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        
        # Load eye detector for better accuracy
        self.eye_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_eye.xml'
        )
        
        self.threshold = Config.FACE_SIMILARITY_THRESHOLD
        
        print(f"✅ FaceRecognitionModel initialized")
        print(f"   Method: OpenCV Haar Cascades")
        print(f"   Similarity Threshold: {self.threshold}")
        
    def extract_embedding(self, image_path):
        """
        Extract face features using OpenCV
        Returns: embedding vector (10,000-dimensional) or None
        """
        try:
            print(f"🔄 Extracting face embedding from: {image_path}")
            
            if not os.path.exists(image_path):
                print(f"❌ Image file not found: {image_path}")
                return None
            
            # Read image
            img = cv2.imread(image_path)
            if img is None:
                print(f"❌ Cannot read image: {image_path}")
                return None
            
            # Convert to grayscale for better face detection
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Detect faces with different scale factors for better accuracy
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30)
            )
            
            if len(faces) == 0:
                print(f"❌ No face detected in image")
                return None
            
            print(f"✅ Detected {len(faces)} face(s)")
            
            # Take the largest face (likely the main subject)
            faces_sorted = sorted(faces, key=lambda x: x[2] * x[3], reverse=True)
            (x, y, w, h) = faces_sorted[0]
            
            # Extract face region
            face_img = gray[y:y+h, x:x+w]
            
            # Verify it's a real face by detecting eyes
            eyes = self.eye_cascade.detectMultiScale(face_img)
            if len(eyes) < 1:
                print(f"⚠️ Warning: No eyes detected, but continuing...")
            else:
                print(f"✅ Verified face with {len(eyes)} eye(s) detected")
            
            # Resize to standard size for consistent embeddings
            face_img_resized = cv2.resize(face_img, (100, 100))
            
            # Apply histogram equalization for better lighting consistency
            face_img_normalized = cv2.equalizeHist(face_img_resized)
            
            # Flatten to 1D array (our "embedding")
            embedding = face_img_normalized.flatten().tolist()
            
            print(f"✅ Embedding extracted successfully (dimension: {len(embedding)})")
            return embedding
            
        except Exception as e:
            print(f"❌ Error extracting embedding: {e}")
            traceback.print_exc()
            return None
    
    def register_face(self, user_id, image_path):
        """
        Register a new face in the database
        Returns: dict with success status and message
        """
        try:
            print(f"🔄 Registering face for user: {user_id}")
            
            # Extract face embedding
            embedding = self.extract_embedding(image_path)
            if embedding is None:
                return {
                    "success": False, 
                    "message": "No face detected in the image"
                }
            
            # Store in database
            store_face_embedding(user_id, embedding, "opencv-haar")
            
            print(f"✅ Face registered for user: {user_id}")
            return {
                "success": True,
                "user_id": user_id,
                "embedding_dimension": len(embedding)
            }
            
        except Exception as e:
            print(f"❌ Error registering face: {e}")
            traceback.print_exc()
            return {
                "success": False,
                "message": str(e)
            }

    def find_duplicate_face(self, embedding):
        """
        Check if an embedding already exists in the database.
        Returns: (matched_user_id, similarity) or (None, 0) if no duplicate found.
        """
        all_embeddings = get_all_face_embeddings()
        if not all_embeddings:
            return None, 0.0

        uploaded_np = np.array(embedding)
        best_user = None
        best_sim = 0.0

        for user_id, stored_embedding in all_embeddings:
            stored_np = np.array(stored_embedding)
            cosine_sim = self._cosine_similarity(uploaded_np, stored_np)
            correlation = np.corrcoef(uploaded_np, stored_np)[0, 1]
            similarity = (cosine_sim + correlation) / 2

            if similarity > best_sim:
                best_sim = similarity
                best_user = user_id

        # Duplicate detection should require very high similarity to prevent false lockouts
        # Raw pixel cosine similarity averages very high baseline (~0.7).
        duplicate_threshold = 0.90 
        if best_sim > duplicate_threshold:
            return best_user, float(best_sim)
        return None, float(best_sim)

    def verify_face(self, uploaded_image_path):
        """
        Verify uploaded face against all registered faces
        Returns: dict with best match user_id and confidence score
        """
        try:
            print(f"🔄 Verifying face from: {uploaded_image_path}")
            
            # Extract embedding from uploaded image
            uploaded_embedding = self.extract_embedding(uploaded_image_path)
            if uploaded_embedding is None:
                return {
                    "success": False,
                    "message": "No face detected in uploaded image"
                }
            
            # Get all registered embeddings from database
            all_embeddings = get_all_face_embeddings()
            
            if len(all_embeddings) == 0:
                return {
                    "success": False,
                    "message": "No registered users in database"
                }
            
            # Find best match using multiple similarity metrics
            best_match = None
            highest_similarity = 0
            
            print(f"📊 Comparing with {len(all_embeddings)} registered users...")
            
            uploaded_np = np.array(uploaded_embedding)
            
            for user_id, stored_embedding in all_embeddings:
                stored_np = np.array(stored_embedding)
                
                # Cosine similarity
                cosine_sim = self._cosine_similarity(uploaded_np, stored_np)
                
                # Normalized correlation
                correlation = np.corrcoef(uploaded_np, stored_np)[0, 1]
                
                # Average both metrics
                similarity = (cosine_sim + correlation) / 2
                
                print(f"   User {user_id}: similarity = {similarity:.4f} "
                      f"(cosine: {cosine_sim:.4f}, corr: {correlation:.4f})")
                
                # Check if similarity is higher and above threshold (raised to 0.75 for stricter security)
                verify_threshold = 0.75
                if similarity > highest_similarity and similarity > verify_threshold:
                    highest_similarity = similarity
                    best_match = user_id
            
            # Return result
            if best_match:
                distance = 1 - highest_similarity
                print(f"✅ Face matched! User: {best_match}, Confidence: {highest_similarity:.4f}")
                return {
                    "success": True,
                    "user_id": best_match,
                    "confidence": float(highest_similarity),
                    "distance": float(distance)
                }
            else:
                print(f"❌ No matching face found (best score: {highest_similarity:.4f})")
                return {
                    "success": False,
                    "message": f"No matching face found (best similarity: {highest_similarity:.4f}, threshold: {1 - self.threshold:.4f})",
                    "best_similarity": float(highest_similarity)
                }
                
        except Exception as e:
            print(f"❌ Error verifying face: {e}")
            traceback.print_exc()
            return {
                "success": False,
                "message": str(e)
            }
    
    def _cosine_similarity(self, vec1, vec2):
        """
        Calculate cosine similarity between two vectors
        Returns: similarity score (0 to 1, higher is more similar)
        """
        vec1 = np.array(vec1, dtype=np.float64)
        vec2 = np.array(vec2, dtype=np.float64)
        
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
            
        similarity = dot_product / (norm1 * norm2)
        return float(similarity)
