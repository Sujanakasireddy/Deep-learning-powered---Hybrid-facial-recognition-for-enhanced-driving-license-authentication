"""
License OCR utility functions
Additional helper functions for license processing
"""

import re
import cv2
import numpy as np

def validate_license_number(license_number):
    """
    Validate license number format
    Returns: (is_valid, normalized_number)
    """
    if not license_number:
        return False, None
    
    # Remove spaces and convert to uppercase
    normalized = license_number.upper().replace(' ', '-')
    
    # Common patterns for Indian driving licenses
    patterns = [
        r'^[A-Z]{2}[-]?\d{13,16}$',      # DL-1420110012345
        r'^[A-Z]{2}\d{2}[-]?\d{11}$',    # DL14-20110012345
        r'^[A-Z]{2}[-]?\d{2}[-]?\d{11}$' # DL-14-20110012345
    ]
    
    for pattern in patterns:
        if re.match(pattern, normalized):
            return True, normalized
    
    return False, normalized

def parse_dob(dob_string):
    """
    Parse date of birth from various formats
    Returns: standardized date string (DD/MM/YYYY)
    """
    if not dob_string:
        return None
    
    # Common separators
    for sep in ['/', '-', '.']:
        if sep in dob_string:
            parts = dob_string.split(sep)
            if len(parts) == 3:
                day, month, year = parts
                # Ensure 2-digit day/month, 4-digit year
                if len(year) == 2:
                    year = '19' + year if int(year) > 25 else '20' + year
                return f"{day.zfill(2)}/{month.zfill(2)}/{year}"
    
    return dob_string

def extract_name_from_text(text):
    """
    Extract name from OCR text using pattern matching
    Returns: extracted name or None
    """
    # Look for common name patterns
    name_pattern = r'[A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3}'
    matches = re.findall(name_pattern, text)
    
    # Filter out common keywords
    keywords = ['License', 'Driver', 'Drivers', 'Address', 'Date', 
                'Birth', 'Number', 'India', 'Name', 'Issue', 'Valid']
    
    valid_names = []
    for match in matches:
        if not any(keyword in match for keyword in keywords):
            valid_names.append(match)
    
    if valid_names:
        # Return the longest match (likely full name)
        return max(valid_names, key=len)
    
    return None

def preprocess_for_ocr(image):
    """
    Advanced preprocessing for better OCR accuracy
    Returns: preprocessed image
    """
    # Convert to grayscale
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()
    
    # Denoise
    denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
    
    # Adaptive thresholding
    thresh = cv2.adaptiveThreshold(
        denoised,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        11,
        2
    )
    
    # Morphological operations to clean up
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    morph = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    
    return morph

def enhance_license_image(image_path):
    """
    Enhance license image quality for better OCR
    Returns: enhanced image (numpy array)
    """
    img = cv2.imread(image_path)
    if img is None:
        return None
    
    # Resize if too large
    height, width = img.shape[:2]
    if width > 1000:
        scale = 1000 / width
        img = cv2.resize(img, None, fx=scale, fy=scale)
    
    # Enhance contrast
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    l = clahe.apply(l)
    enhanced = cv2.merge([l, a, b])
    enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)
    
    return enhanced
