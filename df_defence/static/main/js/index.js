function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const fileInput = document.getElementById('file-input');
const fileLabel = document.getElementById('file-input-label');

// Listen for file input "change" event
fileInput.addEventListener('change', function () {
    // Get selected file name
    const fileName = this.files[0] ? this.files[0].name : '';

    // Update label content
    fileLabel.textContent = fileName;
});

let isRequestPending = false; // Flag variable
let currentSelectedModel = null;

// Add click event listeners for all model options
document.querySelectorAll('.model-option').forEach(option => {
    option.addEventListener('click', function () {
        const modelId = this.dataset.model;

        selectModel(this, modelId);
        // Get default selected model (if any)
        const defaultSelectedModel = document.querySelector('.model-option.selected');
        if (defaultSelectedModel) {
            currentSelectedModel = defaultSelectedModel.dataset.model;
            console.log(currentSelectedModel)
        }
    });
});


// Add submit event listener for form
const scanForm = document.getElementById('scan-form');
if (scanForm) {
    scanForm.addEventListener('submit', function (e) {
        e.preventDefault();
        importData();
    });
}

function importData() {
    if (isRequestPending) {
        console.log('Request already sent, processing...');
        return;
    }

    const fileInput = document.getElementById('file-input');
    const file = fileInput.files[0];
    const scan_button = document.getElementById('scan-button-id');
    const uploadProgress = document.getElementById('upload-progress');
    const progressBar = uploadProgress.querySelector('.progress-bar');
    const uploadStatus = uploadProgress.querySelector('.upload-status');

    // Use global variable to check model selection
    if (!currentSelectedModel) {
        // Try to get selected model from DOM
        const selectedModelElement = document.querySelector('.model-option.selected');
        if (selectedModelElement) {
            currentSelectedModel = selectedModelElement.dataset.model;
        }

        if (!currentSelectedModel) {
            showToast("Please select a detection model", 'warning');
            return;
        }
    }

    if (!file) {
        showToast("Please select a file to upload", 'warning');
        return;
    }

    // Check file type
    if (!(file.type === 'text/csv' || file.name.endsWith('.csv'))) {
        showToast("Please select a CSV format file for import", 'warning');
        return;
    }

    // Initial state: disable detection button
    scan_button.disabled = true;
    scan_button.style.backgroundColor = '#ccc';
    scan_button.textContent = 'File uploading...';

    // Show upload progress area
    uploadProgress.style.display = 'block';
    uploadStatus.textContent = 'Preparing upload...';
    progressBar.style.width = '0%';

    const csrftoken = getCookie('csrftoken');
    isRequestPending = true;
    const formData = new FormData();
    formData.append('file', file);
    formData.append('model', currentSelectedModel);

    fetch('do_index', {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken
        },
        body: formData
    })
        .then(response => {
            // Simulate upload progress
            let progress = 0;
            const interval = setInterval(() => {
                progress += 5;
                if (progress <= 100) {
                    progressBar.style.width = progress + '%';
                    uploadStatus.textContent = 'Uploading ' + progress + '%';
                }
                if (progress === 100) {
                    clearInterval(interval);
                }
            }, 100);

            return response.json();
        })
        .then(data => {
            if (data.status === 'success') {
                // Store uploaded file path
                window.lastUploadedPath = data.path;

                uploadStatus.textContent = 'Upload completed! Preparing to start detection...';
                uploadStatus.style.color = '#28a745';
                progressBar.style.width = '100%';

                // Update button state
                scan_button.textContent = 'Start Detection';
                scan_button.disabled = false;
                scan_button.style.backgroundColor = '';


                // Bind detection button click event
                scan_button.onclick = function () {
                    uploadProgress.style.display = 'none';
                    scan_button.style.backgroundColor = '#ccc';
                    scan_button.disabled = true;
                    scan_button.textContent = 'Detecting...';
                    document.getElementById('loading').style.display = 'block';
                    execScan(currentSelectedModel, data.path);
                };

                isRequestPending = false;
            } else {
                handleUploadError('Upload failed: ' + (data.message || 'Unknown error'));
            }
        })
        .catch(error => {
            handleUploadError('Upload error: ' + error.message);
        });
}

// Add error handling function
function handleUploadError(errorMessage) {
    isRequestPending = false;
    const uploadProgress = document.getElementById('upload-progress');
    const uploadStatus = uploadProgress.querySelector('.upload-status');
    const scan_button = document.getElementById('scan-button-id');

    uploadStatus.textContent = 'Upload failed';
    uploadStatus.style.color = '#dc3545';
    showToast(errorMessage, 'error');

    // Reset button state
    scan_button.disabled = false;
    scan_button.style.backgroundColor = '';
    scan_button.textContent = 'Start Detection';
}

function execScan(model, path) {
    var csrftoken = getCookie('csrftoken');
    var result_echarts = document.getElementById('result-echarts');
    var scan_button = document.getElementById('scan-button-id');
    var Loading = document.getElementById('loading');

    fetch('predict_exec', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({model: model, path: path})
    })
        .then(response => {
            // Ensure even error responses are handled correctly
            return response.json().then(data => {
                if (!response.ok) {
                    throw new Error(data.message || 'Network error');
                }
                return data;
            });
        })
        .then(data => {
            if (data.status === 'success') {
                // Display data results
                result_echarts.style.display = 'block';
                scan_button.style.backgroundColor = '';
                scan_button.disabled = false;
                scan_button.textContent = 'Start Detection';
                Loading.style.display = 'none';

                // Update charts
                updateCharts(data);
                showToast('Detection completed', 'success');
            } else {
                throw new Error(data.message || 'Processing failed');
            }
        })
        .catch(error => {
            console.error('Scan error:', error);
            result_echarts.style.display = 'none';  // Hide chart area
            scan_button.style.backgroundColor = '';
            scan_button.disabled = false;
            scan_button.textContent = 'Start Detection';
            Loading.style.display = 'none';

            // Show more friendly error message
            let errorMessage = error.message;
            if (errorMessage.includes('特征转换失败')) {
                errorMessage = 'Data format incompatible, please check if input data meets requirements';
            }
            showToast(errorMessage, 'error');
        });
}

