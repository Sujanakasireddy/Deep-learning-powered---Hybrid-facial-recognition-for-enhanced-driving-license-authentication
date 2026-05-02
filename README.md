# 🚗 Deep Learning Powered Hybrid Facial Recognition for Enhanced Driver’s License Authentication## 📌 OverviewThis project is a **full-stack biometric authentication system** that uses **deep learning-based facial recognition combined with driver’s license verification** to enhance identity validation.The system ensures secure and accurate user authentication by matching:- Face image (deep learning embeddings)- Driver’s license data (OCR / structured fields)- Hybrid scoring mechanism for final verification decisionIt is designed for **real-world identity verification use cases** such as transport systems, driving license validation, and secure onboarding systems.---## 🎯 Features### 👤 User Registration- Register user with:  - User ID  - Full Name  - Date of Birth  - Address  - Driver’s License Number  - Face image (biometric embedding generation)- Stores face embeddings in backend database### 🔍 Identity Verification- Supports two modes:  - Face + License Verification  - Face-only Verification- Compares uploaded face with stored embeddings- Validates license details- Generates final weighted score### 🧠 Deep Learning Model- Face feature extraction using pretrained deep learning model- Embedding-based similarity matching- Confidence scoring system### 📊 Hybrid Decision SystemFinal verification depends on:- Face similarity score- Name/token matching- License number validation- Weighted scoring logic---## 🏗️ Tech Stack### Frontend- React.js (Vite)- Bootstrap 5- Axios- React Router### Backend- Python / Flask (or Node.js depending on implementation)- OpenCV / Face Recognition / Deep Learning Model- REST API architecture### Database- MySQL / MongoDB (based on setup)---## 📁 Project Structure
project-root/
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── App.jsx
│   │   └── LandingPage.jsx
│   └── .env
│
├── backend/
│   ├── app.py / server.js
│   ├── routes/
│   ├── models/
│   └── database/
│
└── README.md
---## ⚙️ Environment Variables### Frontend (.env)
VITE_API_URL=http://localhost:5001
### Backend (.env)
PORT=5001
DATABASE_URL=your_database_url
MODEL_PATH=your_model_path
---## 🚀 Installation & Setup### 1️⃣ Clone Repository```bashgit clone https://github.com/your-username/face-license-auth.gitcd face-license-auth

2️⃣ Backend Setup
cd backend pip install -r requirements.txt python app.py

3️⃣ Frontend Setup
cd frontend  npm install  npm run dev

🔗 API Endpoints
🔹 Register User
POST /api/register
🔹 Verify Identity
POST /api/verify
🔹 Face Only Verification
POST /api/verify-face-only
🔹 Get User Face Image
GET /api/users/{user_id}/face

📊 Verification Logic
The system calculates a final score:
Final Score =  (Face Similarity × 0.5) +  (Name Match Score × 0.3) +  (License Match Bonus × 0.2)
Decision Rule:


Score ≥ Threshold → VERIFIED


Score < Threshold → NOT VERIFIED



🧪 Output Example
✅ Verified
Status: VERIFIEDFace Score: 87.5License Match: YESFinal Score: 92/100
❌ Not Verified
Status: NOT VERIFIEDFace Score: 45.2License Match: NOFinal Score: 38/100

🖥️ UI Features


Camera capture support


Image preview before submission


Verification result modal


Confidence bar visualization


Responsive UI design



📌 Future Improvements


Liveness detection (anti-spoofing)


Aadhaar / national ID integration


Cloud deployment (AWS / Azure)


Real-time video verification


Multi-face detection handling



👨‍💻 Author
Developed as a Final Year Full Stack + AI Project

This project is my academic project
