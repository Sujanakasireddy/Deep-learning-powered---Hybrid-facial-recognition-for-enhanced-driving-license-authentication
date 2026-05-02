import React, { useState } from 'react';
import { Routes, Route, useNavigate } from 'react-router-dom';
import axios from 'axios';
import CameraCapture from './components/CameraCapture';
import LandingPage from './LandingPage';
import 'bootstrap/dist/css/bootstrap.min.css';
import './App.css';

// Verification Result Modal Component
const VerificationResultModal = ({ result, onClose, verificationType }) => {
  if (!result) return null;

  const isSuccess = result.decision === "VERIFIED" || result.status === "verified";

  const faceScore = result.face_score !== undefined ? result.face_score.toFixed(1) : null;
  const nameMatchScore = result.name_match_score !== undefined ? result.name_match_score.toFixed(1) : null;
  const finalScore = result.final_score !== undefined ? result.final_score.toFixed(1) : null;
  const dlMatch = result.dl_match;

  const getConfidenceClass = (value) => {
    if (value >= 80) return 'high';
    if (value >= 60) return 'medium';
    return 'low';
  };

  if (isSuccess) {
    return (
      <div className="verification-modal-overlay" onClick={onClose}>
        <div className="verification-modal-content" onClick={e => e.stopPropagation()}>
          {/* Animated Checkmark */}
          <div className="verified-icon-container">
            <svg className="verified-checkmark" viewBox="0 0 52 52">
              <path d="M14 27l10 10 14-20" />
            </svg>
          </div>

          {/* Title */}
          <h2 className="verified-title">Verified</h2>
          <p className="verified-subtitle">
            {verificationType === 'face_license'
              ? 'Identity successfully verified with Face & License'
              : 'Face successfully verified'}
          </p>

          {/* User Info Section */}
          {(result.user_id || result.user?.name || result.details?.name || result.user_data?.name) && (
            <div className="user-info-section">
              {/* Display User Image */}
              {result.user_id && (
                <img
                  src={`http://localhost:5001/api/users/${result.user_id}/face`}
                  alt="Verified User"
                  className="verified-user-image"
                  onError={(e) => { e.target.style.display = 'none'; }}
                />
              )}

              {result.user_id && (
                <div className="user-info-row">
                  <span className="user-info-label">User ID</span>
                  <span className="user-info-value">{result.user_id}</span>
                </div>
              )}
              {(result.user?.name || result.details?.name || result.user_data?.name) && (
                <div className="user-info-row">
                  <span className="user-info-label">Name</span>
                  <span className="user-info-value">{result.user?.name || result.details?.name || result.user_data?.name}</span>
                </div>
              )}
              {(result.user?.license_number || result.details?.license_number || result.user_data?.license_number) && (
                <div className="user-info-row">
                  <span className="user-info-label">License #</span>
                  <span className="user-info-value">{result.user?.license_number || result.details?.license_number || result.user_data?.license_number}</span>
                </div>
              )}
              {(result.user?.dob || result.details?.dob || result.user_data?.dob) && (
                <div className="user-info-row">
                  <span className="user-info-label">DOB</span>
                  <span className="user-info-value">{result.user?.dob || result.details?.dob || result.user_data?.dob}</span>
                </div>
              )}
              {(result.user?.address || result.details?.address || result.user_data?.address) && (
                <div className="user-info-row" style={{ flexDirection: 'column', alignItems: 'flex-start' }}>
                  <span className="user-info-label" style={{ marginBottom: '4px' }}>Address</span>
                  <span className="user-info-value" style={{ textAlign: 'left', fontSize: '0.9rem' }}>
                    {result.user?.address || result.details?.address || result.user_data?.address}
                  </span>
                </div>
              )}
            </div>
          )}

          {/* Stats Grid */}
          <div className="verification-stats">
            {faceScore && (
              <div className="stat-item">
                <div className="stat-label">Face Score</div>
                <div className={`stat-value ${parseFloat(faceScore) >= 80 ? 'highlight' : ''}`}>
                  {faceScore}
                </div>
                <div className="confidence-bar-container">
                  <div className="confidence-bar">
                    <div
                      className={`confidence-bar-fill ${getConfidenceClass(parseFloat(faceScore))}`}
                      style={{ width: `${Math.min(faceScore, 100)}%` }}
                    />
                  </div>
                </div>
              </div>
            )}

            {nameMatchScore !== null && (
              <div className="stat-item">
                <div className="stat-label">Name Token Match</div>
                <div className={`stat-value ${parseFloat(nameMatchScore) >= 60 ? 'highlight' : ''}`}>
                  {nameMatchScore}%
                </div>
                <div className="confidence-bar-container">
                  <div className="confidence-bar">
                    <div
                      className={`confidence-bar-fill ${getConfidenceClass(parseFloat(nameMatchScore))}`}
                      style={{ width: `${nameMatchScore}%` }}
                    />
                  </div>
                </div>
              </div>
            )}

            {dlMatch !== undefined && (
              <div className="stat-item">
                <div className="stat-label">DL Number Match</div>
                <div className={`stat-value ${dlMatch ? 'highlight' : 'low'}`} style={{ fontSize: '1.2rem', color: dlMatch ? '#4CAF50' : '#f44336' }}>
                  {dlMatch ? 'Matched (+40)' : 'Miss'}
                </div>
              </div>
            )}

            {finalScore !== null && (
              <div className="stat-item" style={{ gridColumn: '1 / -1', background: 'rgba(0,0,0,0.02)', padding: '15px', borderRadius: '8px' }}>
                <div className="stat-label" style={{ fontWeight: 'bold' }}>Final Weighted Score (Threshold: 70)</div>
                <div className={`stat-value ${parseFloat(finalScore) >= 70 ? 'highlight' : 'low'}`} style={{ fontSize: '1.8rem' }}>
                  {finalScore}/140
                </div>
              </div>
            )}

            {result.verification_method && (
              <div className="stat-item" style={{ gridColumn: '1 / -1' }}>
                <div className="stat-label">Method</div>
                <div className="stat-value" style={{ fontSize: '1rem' }}>
                  {result.verification_method}
                </div>
              </div>
            )}
          </div>

          {/* Close Button */}
          <button className="modal-close-btn" onClick={onClose}>
            Continue
          </button>
        </div>
      </div>
    );
  }

  // Failed verification - show error modal
  return (
    <div className="verification-modal-overlay" onClick={onClose}>
      <div className="verification-modal-content failed" onClick={e => e.stopPropagation()}>
        <div className="failed-icon-container">
          <svg width="60" height="60" viewBox="0 0 52 52" stroke="white" strokeWidth="4" fill="none">
            <path d="M16 16 L36 36 M36 16 L16 36" />
          </svg>
        </div>

        <h2 className="failed-title">Not Verified</h2>
        <p className="verified-subtitle">
          {result.message || 'Verification failed. Please try again.'}
        </p>

        <button className="modal-close-btn" onClick={onClose}>
          Try Again
        </button>
      </div>
    </div>
  );
};