// Add toast notification function
function showToast(message, type = 'info') {
    const toastContainer = document.getElementById('toast-container');
    if (!toastContainer) {
        const container = document.createElement('div');
        container.id = 'toast-container';
        container.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 1050;
        `;
        document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.style.cssText = `
        min-width: 200px;
        margin-bottom: 10px;
        padding: 15px;
        border-radius: 4px;
        font-size: 14px;
        opacity: 0;
        transition: opacity 0.3s ease-in-out;
    `;

    // Set different styles based on type
    switch (type) {
        case 'success':
            toast.style.backgroundColor = '#d4edda';
            toast.style.color = '#155724';
            toast.style.border = '1px solid #c3e6cb';
            break;
        case 'error':
            toast.style.backgroundColor = '#f8d7da';
            toast.style.color = '#721c24';
            toast.style.border = '1px solid #f5c6cb';
            break;
        case 'warning':
            toast.style.backgroundColor = '#fff3cd';
            toast.style.color = '#856404';
            toast.style.border = '1px solid #ffeeba';
            break;
        default:
            toast.style.backgroundColor = '#d1ecf1';
            toast.style.color = '#0c5460';
            toast.style.border = '1px solid #bee5eb';
    }

    toast.textContent = message;
    document.getElementById('toast-container').appendChild(toast);

    // Show toast notification
    setTimeout(() => {
        toast.style.opacity = '1';
    }, 10);

    // Error messages display for 5 seconds
    const displayTime = type === 'error' ? 5000 : 3000;

    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => {
            toast.remove();
        }, 300);
    }, displayTime);
}

// Update charts function
function updateCharts(data) {
    const myChart0 = echarts.init(document.getElementById('chart-container0'), null, {
        height: '400px'
    })
    const myChart1 = echarts.init(document.getElementById('chart-container1'), null, {
        height: '400px'
    })

    // Accuracy gauge configuration
    const option0 = {
        title: {
            text: 'Detection Accuracy',
            left: 'center',
            top: '2%',
            textStyle: {
                fontSize: 20
            }
        },
        grid: {
            top: '15%',
            bottom: '15%',
            left: '15%',
            right: '15%'
        },
        series: [{
            name: 'Accuracy',
            type: 'gauge',
            detail: {
                formatter: function (value) {
                    return value.toFixed(2).replace(/\.?0+$/, '') + '%';
                },
                fontSize: 20
            },
            data: [{value: parseFloat(data.overall_accuracy)}],
            axisLabel: {
                formatter: function (value) {
                    return value.toFixed(1) + '%';
                }
            }
        }]
    };

    // Attack type distribution pie chart configuration
    const option1 = {
        title: {
            text: 'Attack Type Distribution',
            left: 'center',
            top: '2%',
            textStyle: {
                fontSize: 20
            }
        },
        tooltip: {
            trigger: 'item',
            formatter: '{a} <br/>{b}: {c} ({d}%)'
        },
        legend: {
            orient: 'vertical',
            left: 'left',
            data: data.attack_types
        },
        series: [{
            name: 'Attack Type',
            type: 'pie',
            radius: ['40%', '70%'],
            data: data.attack_count_val.map(item => ({
                name: item[0],
                value: item[1]
            })),
            emphasis: {
                itemStyle: {
                    shadowBlur: 10,
                    shadowOffsetX: 0,
                    shadowColor: 'rgba(0, 0, 0, 0.5)'
                }
            }
        }]
    };

    myChart0.setOption(option0);
    myChart1.setOption(option1);
}

// Modify model selection function
function selectModel(element, modelId) {
    if (!element || !modelId) {
        console.error('Invalid model selection parameters');
        return;
    }

    try {
        // Remove selected state from other options
        document.querySelectorAll('.model-option').forEach(option => {
            option.classList.remove('selected');
            const badge = option.querySelector('.selected-badge');
            if (badge) {
                badge.style.display = 'none';
            }
        });

        // Add selected state to current option
        element.classList.add('selected');
        const selectedBadge = element.querySelector('.selected-badge');
        if (selectedBadge) {
            selectedBadge.style.display = 'block';
        }

        // Update currently selected model
        currentSelectedModel = modelId;
        console.log('Currently selected model:', currentSelectedModel);

        // If file has been uploaded and upload is complete, update scan_button onclick event
        const scan_button = document.getElementById('scan-button-id');
        if (scan_button && !scan_button.disabled && scan_button.textContent === 'Start Detection') {
            scan_button.onclick = function (e) {
                e.preventDefault();
                document.getElementById('upload-progress').style.display = 'none';
                scan_button.style.backgroundColor = '#ccc';
                scan_button.disabled = true;
                scan_button.textContent = 'Detecting...';
                const loading = document.getElementById('loading');
                if (loading) {
                    loading.style.display = 'block';
                }
                execScan(currentSelectedModel, window.lastUploadedPath);
            };
        }
    } catch (error) {
        console.error('Model selection error:', error);
        showToast('Model selection failed, please try again', 'error');
    }
}