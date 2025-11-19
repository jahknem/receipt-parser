const fileInput = document.getElementById('file-input');
const uploadBtn = document.getElementById('upload-btn');
const progressBar = document.getElementById('progress-bar');
const statusDiv = document.getElementById('status');
const resultContainer = document.getElementById('result-container');
const resultPre = document.getElementById('result');
const cancelBtn = document.getElementById('cancel-btn');
const retryBtn = document.getElementById('retry-btn');

let xhr;
let jobId;
let pollingInterval;

fileInput.addEventListener('change', () => {
    uploadBtn.disabled = !fileInput.files.length;
});

uploadBtn.addEventListener('click', () => {
    const file = fileInput.files[0];
    if (!file) return;

    resetUI();
    uploadFile(file);
});

cancelBtn.addEventListener('click', () => {
    if (xhr) {
        xhr.abort();
    }
    if (pollingInterval) {
        clearTimeout(pollingInterval);
    }
    statusDiv.textContent = 'Upload canceled.';
    resetButtons();
});

retryBtn.addEventListener('click', () => {
    const file = fileInput.files[0];
    if (!file) return;

    resetUI();
    uploadFile(file);
});

function resetUI() {
    progressBar.style.width = '0%';
    progressBar.textContent = '';
    statusDiv.textContent = '';
    resultContainer.style.display = 'none';
    resultPre.textContent = '';
    cancelBtn.style.display = 'none';
    retryBtn.style.display = 'none';
}

function resetButtons() {
    uploadBtn.style.display = 'inline-block';
    cancelBtn.style.display = 'none';
    retryBtn.style.display = 'none';
}

function uploadFile(file) {
    const formData = new FormData();
    formData.append('file', file);

    xhr = new XMLHttpRequest();
    xhr.open('POST', '/receipts', true);

    xhr.upload.onprogress = (event) => {
        if (event.lengthComputable) {
            const percentComplete = (event.loaded / event.total) * 100;
            progressBar.style.width = percentComplete + '%';
            progressBar.textContent = Math.round(percentComplete) + '%';
        }
    };

    xhr.onload = () => {
        if (xhr.status === 202) {
            const response = JSON.parse(xhr.responseText);
            jobId = response.job_id;
            statusDiv.textContent = 'Processing...';
            pollJobStatus(jobId);
        } else if (xhr.status === 400) {
            handleError('Upload failed. Please select an image file.');
        } else {
            handleError('Upload failed. Server responded with ' + xhr.status);
        }
    };

    xhr.onerror = () => {
        handleError('An error occurred during the upload.');
    };

    xhr.onabort = () => {
        statusDiv.textContent = 'Upload canceled.';
        resetButtons();
    };


    xhr.send(formData);
    uploadBtn.style.display = 'none';
    cancelBtn.style.display = 'inline-block';
}

function pollJobStatus(jobId) {
    let backoff = 1000;
    const poll = () => {
        fetch(`/receipts/${jobId}`)
            .then(response => {
                if (response.status === 202) {
                    return response.json().then(data => {
                        if (data.status === 'processing') {
                            pollingInterval = setTimeout(poll, backoff);
                            backoff *= 2; // Exponential backoff
                        }
                    });
                } else if (response.status === 200) {
                    return response.json().then(data => {
                        statusDiv.textContent = 'Processing complete!';
                        resultContainer.style.display = 'block';
                        resultPre.textContent = JSON.stringify(data.parsed, null, 2);
                        resetButtons();
                    });
                } else if (response.status >= 400) {
                    return response.json().then(data => {
                         handleError(`Processing failed: ${data.detail}`);
                    });
                }
            })
            .catch(error => {
                handleError('An error occurred while polling for the result.');
            });
    };
    poll();
}

function handleError(message) {
    statusDiv.textContent = message;
    uploadBtn.style.display = 'none';
    cancelBtn.style.display = 'none';
    retryBtn.style.display = 'inline-block';
}