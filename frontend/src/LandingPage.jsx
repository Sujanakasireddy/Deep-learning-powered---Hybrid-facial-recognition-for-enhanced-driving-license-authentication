import React from 'react';
import { useNavigate } from 'react-router-dom';
import 'bootstrap/dist/css/bootstrap.min.css';
import './App.css';

const LandingPage = () => {
    const navigate = useNavigate();

    const handleRegisterClick = () => {
        navigate('/register');
    };

    const handleVerifyClick = () => {
        navigate('/verify');
    };

    return (
        <div className="min-vh-100 d-flex align-items-center" style={{ backgroundColor: '#2b2b2b' }}>
            <div className="container">
                <div className="row justify-content-center">
                    <div className="col-lg-10">
                        <div className="text-center mb-5">
                            <h1 className=" display-4 fw-bold text-light mb-3">
                                Hybrid Verification System
                            </h1>
                            <p className="lead text-light mb-4" style={{ maxWidth: '600px', margin: '0 auto' }}>
                                Secure identity verification combining facial recognition and driver's license validation
                            </p>
                        </div>

                        <div className="row g-4">
                            {/* Registration Card */}
                            <div className="col-md-6">
                                <div
                                    className="card h-100 border-0 shadow-sm cursor-pointer"
                                    style={{
                                        transition: 'all 0.3s ease',
                                        cursor: 'pointer',
                                        borderRadius: '16px',
                                        overflow: 'hidden'
                                    }}
                                    onClick={handleRegisterClick}
                                    onMouseEnter={(e) => {
                                        e.currentTarget.style.transform = 'translateY(-8px)';
                                        e.currentTarget.style.boxShadow = '0 12px 24px rgba(0,0,0,0.08)';
                                    }}
                                    onMouseLeave={(e) => {
                                        e.currentTarget.style.transform = 'translateY(0)';
                                        e.currentTarget.style.boxShadow = '0 4px 12px rgba(0,0,0,0.03)';
                                    }}
                                >
                                    <div className="card-body d-flex flex-column align-items-center justify-content-center p-5 text-center">
                                        <div className="mb-4">
                                            <div className="bg-primary bg-opacity-10 rounded-circle p-4 d-inline-flex">
                                                <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" fill="currentColor" className="bi bi-person-plus text-primary" viewBox="0 0 16 16">
                                                    <path d="M6 8a3 3 0 1 0 0-6 3 3 0 0 0 0 6zm2-3a2 2 0 1 1-4 0 2 2 0 0 1 4 0zm4 8c0 1-1 1-1 1H1s-1 0-1-1 1-4 6-4 6 3 6 4zm-1-.004c-.001-.246-.154-.986-.832-1.664C9.516 10.68 8.289 10 6 10c-2.29 0-3.516.68-4.168 1.332-.678.678-.83 1.418-.832 1.664h10z" />
                                                    <path fillRule="evenodd" d="M13.5 5a.5.5 0 0 1 .5.5V7h1.5a.5.5 0 0 1 0 1H14v1.5a.5.5 0 0 1-1 0V8h-1.5a.5.5 0 0 1 0-1H13V5.5a.5.5 0 0 1 .5-.5z" />
                                                </svg>
                                            </div>
                                        </div>
                                        <h3 className="card-title fw-bold mb-3 text-dark">User Registration</h3>
                                        <p className="card-text text-muted mb-4">
                                            Register new users with facial biometrics and driver's license verification
                                        </p>
                                        <button
                                            className="btn btn-primary px-4 py-2 rounded-pill"
                                            onClick={(e) => {
                                                e.stopPropagation();
                                                handleRegisterClick();
                                            }}
                                            style={{ fontWeight: '500' }}
                                        >
                                            Register Now
                                            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" className="bi bi-arrow-right ms-2" viewBox="0 0 16 16">
                                                <path fillRule="evenodd" d="M1 8a.5.5 0 0 1 .5-.5h11.793l-3.147-3.146a.5.5 0 0 1 .708-.708l4 4a.5.5 0 0 1 0 .708l-4 4a.5.5 0 0 1-.708-.708L13.293 8.5H1.5A.5.5 0 0 1 1 8z" />
                                            </svg>
                                        </button>
                                    </div>
                                </div>
                            </div>

                            {/* Verification Card */}
                            <div className="col-md-6">
                                <div
                                    className="card h-100 border-0 shadow-sm cursor-pointer"
                                    style={{
                                        transition: 'all 0.3s ease',
                                        cursor: 'pointer',
                                        borderRadius: '16px',
                                        overflow: 'hidden'
                                    }}
                                    onClick={handleVerifyClick}
                                    onMouseEnter={(e) => {
                                        e.currentTarget.style.transform = 'translateY(-8px)';
                                        e.currentTarget.style.boxShadow = '0 12px 24px rgba(0,0,0,0.08)';
                                    }}
                                    onMouseLeave={(e) => {
                                        e.currentTarget.style.transform = 'translateY(0)';
                                        e.currentTarget.style.boxShadow = '0 4px 12px rgba(0,0,0,0.03)';
                                    }}
                                >
                                    <div className="card-body d-flex flex-column align-items-center justify-content-center p-5 text-center">
                                        <div className="mb-4">
                                            <div className="bg-success bg-opacity-10 rounded-circle p-4 d-inline-flex">
                                                <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" fill="currentColor" className="bi bi-shield-check text-success" viewBox="0 0 16 16">
                                                    <path d="M5.338 1.59a61.44 61.44 0 0 0-2.837.856.481.481 0 0 0-.328.39c-.554 4.157.726 7.19 2.253 9.188a10.725 10.725 0 0 0 2.287 2.233c.346.244.652.42.893.533.12.057.218.095.293.118a.55.55 0 0 0 .101.025.615.615 0 0 0 .1-.025c.076-.023.174-.061.294-.118.24-.113.547-.29.893-.533a10.726 10.726 0 0 0 2.287-2.233c1.527-1.997 2.807-5.031 2.253-9.188a.48.48 0 0 0-.328-.39c-.651-.213-1.75-.56-2.837-.855C9.552 1.29 8.531 1.067 8 1.067c-.53 0-1.552.223-2.662.524zM5.072.56C6.157.265 7.31 0 8 0s1.843.265 2.928.56c1.11.3 2.229.655 2.887.87a1.54 1.54 0 0 1 1.044 1.262c.596 4.477-.787 7.795-2.465 9.99a11.775 11.775 0 0 1-2.517 2.453 7.159 7.159 0 0 1-1.048.625c-.28.132-.581.24-.829.24s-.548-.108-.829-.24a7.158 7.158 0 0 1-1.048-.625 11.777 11.777 0 0 1-2.517-2.453C1.928 10.487.545 7.169 1.141 2.692A1.54 1.54 0 0 1 2.185 1.43 62.456 62.456 0 0 1 5.072.56z" />
                                                    <path d="M10.854 5.146a.5.5 0 0 1 0 .708l-3 3a.5.5 0 0 1-.708 0l-1.5-1.5a.5.5 0 1 1 .708-.708L7.5 7.793l2.646-2.647a.5.5 0 0 1 .708 0z" />
                                                </svg>
                                            </div>
                                        </div>
                                        <h3 className="card-title fw-bold mb-3 text-dark">Identity Verification</h3>
                                        <p className="card-text text-muted mb-4">
                                            Verify user identity with real-time facial recognition and license authentication
                                        </p>
                                        <button
                                            className="btn btn-success px-4 py-2 rounded-pill"
                                            onClick={(e) => {
                                                e.stopPropagation();
                                                handleVerifyClick();
                                            }}
                                            style={{ fontWeight: '500' }}
                                        >
                                            Verify Identity
                                            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" className="bi bi-arrow-right ms-2" viewBox="0 0 16 16">
                                                <path fillRule="evenodd" d="M1 8a.5.5 0 0 1 .5-.5h11.793l-3.147-3.146a.5.5 0 0 1 .708-.708l4 4a.5.5 0 0 1 0 .708l-4 4a.5.5 0 0 1-.708-.708L13.293 8.5H1.5A.5.5 0 0 1 1 8z" />
                                            </svg>
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div className="text-center mt-5">
                            <div className="d-inline-block bg-light rounded-pill px-4 py-2">
                                <small className="text-muted mb-0">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" className="bi bi-shield-lock me-2" viewBox="0 0 16 16">
                                        <path d="M5.338 1.59a61.44 61.44 0 0 0-2.837.856.481.481 0 0 0-.328.39c-.554 4.157.726 7.19 2.253 9.188a10.725 10.725 0 0 0 2.287 2.233c.346.244.652.42.893.533.12.057.218.095.293.118a.55.55 0 0 0 .101.025.615.615 0 0 0 .1-.025c.076-.023.174-.061.294-.118.24-.113.547-.29.893-.533a10.726 10.726 0 0 0 2.287-2.233c1.527-1.997 2.807-5.031 2.253-9.188a.48.48 0 0 0-.328-.39c-.651-.213-1.75-.56-2.837-.855C9.552 1.29 8.531 1.067 8 1.067c-.53 0-1.552.223-2.662.524zM5.072.56C6.157.265 7.31 0 8 0s1.843.265 2.928.56c1.11.3 2.229.655 2.887.87a1.54 1.54 0 0 1 1.044 1.262c.596 4.477-.787 7.795-2.465 9.99a11.775 11.775 0 0 1-2.517 2.453 7.159 7.159 0 0 1-1.048.625c-.28.132-.581.24-.829.24s-.548-.108-.829-.24a7.158 7.158 0 0 1-1.048-.625 11.777 11.777 0 0 1-2.517-2.453C1.928 10.487.545 7.169 1.141 2.692A1.54 1.54 0 0 1 2.185 1.43 62.456 62.456 0 0 1 5.072.56z" />
                                        <path d="M9.5 6.5a1.5 1.5 0 1 1-3 0 1.5 1.5 0 0 1 3 0z" />
                                        <path d="M7.411 8.034a.5.5 0 0 1 .668.246c.067.415.257.832.591 1.157a3.178 3.178 0 0 0 .723.544c.282.147.616.257.97.327a.5.5 0 0 1-.098.995c-.448-.089-.857-.225-1.207-.408a4.178 4.178 0 0 1-.85-.576c-.294-.287-.52-.575-.675-.843a.5.5 0 0 1 .246-.668z" />
                                    </svg>
                                    Secure & Privacy Compliant
                                </small>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default LandingPage;