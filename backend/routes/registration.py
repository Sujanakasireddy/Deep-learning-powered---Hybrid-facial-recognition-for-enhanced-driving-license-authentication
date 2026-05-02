from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os
import traceback
import re
from datetime import datetime

from config import Config
from models.face_recognition import FaceRecognitionModel
from database import (
    store_face_embedding, 
    store_license_record, 
    user_exists
)

registration_bp = Blueprint('registration', __name__)
face_model = FaceRecognitionModel()


# ========== VALIDATION FUNCTIONS ==========

def validate_user_id(user_id):
    return re.match(r'^[A-Za-z0-9_]{4,20}$', str(user_id))

def validate_full_name(name):
    return re.match(r'^[A-Za-z ]{3,}$', str(name))

def validate_license(license_no):
    return re.match(r'^[A-Z]{2}[0-9A-Z]{8,16}$', str(license_no))

def validate_dob(dob):
    try:
        birth_date = datetime.strptime(dob, "%Y-%m-%d")
        age = (datetime.today() - birth_date).days // 365
        return age >= 18
    except:
        return False

def validate_address(address):
    return len(str(address).strip()) >= 10


# ✅ FIXED IMAGE VALIDATION
def validate_image(file, source="upload"):
    if not file:
        return "Face image is required"

    allowed_extensions = ['jpg', 'jpeg', 'png']
    filename = file.filename.lower()

    if '.' not in filename:
        return "Invalid file"

    ext = filename.split('.')[-1]

    if ext not in allowed_extensions:
        return "Only JPG/PNG allowed"

    # ✅ FIXED SIZE VALIDATION (2MB max)
    file.seek(0, 2)
    size = file.tell()
    file.seek(0)

    if size > 2 * 1024 * 1024:
        return "Image must be less than 2MB"

    return "Valid"


# ========== REGISTER USER ==========

@registration_bp.route('/register', methods=['POST'])
def register_user_endpoint():
    try:
        # ===== GET DATA =====
        user_id = request.form.get('user_id')
        name = request.form.get('name')
        license_number = request.form.get('license_number')
        dob = request.form.get('dob')
        address = request.form.get('address')
        face_image = request.files.get('face_image')

        # ✅ detect source
        source = request.form.get('source', 'upload')

        # ===== EMPTY CHECK =====
        if not all([user_id, name, license_number, dob, address, face_image]):
            return jsonify({
                "success": False,
                "message": "All fields are required"
            }), 400

        # ===== VALIDATIONS =====
        if not validate_user_id(user_id):
            return jsonify({"success": False, "message": "Invalid User ID"}), 400

        if not validate_full_name(name):
            return jsonify({"success": False, "message": "Invalid Name"}), 400

        if not validate_license(license_number):
            return jsonify({"success": False, "message": "Invalid License Number"}), 400

        if not validate_dob(dob):
            return jsonify({"success": False, "message": "User must be 18+"}), 400

        if not validate_address(address):
            return jsonify({"success": False, "message": "Address too short"}), 400

        # ✅ IMAGE VALIDATION
        img_check = validate_image(face_image, source)
        if img_check != "Valid":
            return jsonify({
                "success": False,
                "message": img_check
            }), 400

        # ===== CHECK USER =====
        if user_exists(user_id):
            return jsonify({
                "success": False,
                "message": f"User '{user_id}' already exists"
            }), 400

        # ===== SAVE IMAGE =====
        face_filename = secure_filename(f'{user_id}_face.jpg')
        face_path = os.path.join(Config.UPLOAD_FOLDER, face_filename)
        face_image.save(face_path)

        # ===== FACE EMBEDDING =====
        embedding = face_model.extract_embedding(face_path)

        if embedding is None:
            os.remove(face_path)
            return jsonify({
                "success": False,
                "message": "No face detected"
            }), 400

        # ===== DUPLICATE FACE =====
        duplicate_user, _ = face_model.find_duplicate_face(embedding)

        if duplicate_user:
            os.remove(face_path)
            return jsonify({
                "success": False,
                "message": f"Face already registered as '{duplicate_user}'"
            }), 409

        # ===== STORE =====
        store_face_embedding(
            user_id,
            embedding if isinstance(embedding, list) else embedding.tolist(),
            model_name='OpenCV-Custom'
        )

        store_license_record(user_id, {
            "name": name,
            "license_number": license_number,
            "dob": dob,
            "address": address
        })

        return jsonify({
            "success": True,
            "message": "User registered successfully",
            "user_id": user_id
        }), 201

    except Exception as e:
        traceback.print_exc()
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500