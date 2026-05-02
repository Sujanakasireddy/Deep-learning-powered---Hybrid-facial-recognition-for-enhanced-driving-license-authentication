"""
Image preprocessing utilities
Based on research paper preprocessing techniques
"""

import cv2
import numpy as np

def histogram_equalization(image):
    """
    Apply histogram equalization for better contrast
    Based on research paper preprocessing step
    """
    if len(image.shape) == 3:
        # Convert to YUV
        yuv = cv2.cvtColor(image, cv2.COLOR_BGR2YUV)
        # Equalize the Y channel
        yuv[:, :, 0] = cv2.equalizeHist(yuv[:, :, 0])
        # Convert back to BGR
        return cv2.cvtColor(yuv, cv2.COLOR_YUV2BGR)
    else:
        # Grayscale image
        return cv2.equalizeHist(image)

def adaptive_gaussian_threshold(image):
    """
    Apply adaptive Gaussian thresholding
    """
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image
    
    return cv2.adaptiveThreshold(
        gray,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        11,
        2
    )

def denoise_image(image, strength=10):
    """
    Remove noise from image
    """
    if len(image.shape) == 3:
        return cv2.fastNlMeansDenoisingColored(image, None, strength, strength, 7, 21)
    else:
        return cv2.fastNlMeansDenoising(image, None, strength, 7, 21)

def resize_image(image, max_width=800):
    """
    Resize image to standard size for consistent processing
    """
    height, width = image.shape[:2]
    
    if width > max_width:
        scale = max_width / width
        new_width = int(width * scale)
        new_height = int(height * scale)
        return cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
    
    return image

def detect_and_align_face(image):
    """
    Detect face and align for better recognition
    Returns: aligned face image or None
    """
    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    )
    
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    
    if len(faces) > 0:
        # Take the largest face
        x, y, w, h = max(faces, key=lambda rect: rect[2] * rect[3])
        # Add padding
        padding = int(0.2 * w)
        x = max(0, x - padding)
        y = max(0, y - padding)
        w = min(image.shape[1] - x, w + 2 * padding)
        h = min(image.shape[0] - y, h + 2 * padding)
        
        return image[y:y+h, x:x+w]
    
    return None

def sharpen_image(image):
    """
    Sharpen image for better detail visibility
    """
    kernel = np.array([[-1, -1, -1],
                       [-1,  9, -1],
                       [-1, -1, -1]])
    return cv2.filter2D(image, -1, kernel)

def correct_skew(image):
    """
    Correct skew in document images (license cards)
    """
    # Convert to grayscale
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image
    
    # Threshold
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    
    # Find contours
    coords = np.column_stack(np.where(thresh > 0))
    
    if len(coords) == 0:
        return image
    
    # Calculate angle
    angle = cv2.minAreaRect(coords)[-1]
    
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle
    
    # Rotate image
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(
        image, M, (w, h),
        flags=cv2.INTER_CUBIC,
        borderMode=cv2.BORDER_REPLICATE
    )
    
    return rotated
