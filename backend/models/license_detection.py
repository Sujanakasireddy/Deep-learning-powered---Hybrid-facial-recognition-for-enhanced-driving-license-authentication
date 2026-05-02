import cv2
import numpy as np
import easyocr
import re
import ssl
import os
import traceback
from pathlib import Path


class LicenseDetectionModel:
    """
    License OCR pipeline using EasyOCR.

    Key improvements over the original:
      1. Rotation: tries all 4 cardinal rotations, picks the one that scores
         the most readable English tokens (avoids reliance on Tesseract OSD).
      2. DL Number regex: fixed to capture the full Indian DL number incl.
         the last digit that was previously dropped.
      3. DOB: uses "Date Of Birth" context label when available rather than
         blindly picking the first date in the document.
    """

    def __init__(self):
        self.reader = None
        self._rotation_angles = [0, 90, 180, 270]
        print("🔄 License detection model initialized (EasyOCR lazy-loaded)")

    # ── internal helpers ───────────────────────────────────────────────────

    def _load_ocr(self):
        if self.reader is None:
            print("🔄 Loading EasyOCR (first run may take ~30 s) …")
            try:
                ssl._create_default_https_context = ssl._create_unverified_context
                self.reader = easyocr.Reader(['en'], gpu=False, verbose=False)
                print("✅ EasyOCR ready")
            except Exception as e:
                print(f"❌ EasyOCR load failed: {e}")
                raise

    @staticmethod
    def _rotate(img, angle):
        if angle == 90:
            return cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
        elif angle == 180:
            return cv2.rotate(img, cv2.ROTATE_180)
        elif angle == 270:
            return cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
        return img

    def _best_rotation(self, img):
        """
        Try all 4 rotations using EasyOCR; return the rotation whose results
        contain the most high-confidence English tokens.
        This replaces the unreliable Tesseract OSD approach.
        """
        best_angle = 0
        best_score = -1
        best_results = None

        for angle in self._rotation_angles:
            rotated = self._rotate(img, angle)
            gray = self._preprocess_to_gray(rotated)
            try:
                results = self.reader.readtext(gray, detail=1)
            except Exception:
                continue

            # Score = sum of confidence for tokens that look like real words
            score = sum(
                conf
                for _, text, conf in results
                if conf > 0.4 and re.search(r'[A-Za-z]{2,}', text)
            )
            print(f"   Rotation {angle}°: score={score:.2f} ({len(results)} detections)")

            if score > best_score:
                best_score = score
                best_angle = angle
                best_results = results

        print(f"✅ Best rotation: {best_angle}°")
        return best_angle, best_results or []

    @staticmethod
    def _preprocess_to_gray(img):
        """Resize → CLAHE → denoise → adaptive threshold."""
        h, w = img.shape[:2]
        target_w = 1280
        img = cv2.resize(img, (target_w, int(h * target_w / w)))
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        gray = clahe.apply(gray)
        gray = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
        binary = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
        return binary

    # ── public API ─────────────────────────────────────────────────────────

    def extract_license_info(self, image_path):
        """
        Main entry point.
        Returns:
          {
            "success": bool,
            "extracted_data": {
              "license_number": str | None,
              "name": str | None,
              "dob": str | None,
              "address": str | None,
              "tokens": list[dict]
            },
            "raw_text": str
          }
        """
        try:
            self._load_ocr()
            print(f"🔄 Extracting license info from: {image_path}")

            img = cv2.imread(str(image_path))
            if img is None:
                raise ValueError(f"Cannot load image: {image_path}")

            # Find best rotation and get first-pass OCR results
            best_angle, results_rotated = self._best_rotation(img)

            # Also run OCR on the colour (non-binarised) rotation for richer output
            best_img = self._rotate(img, best_angle)
            h, w = best_img.shape[:2]
            best_img_resized = cv2.resize(best_img, (1280, int(h * 1280 / w)))
            results_color = self.reader.readtext(best_img_resized, detail=1)

            # Merge: grey (preprocessed) + colour passes
            all_results = results_rotated + results_color
            tokens_filtered = [
                (text, conf) for _, text, conf in all_results if conf > 0.25
            ]

            full_text = " ".join(t for t, _ in tokens_filtered)
            print(f"📄 Combined OCR text (first 300 chars): {full_text[:300]}")

            extracted = self._parse(full_text, tokens_filtered)

            return {
                "success": True,
                "extracted_data": extracted,
                "raw_text": full_text
            }

        except Exception as e:
            print(f"❌ OCR error: {e}")
            traceback.print_exc()
            return {
                "success": False,
                "error": str(e),
                "extracted_data": {}
            }

    def _parse(self, full_text: str, tokens: list) -> dict:
        """
        Parse OCR output into structured fields.
        Handles two licence styles:
          A) Newer digital format — fields are labelled (Name:, Date Of Birth:, …)
          B) Older physical format — no field labels; heuristics only
        """
        data = {
            "license_number": None,
            "name": None,
            "dob": None,
            "address": None,
            "tokens": [
                {"text": t.upper().strip(), "conf": c}
                for t, c in tokens if c > 0.4
            ],
        }

        upper = full_text.upper()

        # ── DL Number ──────────────────────────────────────────────────────
        # Strip ALL non-alphanumeric characters first to handle OCR noise like
        # spaces, hyphens, commas, quotes inserted inside the DL number.
        # Then search for the standard Indian DL pattern.
        dl_patterns = [
            # Strict: 2 letters + exactly 13 digits (most common Indian DL)
            r'([A-Z]{2}\d{13})',
            # Medium: 2 letters + 10-15 digits
            r'([A-Z]{2}\d{10,15})',
        ]
        # Strip everything except letters and digits
        alphanum_upper = re.sub(r'[^A-Z0-9]', '', upper)
        for pat in dl_patterns:
            m = re.search(pat, alphanum_upper)
            if m:
                candidate = m.group(1)
                digits = len(re.findall(r'\d', candidate))
                if digits >= 10:
                    data["license_number"] = candidate
                    print(f"✅ DL Number: {candidate}")
                    break

        if not data["license_number"]:
            print("⚠️ DL number extraction failed")

        # ── Date of Birth ──────────────────────────────────────────────────
        # Strategy 1: look for context label "DATE OF BIRTH" or "DOB"
        dob_context = re.search(
            r'(?:DATE\s+OF\s+BIRTH|DOB)[:\s]*(\d{2}[\/\-]\d{2}[\/\-]\d{4})',
            upper
        )
        if dob_context:
            data["dob"] = dob_context.group(1).replace('/', '-')
            print(f"✅ DOB (context): {data['dob']}")
        else:
            # Strategy 2: collect ALL dates, prefer ones that look like a birth year
            all_dates = re.findall(r'\b(\d{2}[\/\-]\d{2}[\/\-]\d{4})\b', full_text)
            birth_dates = []
            for d in all_dates:
                year_m = re.search(r'\d{4}', d)
                if year_m:
                    year = int(year_m.group())
                    if 1940 <= year <= 2010:   # plausible birth year range
                        birth_dates.append(d.replace('/', '-'))
            if birth_dates:
                data["dob"] = birth_dates[0]
                print(f"✅ DOB (year heuristic): {data['dob']}")
            elif all_dates:
                data["dob"] = all_dates[0].replace('/', '-')
                print(f"⚠️ DOB (first date fallback): {data['dob']}")

        # ── Name ───────────────────────────────────────────────────────────
        # Strategy 1: labelled field "NAME :" or "NAME :"
        # Accepts name that immediately follows 'Name :' label (digital DL format)
        name_context = re.search(
            r'NAME\s*:?\s*([A-Z][A-Z\s]{3,50}?)(?:\s{2,}|\n|$)',
            upper
        )
        if name_context:
            raw_name = name_context.group(1).strip()
            # Reject if it looks like a relationship label (Son/Daughter/Wife of)
            if not re.search(r'(SON|DAUGHTER|WIFE|HUSBAND|OF)', raw_name):
                data["name"] = raw_name
                print(f"✅ Name (context label): {data['name']}")

        if not data["name"]:
            # Strategy 2: highest-confidence multi-word token that is not a keyword
            excluded = {
                'UNION', 'INDIA', 'INDIAN', 'STATE', 'DRIVING', 'LICENCE',
                'LICENSE', 'TRANSPORT', 'AUTHORITY', 'DATE', 'ISSUE', 'ISSUED',
                'BLOOD', 'GROUP', 'ADDRESS', 'ANDHRA', 'PRADESH',
                'RTA', 'LICENCING', 'LICENSING', 'VALIDITY', 'VEHICLE',
                'CATEGORY', 'HAZARDOUS', 'HILL', 'HOLDER', 'SIGNATURE',
                'ORGAN', 'DONOR', 'AADHAAR', 'AP', 'NT', 'TR',
                'SON', 'DAUGHTER', 'WIFE', 'HUSBAND', 'SONDAUGHTERWIFE',
                'SONDAUGHTERWWIFE',
            }
            candidates = []
            for t, c in tokens:
                clean = re.sub(r'[^A-Z\s]', '', t.upper()).strip()
                words = [w for w in clean.split() if len(w) > 2 and w not in excluded]
                if len(words) >= 2 and c > 0.40:
                    candidates.append((' '.join(words), c))
            # Sort by confidence descending (prefer high-confidence short clean name)
            candidates.sort(key=lambda x: x[1], reverse=True)
            if candidates:
                data["name"] = candidates[0][0]
                print(f"✅ Name (heuristic): {data['name']}")

        return data