// Image Compression Function (ADD ABOVE COMPONENT)
const compressImage = (file, maxWidth = 800, quality = 0.7) => {
  return new Promise((resolve) => {
    const img = new Image();
    const reader = new FileReader();

    reader.onload = (e) => {
      img.src = e.target.result;
    };

    reader.onloadend = () => {
      img.onload = () => {
        const canvas = document.createElement("canvas");
        let width = img.width;
        let height = img.height;

        if (width > maxWidth) {
          height = height * (maxWidth / width);
          width = maxWidth;
        }

        canvas.width = width;
        canvas.height = height;

        const ctx = canvas.getContext("2d");
        ctx.drawImage(img, 0, 0, width, height);

        canvas.toBlob(
          (blob) => {
            const compressedFile = new File([blob], file.name, {
              type: "image/jpeg",
            });
            resolve(compressedFile);
          },
          "image/jpeg",
          quality
        );
      };
    };

    reader.readAsDataURL(file);
  });
};


// Registration Component
const RegistrationPage = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    user_id: '',
    name: '',
    license_number: '',
    dob: '',
    address: ''
  });

  const [selectedFiles, setSelectedFiles] = useState({
    face_image: null
  });

  const [previewUrls, setPreviewUrls] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [showCamera, setShowCamera] = useState(null);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleFileChange = (e) => {
    const { name, files } = e.target;
    if (files && files[0]) {
      handleFileSelection(files[0], name);
    }
  };

  // ✅ UPDATED (compression added)
  const handleFileSelection = async (file, fieldName) => {
    const compressedFile = await compressImage(file);

    setSelectedFiles(prev => ({
      ...prev,
      [fieldName]: compressedFile
    }));

    const url = URL.createObjectURL(compressedFile);
    setPreviewUrls(prev => ({
      ...prev,
      [fieldName]: url
    }));
  };

  // ✅ UPDATED (compression added)
  const handleCameraCapture = async (file, dataUrl, captureType) => {
    const compressedFile = await compressImage(file);
    handleFileSelection(compressedFile, `${captureType}_image`);
    setShowCamera(null);
  };

  const removeImage = (fieldName) => {
    if (previewUrls[fieldName]) {
      URL.revokeObjectURL(previewUrls[fieldName]);
    }

    setSelectedFiles(prev => ({
      ...prev,
      [fieldName]: null
    }));

    setPreviewUrls(prev => {
      const newPreviews = { ...prev };
      delete newPreviews[fieldName];
      return newPreviews;
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError('');
    setResult(null);

    const formDataObj = new FormData();
    Object.keys(formData).forEach(key => {
      formDataObj.append(key, formData[key]);
    });

    if (selectedFiles.face_image) {
      formDataObj.append('face_image', selectedFiles.face_image);
    }

    try {
      const response = await axios.post('http://localhost:5001/api/register', formDataObj, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });

      setResult(response.data);

      setFormData({
        user_id: '',
        name: '',
        license_number: '',
        dob: '',
        address: ''
      });

      setSelectedFiles({
        face_image: null
      });

      setPreviewUrls({});
    } catch (err) {
      setError(err.response?.data?.message || 'Registration failed');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleBackToHome = () => {
    navigate('/');
  };

  return (
    <div className="app-container">
      {showCamera && (
        <CameraCapture
          onCapture={handleCameraCapture}
          onClose={() => setShowCamera(null)}
          title={showCamera === 'face' ? "Capture Face Photo" : "Capture License Photo"}
          captureType={showCamera}
        />
      )}

      <header className="app-header">
        <div className="container">
          <div className="d-flex justify-content-between align-items-center">
            <div>
              <h1 className="header-title">User Registration</h1>
              <p className="header-subtitle">Register new users with facial biometrics</p>
            </div>
            <button className="btn btn-outline-primary" onClick={handleBackToHome}>
              Back to Home
            </button>
          </div>
        </div>
      </header>

      <main className="main-content">
        <div className="container">
          <div className="row justify-content-center">
            <div className="col-lg-8">
              {error && (
                <div className="alert alert-danger" role="alert">
                  {error}
                </div>
              )}

              {result && result.success && (
            <div className="alert alert-success" role="alert">
              <h4 className="alert-heading">Registration Successful!</h4>
              <p>User {result.user_id} has been registered successfully.</p>
            <hr />
              <p className="mb-0">
              Face embedding stored with dimension: {result?.details?.embedding_dimension || "N/A"}
              </p>
            </div>
            )}

              <form onSubmit={handleSubmit} className="card shadow-sm">
                <div className="card-body p-4">
                  <h2 className="section-title mb-4">Personal Information</h2>

                  <div className="mb-3">
                    <label className="form-label">User ID *</label>
                    <input type="text" className="form-control" name="user_id" value={formData.user_id} onChange={handleInputChange} required />
                  </div>

                  <div className="mb-3">
                    <label className="form-label">Full Name *</label>
                    <input type="text" className="form-control" name="name" value={formData.name} onChange={handleInputChange} required />
                  </div>

                  <div className="mb-3">
                    <label className="form-label">License Number *</label>
                    <input type="text" className="form-control" name="license_number" value={formData.license_number} onChange={handleInputChange} required />
                  </div>

                  <div className="mb-3">
                    <label className="form-label">Date of Birth *</label>
                    <input type="date" className="form-control" name="dob" value={formData.dob} onChange={handleInputChange} required />
                  </div>

                  <div className="mb-4">
                    <label className="form-label">Address *</label>
                    <textarea className="form-control" name="address" rows="3" value={formData.address} onChange={handleInputChange} required />
                  </div>

                  <h2 className="section-title mb-4">Biometric Data</h2>

                  <div className="mb-4">
                    <label className="form-label">Face Image *</label>
                    <div className="input-group">
                      <input type="file" className="form-control" name="face_image" accept="image/*" onChange={handleFileChange} />
                      <button className="btn btn-outline-primary" type="button" onClick={() => setShowCamera('face')}>
                        Camera
                      </button>
                    </div>

                    {previewUrls.face_image && (
                      <div className="mt-3 position-relative">
                        <img src={previewUrls.face_image} alt="Face preview" className="img-preview" />
                        <button type="button" className="btn btn-danger btn-sm position-absolute top-0 end-0 m-2" onClick={() => removeImage('face_image')}>
                          X
                        </button>
                      </div>
                    )}
                  </div>

                  <button type="submit" className="btn btn-primary btn-lg" disabled={isSubmitting}>
                    {isSubmitting ? 'Registering...' : 'Register User'}
                  </button>

                </div>
              </form>
            </div>
          </div>
        </div>
      </main>

      <footer className="app-footer">
        <div className="container">
          <p className="text-center mb-0">© 2026 Hybrid Verification System</p>
        </div>
      </footer>
    </div>
  );
};

// Verification Component
const VerificationPage = () => {
  const navigate = useNavigate();
  const [verificationType, setVerificationType] = useState('face_license');
  const [selectedFiles, setSelectedFiles] = useState({
    face_image: null,
    license_image: null
  });
  const [previewUrls, setPreviewUrls] = useState({});
  const [isVerifying, setIsVerifying] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [showCamera, setShowCamera] = useState(null); // 'face' or 'license'
  const [showResultModal, setShowResultModal] = useState(false);
  const MAX_IMAGE_SIZE = 2 * 1024 * 1024; // 2MB

  const handleFileChange = (e) => {
    const { name, files } = e.target;
    if (files && files[0]) {
      handleFileSelection(files[0], name);
    }
  };

  const handleFileSelection = (file, fieldName) => {

  // ✅ FILE SIZE VALIDATION
  if (file.size > MAX_IMAGE_SIZE) {
    setError("Image size should be less than 2MB");
    return;
  }

  setError('');

  setSelectedFiles(prev => ({
    ...prev,
    [fieldName]: file
  }));

  const url = URL.createObjectURL(file);
  setPreviewUrls(prev => ({
    ...prev,
    [fieldName]: url
  }));
};

  const handleCameraCapture = (file, dataUrl, captureType) => {

  // ✅ CAMERA IMAGE SIZE VALIDATION
  if (file.size > MAX_IMAGE_SIZE) {
    setError("Captured image is too large. Please retake under 2MB.");
    return;
  }

  setError('');

  handleFileSelection(file, `${captureType}_image`);
  setShowCamera(null);
};

  const removeImage = (fieldName) => {
    // Clean up the preview URL
    if (previewUrls[fieldName]) {
      URL.revokeObjectURL(previewUrls[fieldName]);
    }

    setSelectedFiles(prev => ({
      ...prev,
      [fieldName]: null
    }));

    setPreviewUrls(prev => {
      const newPreviews = { ...prev };
      delete newPreviews[fieldName];
      return newPreviews;
    });
  };

  const handleVerify = async (e) => {
    e.preventDefault();
    setIsVerifying(true);
    setError('');
    setResult(null);

    if (!selectedFiles.face_image) {
      setError('Please upload a face image');
      setIsVerifying(false);
      return;
    }

    if (verificationType === 'face_license' && !selectedFiles.license_image) {
      setError('Please upload a license image');
      setIsVerifying(false);
      return;
    }

    const formData = new FormData();
    formData.append('face_image', selectedFiles.face_image);

    if (verificationType === 'face_license') {
      formData.append('license_image', selectedFiles.license_image);
    }

    try {
      const endpoint = verificationType === 'face_license'
        ? 'http://localhost:5001/api/verify'
        : 'http://localhost:5001/api/verify-face-only';

      const response = await axios.post(endpoint, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });

      setResult(response.data);
      setShowResultModal(true);
    } catch (err) {
      const errorData = err.response?.data || { success: false, message: 'Verification failed' };
      setResult(errorData);
      setShowResultModal(true);
      setError(errorData.message || 'Verification failed');
    } finally {
      setIsVerifying(false);
    }
  };

  const handleBackToHome = () => {
    navigate('/');
  };

  return (
    <div className="app-container">
      {/* Verification Result Modal */}
      {showResultModal && (
        <VerificationResultModal
          result={result}
          onClose={() => setShowResultModal(false)}
          verificationType={verificationType}
        />
      )}

      {/* Camera Modal */}
      {showCamera && (
        <CameraCapture
          onCapture={handleCameraCapture}
          onClose={() => setShowCamera(null)}
          title={showCamera === 'face' ? "Capture Face Photo" : "Capture License Photo"}
          captureType={showCamera}
        />
      )}

      {/* Header */}
      <header className="app-header">
        <div className="container">
          <div className="d-flex justify-content-between align-items-center">
            <div>
              <h1 className="header-title">Identity Verification</h1>
              <p className="header-subtitle">Verify user identity with biometric authentication</p>
            </div>
            <button className="btn btn-outline-primary" onClick={handleBackToHome}>
              Back to Home
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="main-content">
        <div className="container">
          <div className="row justify-content-center">
            <div className="col-lg-8">
              {/* Verification Type Tabs */}
              <ul className="nav nav-tabs mb-4">
                <li className="nav-item">
                  <button
                    className={`nav-link ${verificationType === 'face_license' ? 'active' : ''}`}
                    onClick={() => setVerificationType('face_license')}
                  >
                    Full Verification (Face + License)
                  </button>
                </li>
                <li className="nav-item">
                  <button
                    className={`nav-link ${verificationType === 'face_only' ? 'active' : ''}`}
                    onClick={() => setVerificationType('face_only')}
                  >
                    Face Only
                  </button>
                </li>
              </ul>

              {error && (
                <div className="alert alert-danger" role="alert">
                  {error}
                </div>
              )}

              <form onSubmit={handleVerify} className="card shadow-sm">
                <div className="card-body p-4">
                  <h2 className="section-title mb-4">
                    {verificationType === 'face_license'
                      ? 'Full Verification'
                      : 'Face Verification'}
                  </h2>

                  {/* Face Image Upload */}
                  <div className="mb-4">
                    <label className="form-label">Face Image *</label>
                    <div className="input-group">
                      <input
                        type="file"
                        className="form-control"
                        id="face_image"
                        name="face_image"
                        accept="image/*"
                        onChange={handleFileChange}
                      />
                      <button
                        className="btn btn-outline-primary"
                        type="button"
                        onClick={() => setShowCamera('face')}
                      >
                        <i className="bi bi-camera-fill me-1"></i> Camera
                      </button>
                    </div>
                    {previewUrls.face_image && (
                      <div className="mt-3 position-relative">
                        <img
                          src={previewUrls.face_image}
                          alt="Face preview"
                          className="img-preview"
                          style={{ maxWidth: '300px', maxHeight: '300px' }}
                        />
                        <button
                          type="button"
                          className="btn btn-danger btn-sm position-absolute top-0 end-0 m-2"
                          onClick={() => removeImage('face_image')}
                        >
                          <i className="bi bi-x-lg"></i>
                        </button>
                      </div>
                    )}
                    <div className="form-text">Clear frontal face photo with good lighting</div>
                  </div>

                  {/* License Image Upload (only for full verification) */}
                  {verificationType === 'face_license' && (
                    <div className="mb-4">
                      <label className="form-label">Driver's License Image *</label>
                      <div className="input-group">
                        <input
                          type="file"
                          className="form-control"
                          id="license_image"
                          name="license_image"
                          accept="image/*"
                          onChange={handleFileChange}
                        />
                        <button
                          className="btn btn-outline-primary"
                          type="button"
                          onClick={() => setShowCamera('license')}
                        >
                          <i className="bi bi-camera-fill me-1"></i> Camera
                        </button>
                      </div>
                      {previewUrls.license_image && (
                        <div className="mt-3 position-relative">
                          <img
                            src={previewUrls.license_image}
                            alt="License preview"
                            className="img-preview"
                            style={{ maxWidth: '300px', maxHeight: '300px' }}
                          />
                          <button
                            type="button"
                            className="btn btn-danger btn-sm position-absolute top-0 end-0 m-2"
                            onClick={() => removeImage('license_image')}
                          >
                            <i className="bi bi-x-lg"></i>
                          </button>
                        </div>
                      )}
                      <div className="form-text">Clear photo of driver's license</div>
                    </div>
                  )}

                  <div className="d-grid">
                    <button
                      type="submit"
                      className="btn btn-primary btn-lg"
                      disabled={isVerifying}
                    >
                      {isVerifying ? (
                        <>
                          <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                          Verifying...
                        </>
                      ) : (
                        `Verify ${verificationType === 'face_license' ? 'Identity' : 'Face'}`
                      )}
                    </button>
                  </div>
                </div>
              </form>

              {/* Results Section */}
              {result && (
                <div className="result-section mt-4">
                  <h3 className="result-title">Verification Results</h3>
                  <div className="card result-card">
                    <div className="row">
                      <div className="col-md-6">
                        <div className="verification-details">
                          <div className="detail-row">
                            <span className="detail-label">Status:</span>
                            <span className={`badge ${result.success ? 'bg-success' : 'bg-grey'}`}>
                              {result.success ? 'Verified' : ''}
                            </span>
                          </div>
                          {result.user_id && (
                            <div className="detail-row">
                              <span className="detail-label">User ID:</span>
                              <span className="detail-value">{result.user_id}</span>
                            </div>
                          )}
                          {result.face_confidence !== undefined && (
                            <div className="detail-row">
                              <span className="detail-label">Face Confidence:</span>
                              <span className="detail-value">{(result.face_confidence * 100).toFixed(2)}%</span>
                            </div>
                          )}
                          {result.license_match_score !== undefined && (
                            <div className="detail-row">
                              <span className="detail-label">License Match:</span>
                              <span className="detail-value">{(result.license_match_score * 100).toFixed(2)}%</span>
                            </div>
                          )}
                        </div>
                      </div>
                      <div className="col-md-6">
                        <div className="verification-details">
                          {result.message && (
                            <div className="detail-row">
                              <span className="detail-label">Message:</span>
                              <span className="detail-value">{result.message}</span>
                            </div>
                          )}
                          {result.details && (
                            <div className="detail-row">
                              <span className="detail-label">Details:</span>
                              <span className="detail-value">{JSON.stringify(result.details)}</span>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="app-footer">
        <div className="container">
          <p className="text-center mb-0">© 2026 Hybrid Verification System. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
};

// Main App Component with Routing
const App = () => {
  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/register" element={<RegistrationPage />} />
      <Route path="/verify" element={<VerificationPage />} />
    </Routes>
  );
};

export default App;
