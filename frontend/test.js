
document.addEventListener('DOMContentLoaded', () => {
    const testResults = document.getElementById('test-results');
    let testCount = 0;
    let passCount = 0;

    function assert(condition, message) {
        testCount++;
        const p = document.createElement('p');
        if (condition) {
            passCount++;
            p.style.color = 'green';
            p.textContent = `PASS: ${message}`;
        } else {
            p.style.color = 'red';
            p.textContent = `FAIL: ${message}`;
        }
        testResults.appendChild(p);
    }

    function summary() {
        const p = document.createElement('p');
        p.innerHTML = `<strong>Tests complete: ${passCount}/${testCount} passed.</strong>`;
        testResults.appendChild(p);
    }

    // Mocking browser APIs and DOM elements
    const mockStream = {
        getTracks: () => [{
            stop: () => {}
        }]
    };
    navigator.mediaDevices.getUserMedia = async () => mockStream;
    HTMLCanvasElement.prototype.toBlob = function(callback) {
        callback(new Blob());
    };
    window.fetch = async (url, options) => {
        if (url === '/receipts' && options.method === 'POST') {
            return {
                ok: true,
                json: async () => ({
                    job_id: 'test-job-id'
                })
            };
        }
    };

    async function runTests() {
        // Test: startCamera successfully starts the camera
        await startCamera();
        assert(cameraPreview.srcObject === mockStream, "startCamera should set the video srcObject.");

        // Test: capturePhoto updates the UI
        capturePhoto();
        assert(confirmationContainer.style.display === 'block', "capturePhoto should show the confirmation container.");
        assert(cameraContainer.style.display === 'none', "capturePhoto should hide the camera container.");

        // Test: retakePhoto goes back to the camera view
        retakePhoto();
        assert(confirmationContainer.style.display === 'none', "retakePhoto should hide the confirmation container.");
        assert(cameraContainer.style.display === 'block', "retakePhoto should show the camera container.");

        // Test: switchCamera toggles facing mode
        const initialFacingMode = currentFacingMode;
        switchCameraBtn.click();
        assert(currentFacingMode !== initialFacingMode, "switchCameraBtn should toggle the currentFacingMode.");

        // Test: uploadPhoto calls fetch
        let fetchCalled = false;
        const originalFetch = window.fetch;
        window.fetch = async (url, options) => {
            if (url === '/receipts') {
                fetchCalled = true;
            }
            return originalFetch(url, options);
        };
        uploadPhoto();
        // Allow time for the async operation to complete
        await new Promise(resolve => setTimeout(resolve, 100));
        assert(fetchCalled, "uploadPhoto should call fetch with the /receipts endpoint.");
        window.fetch = originalFetch;

        summary();
    }

    runTests();
});
