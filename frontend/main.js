const cameraContainer = document.getElementById('camera-container');
const cameraPreview = document.getElementById('camera-preview');
const canvas = document.getElementById('canvas');
const captureBtn = document.getElementById('capture-btn');
const switchCameraBtn = document.getElementById('switch-camera-btn');

const confirmationContainer = document.getElementById('confirmation-container');
const capturedImage = document.getElementById('captured-image');
const retakeBtn = document.getElementById('retake-btn');
const usePhotoBtn = document.getElementById('use-photo-btn');

const errorContainer = document.getElementById('error-container');
const errorMessage = document.getElementById('error-message');
const fallbackContainer = document.getElementById('fallback-container');
const fileInput = document.getElementById('file-input');

let stream;
let currentFacingMode = 'environment';

async function startCamera(facingMode = 'environment') {
    try {
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
        }

        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            throw new Error('Camera API not supported in this browser');
        }

        stream = await navigator.mediaDevices.getUserMedia({
            video: {
                facingMode: facingMode
            }
        });
        cameraPreview.srcObject = stream;
        checkCameraCapabilities();
    } catch (error) {
        console.error('Error accessing camera:', error);
        showError('Could not access the camera. Please make sure you have granted the necessary permissions.');
    }
}

async function checkCameraCapabilities() {
    const devices = await navigator.mediaDevices.enumerateDevices();
    const videoInputs = devices.filter(device => device.kind === 'videoinput');
    if (videoInputs.length > 1) {
        switchCameraBtn.style.display = 'block';
    } else {
        switchCameraBtn.style.display = 'none';
    }
}

function stopCamera() {
    if (stream) {
        stream.getTracks().forEach(track => track.stop());
    }
}

function capturePhoto() {
    canvas.width = cameraPreview.videoWidth;
    canvas.height = cameraPreview.videoHeight;
    canvas.getContext('2d').drawImage(cameraPreview, 0, 0);
    capturedImage.src = canvas.toDataURL('image/jpeg');
    cameraContainer.style.display = 'none';
    confirmationContainer.style.display = 'block';
    stopCamera();
}

function retakePhoto() {
    confirmationContainer.style.display = 'none';
    cameraContainer.style.display = 'block';
    startCamera(currentFacingMode);
}

function uploadPhoto() {
    canvas.toBlob(async (blob) => {
        const formData = new FormData();
        formData.append('file', blob, 'receipt.jpg');

        try {
            const response = await fetch('/receipts', {
                method: 'POST',
                body: formData
            });

            if (response.ok) {
                const result = await response.json();
                console.log('Upload successful:', result);
                alert(`Photo uploaded successfully! Job ID: ${result.job_id}`);
            } else {
                console.error('Upload failed:', response.statusText);
                showError('Failed to upload the photo. Please try again.');
            }
        } catch (error) {
            console.error('Error uploading photo:', error);
            showError('An error occurred while uploading the photo. Please check your network connection and try again.');
        }
    }, 'image/jpeg');
}

function showError(message) {
    errorMessage.textContent = message;
    errorContainer.style.display = 'block';
    cameraContainer.style.display = 'none';
    confirmationContainer.style.display = 'none';
    fallbackContainer.style.display = 'block';
}

async function uploadFile(file) {
    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch('/receipts', {
            method: 'POST',
            body: formData
        });

        if (response.ok) {
            const result = await response.json();
            console.log('Upload successful:', result);
            alert(`Photo uploaded successfully! Job ID: ${result.job_id}`);
        } else {
            console.error('Upload failed:', response.statusText);
            showError('Failed to upload the photo. Please try again.');
        }
    } catch (error) {
        console.error('Error uploading photo:', error);
        showError('An error occurred while uploading the photo. Please check your network connection and try again.');
    }
}

fileInput.addEventListener('change', (event) => {
    const file = event.target.files[0];
    if (file) {
        uploadFile(file);
    }
});

captureBtn.addEventListener('click', capturePhoto);
retakeBtn.addEventListener('click', retakePhoto);
usePhotoBtn.addEventListener('click', uploadPhoto);
switchCameraBtn.addEventListener('click', () => {
    currentFacingMode = currentFacingMode === 'environment' ? 'user' : 'environment';
    startCamera(currentFacingMode);
});

startCamera(currentFacingMode);
