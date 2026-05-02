import React, { useRef, useState, useEffect } from 'react';
import 'bootstrap/dist/css/bootstrap.min.css';

const CameraCapture = ({
    onCapture,
    onClose,
    title = "Capture Image",
    captureType = "face" // "face" or "license"
}) => {
    const videoRef = useRef(null);
    const canvasRef = useRef(null);
    const [stream, setStream] = useState(null);
    const [capturedImage, setCapturedImage] = useState(null);
    const [facingMode, setFacingMode] = useState('user'); // 'user' for front camera, 'environment' for back
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        startCamera();

        return () => {
            stopCamera();
        };
    }, [facingMode]);

    const startCamera = async () => {
        setIsLoading(true);
        setError('');

        try {
            stopCamera(); // Stop any existing stream

            const constraints = {
                video: {
                    facingMode: facingMode,
                    width: { ideal: 1280 },
                    height: { ideal: 720 }
                },
                audio: false
            };

            const mediaStream = await navigator.mediaDevices.getUserMedia(constraints);
            setStream(mediaStream);

            if (videoRef.current) {
                videoRef.current.srcObject = mediaStream;
            }
        } catch (err) {
            console.error('Error accessing camera:', err);
            setError(`Could not access camera: ${err.message || 'Unknown error'}`);
        } finally {
            setIsLoading(false);
        }
    };

    const stopCamera = () => {
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
            setStream(null);
        }
    };

    const captureImage = () => {
        if (!videoRef.current) return;

        const video = videoRef.current;
        const canvas = canvasRef.current;

        if (!canvas) return;

        const context = canvas.getContext('2d');

        // Set canvas dimensions to match video
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;

        // Mirror the video when facingMode is 'user' (front camera)
        if (facingMode === 'user') {
            // Save the current context
            context.save();
            // Flip the canvas horizontally
            context.translate(canvas.width, 0);
            context.scale(-1, 1);
            // Draw the video frame (it will be mirrored)
            context.drawImage(video, 0, 0, canvas.width, canvas.height);
            // Restore the context
            context.restore();
        } else {
            // For back camera, draw normally without mirroring
            context.drawImage(video, 0, 0, canvas.width, canvas.height);
        }

        // Convert to data URL
        const dataUrl = canvas.toDataURL('image/jpeg', 0.9);
        setCapturedImage(dataUrl);
    };

    const retakeImage = () => {
        setCapturedImage(null);
    };

    const useImage = () => {
        if (!capturedImage) return;

        // Convert data URL to Blob
        const byteString = atob(capturedImage.split(',')[1]);
        const mimeString = capturedImage.split(',')[0].split(':')[1].split(';')[0];
        const ab = new ArrayBuffer(byteString.length);
        const ia = new Uint8Array(ab);

        for (let i = 0; i < byteString.length; i++) {
            ia[i] = byteString.charCodeAt(i);
        }

        const blob = new Blob([ab], { type: mimeString });

        // Create a File object
        const fileName = `${captureType}_${Date.now()}.jpg`;
        const file = new File([blob], fileName, { type: mimeString });

        // Call the onCapture callback with the file
        onCapture(file, capturedImage, captureType);
    };

    const toggleCamera = () => {
        setFacingMode(prev => prev === 'user' ? 'environment' : 'user');
    };

    return (
        <div className="camera-modal">
            <div className="camera-container">
                <div className="camera-header">
                    <h5>{title}</h5>
                    <button
                        type="button"
                        className="btn-close"
                        onClick={onClose}
                        aria-label="Close"
                    ></button>
                </div>

                <div className="camera-body">
                    {error ? (
                        <div className="text-center text-white p-4">
                            <div className="mb-3">
                                <i className="bi bi-camera-video-off" style={{
                                    fontSize: '3rem'
                                }}></i>
                            </div>
                            <p className="mb-0">{error}</p>
                            <button
                                className="btn btn-primary mt-3"
                                onClick={startCamera}
                            >
                                Retry Camera
                            </button>
                        </div>
                    ) : isLoading ? (
                        <div className="text-center text-white p-4">
                            <div className="spinner-border text-light" role="status">
                                <span className="visually-hidden">Loading...</span>
                            </div>
                            <p className="mt-2 mb-0">Accessing camera...</p>
                        </div>
                    ) : capturedImage ? (
                        <div className="text-center p-3">
                            <img
                                src={capturedImage}
                                alt="Captured"
                                className="img-fluid"
                                style={{ maxHeight: '70vh', objectFit: 'contain' }}
                            />
                        </div>
                    ) : (
                        <>
                            <video
                                ref={videoRef}
                                autoPlay
                                playsInline
                                muted
                                className="camera-video w-100"
                                style={{
                                    maxHeight: '70vh',
                                    objectFit: 'contain',
                                    transform: facingMode === 'user' ? 'scaleX(-1)' : 'none'
                                }}
                                onLoadedMetadata={() => setIsLoading(false)}
                            />
                            <canvas ref={canvasRef} style={{ display: 'none' }} />
                        </>
                    )}
                </div>

                <div className="camera-footer">
                    {error ? null : capturedImage ? (
                        <div className="d-flex justify-content-center gap-3">
                            <button
                                className="btn btn-secondary"
                                onClick={retakeImage}
                            >
                                <i className="bi bi-arrow-counterclockwise me-2"></i>
                                Retake
                            </button>
                            <button
                                className="btn btn-success"
                                onClick={useImage}
                            >
                                <i className="bi bi-check-circle me-2"></i>
                                Use Image
                            </button>
                        </div>
                    ) : (
                        <div className="d-flex justify-content-center gap-3">
                            <button
                                className="btn btn-outline-primary"
                                onClick={toggleCamera}
                                disabled={isLoading}
                            >
                                <i className="bi bi-arrow-repeat me-2"></i>
                                Switch Camera
                            </button>
                            <button
                                className="btn btn-primary btn-lg"
                                onClick={captureImage}
                                disabled={isLoading}
                            >
                                <i className="bi bi-camera-fill me-2"></i>
                                Capture
                            </button>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default CameraCapture;