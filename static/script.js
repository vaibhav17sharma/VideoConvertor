const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const fileCount = document.getElementById('fileCount');
const convertWebmBtn = document.getElementById('convertWebmBtn');
const convertHlsBtn = document.getElementById('convertHlsBtn');

// WebSocket connection for progress updates
const socket = io();
let progressData = {};

socket.on('conversion_progress', (data) => {
    progressData[data.filename] = data;
    updateProgressDisplay();
});

socket.on('hls_progress', (data) => {
    progressData[data.filename] = data;
    updateProgressDisplay();
});

function updateProgressDisplay() {
    const progressContainer = document.getElementById('progressContainer');
    if (!progressContainer) return;

    let html = '';
    for (const [filename, data] of Object.entries(progressData)) {
        html += `
            <div class="progress-item">
                <div class="progress-filename">${filename}</div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: ${data.progress}%"></div>
                </div>
                <div class="progress-info">
                    <span class="progress-percent">${data.progress.toFixed(1)}%</span>
                    <span class="progress-eta">ETA: ${data.eta}</span>
                </div>
            </div>
        `;
    }
    progressContainer.innerHTML = html;
}

// Drag and drop
uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('dragover');
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.classList.remove('dragover');
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
    fileInput.files = e.dataTransfer.files;
    updateFileCount();
});

fileInput.addEventListener('change', updateFileCount);

function updateFileCount() {
    const count = fileInput.files.length;
    const filePreview = document.getElementById('filePreview');
    const fileList = document.getElementById('fileList');

    if (count > 0) {
        fileCount.textContent = `${count} file${count > 1 ? 's' : ''} selected`;
        convertWebmBtn.disabled = false;
        convertHlsBtn.disabled = false;

        filePreview.style.display = 'block';
        fileList.innerHTML = '';

        Array.from(fileInput.files).forEach(file => {
            const fileItem = document.createElement('div');
            fileItem.className = 'file-item';

            const fileName = document.createElement('div');
            fileName.className = 'file-name';
            fileName.textContent = file.name;

            const fileSize = document.createElement('div');
            fileSize.className = 'file-size';
            fileSize.textContent = formatFileSize(file.size);

            const fileType = document.createElement('div');
            fileType.className = 'file-type';
            fileType.textContent = file.type.split('/')[1]?.toUpperCase() || file.name.split('.').pop().toUpperCase();

            fileItem.appendChild(fileName);
            fileItem.appendChild(fileSize);
            fileItem.appendChild(fileType);
            fileList.appendChild(fileItem);
        });
    } else {
        fileCount.textContent = '';
        convertWebmBtn.disabled = true;
        convertHlsBtn.disabled = true;
        filePreview.style.display = 'none';
    }
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// WebM form submission
document.getElementById('uploadForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    convertWebmBtn.textContent = 'Converting...';
    convertWebmBtn.disabled = true;
    convertHlsBtn.disabled = true;

    showProgressContainer('Converting to WebM...');
    progressData = {};

    const flashMessages = document.querySelector('.flash-messages');
    if (flashMessages) flashMessages.style.display = 'none';

    const formData = new FormData();
    Array.from(fileInput.files).forEach(file => formData.append('files', file));

    try {
        const response = await fetch('/upload', {
            method: 'POST',
            headers: { 'X-Requested-With': 'XMLHttpRequest' },
            body: formData
        });

        const result = await response.json();

        if (result.success) {
            showResults(result);
        } else {
            showError(result.error);
        }
    } catch (error) {
        showError('Upload failed: ' + error.message);
    }

    convertWebmBtn.textContent = 'Convert to WebM';
    convertWebmBtn.disabled = false;
    convertHlsBtn.disabled = false;
});

// HLS button handler
convertHlsBtn.addEventListener('click', async () => {
    if (!fileInput.reportValidity()) return;

    convertHlsBtn.textContent = 'Converting...';
    convertHlsBtn.disabled = true;
    convertWebmBtn.disabled = true;

    showProgressContainer('Converting to HLS (m3u8)...');
    progressData = {};

    const flashMessages = document.querySelector('.flash-messages');
    if (flashMessages) flashMessages.style.display = 'none';

    const formData = new FormData();
    Array.from(fileInput.files).forEach(file => formData.append('files', file));

    try {
        const response = await fetch('/convert-hls', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (result.success) {
            showHlsResults(result);
        } else {
            showError(result.error);
        }
    } catch (error) {
        showError('Upload failed: ' + error.message);
    }

    convertHlsBtn.textContent = 'Convert to m3u8';
    convertHlsBtn.disabled = false;
    convertWebmBtn.disabled = false;
});

function showResults(results) {
    document.querySelector('form').style.display = 'none';
    document.querySelector('.features') && (document.querySelector('.features').style.display = 'none');
    document.querySelector('.stats') && (document.querySelector('.stats').style.display = 'none');

    const progressSection = document.getElementById('progressSection');
    if (progressSection) progressSection.remove();

    const resultsHTML = `
        <div class="results-section">
            <div class="success-icon">🎉</div>
            <h2>Conversion Complete!</h2>

            <div class="summary">
                <div class="summary-title">Successfully converted ${results.files.length} file${results.files.length > 1 ? 's' : ''} to WebM</div>
                <div class="summary-stats">
                    <div class="stat">
                        <div class="stat-number">${(results.files.reduce((sum, f) => sum + f.savings_percent, 0) / results.files.length).toFixed(1)}%</div>
                        <div class="stat-label">Average Savings</div>
                    </div>
                    <div class="stat">
                        <div class="stat-number">${formatFileSize(results.files.reduce((sum, f) => sum + (f.original_size - f.converted_size), 0))}</div>
                        <div class="stat-label">Total Saved</div>
                    </div>
                </div>
            </div>

            <div class="cleanup-timer">
                ⏰ Files will be auto-deleted in: <span class="timer-value" id="cleanupTimer">30:00</span>
            </div>

            <div class="files-grid">
                ${results.files.map(file => `
                    <div class="file-card">
                        <div class="file-name">${file.filename}</div>
                        <div class="file-sizes">
                            <div class="size-info">
                                <div class="size-label">Original</div>
                                <div class="size-value">${formatFileSize(file.original_size)}</div>
                            </div>
                            <div class="size-info">
                                <div class="size-label">WebM</div>
                                <div class="size-value">${formatFileSize(file.converted_size)}</div>
                            </div>
                        </div>
                        <div class="savings">
                            ${file.savings_percent > 0 ?
                                `🎯 ${file.savings_percent.toFixed(1)}% smaller` :
                                `📈 ${(-file.savings_percent).toFixed(1)}% larger`
                            }
                        </div>
                        <div class="encoder-badge${file.encoder_used.startsWith('GPU') ? ' gpu' : ''}">${file.encoder_used}</div>
                    </div>
                `).join('')}
            </div>

            <div class="download-section">
                ${results.is_batch ?
                    '<a href="/download_batch" class="download-btn">📦 Download All as ZIP</a>' :
                    `<a href="/download/${results.files[0].filename}" class="download-btn">⬇️ Download ${results.files[0].filename}</a>`
                }
                <button onclick="location.reload()" class="download-btn back-btn">🔄 Convert More Files</button>
            </div>

            ${results.errors && results.errors.length > 0 ? `
                <div class="errors">
                    <div class="error-title">⚠️ Some files couldn't be converted:</div>
                    ${results.errors.map(error => `<div class="error-item">${error}</div>`).join('')}
                </div>
            ` : ''}
        </div>
    `;

    document.querySelector('.container').insertAdjacentHTML('beforeend', resultsHTML);
    startCleanupTimer();
}

function showHlsResults(results) {
    document.querySelector('form').style.display = 'none';
    document.querySelector('.features') && (document.querySelector('.features').style.display = 'none');
    document.querySelector('.stats') && (document.querySelector('.stats').style.display = 'none');

    const progressSection = document.getElementById('progressSection');
    if (progressSection) progressSection.remove();

    const resultsHTML = `
        <div class="results-section">
            <div class="success-icon">🎉</div>
            <h2>HLS Conversion Complete!</h2>

            <div class="summary">
                <div class="summary-title">Successfully converted ${results.jobs.length} file${results.jobs.length > 1 ? 's' : ''} to HLS (m3u8)</div>
                <div class="summary-stats">
                    <div class="stat">
                        <div class="stat-number">${results.jobs.reduce((sum, j) => sum + j.segment_count, 0)}</div>
                        <div class="stat-label">Total Segments</div>
                    </div>
                    <div class="stat">
                        <div class="stat-number">${formatFileSize(results.jobs.reduce((sum, j) => sum + j.total_size, 0))}</div>
                        <div class="stat-label">Total Size</div>
                    </div>
                </div>
            </div>

            <div class="cleanup-timer">
                ⏰ Files will be auto-deleted in: <span class="timer-value" id="cleanupTimer">30:00</span>
            </div>

            <div class="files-grid">
                ${results.jobs.map(job => `
                    <div class="file-card">
                        <div class="file-name">${job.original_name}</div>
                        <div class="file-sizes">
                            <div class="size-info">
                                <div class="size-label">Segments</div>
                                <div class="size-value">${job.segment_count} .ts files</div>
                            </div>
                            <div class="size-info">
                                <div class="size-label">Total Size</div>
                                <div class="size-value">${formatFileSize(job.total_size)}</div>
                            </div>
                        </div>
                        <div class="savings">📺 playlist.m3u8 + ${job.segment_count} segments</div>
                        <div class="encoder-badge${job.encoder_used.startsWith('GPU') ? ' gpu' : ''}">${job.encoder_used}</div>
                        <div style="margin-top:10px">
                            <a href="/download-hls/${job.job_id}" class="download-btn" style="padding:8px 20px;font-size:0.9em">⬇️ Download ZIP</a>
                        </div>
                    </div>
                `).join('')}
            </div>

            <div class="download-section">
                ${results.is_batch ?
                    '<a href="/download-hls-batch" class="download-btn">📦 Download All as ZIP</a>' :
                    `<a href="/download-hls/${results.jobs[0].job_id}" class="download-btn">⬇️ Download ${results.jobs[0].original_name.replace(/\.[^.]+$/, '')}.zip</a>`
                }
                <button onclick="location.reload()" class="download-btn back-btn">🔄 Convert More Files</button>
            </div>

            ${results.errors && results.errors.length > 0 ? `
                <div class="errors">
                    <div class="error-title">⚠️ Some files couldn't be converted:</div>
                    ${results.errors.map(error => `<div class="error-item">${error}</div>`).join('')}
                </div>
            ` : ''}
        </div>
    `;

    document.querySelector('.container').insertAdjacentHTML('beforeend', resultsHTML);
    startCleanupTimer();
}

function showProgressContainer(title = 'Converting Videos...') {
    const existing = document.getElementById('progressSection');
    if (existing) existing.remove();

    const progressHTML = `
        <div class="progress-section" id="progressSection">
            <h3>${title}</h3>
            <div id="progressContainer"></div>
        </div>
    `;
    document.querySelector('.container').insertAdjacentHTML('beforeend', progressHTML);
}

function showError(message) {
    const existing = document.querySelector('.flash-messages');
    if (existing) existing.remove();

    const errorHTML = `
        <div class="flash-messages">
            <div class="flash-message error">${message}</div>
        </div>
    `;
    document.querySelector('.container').insertAdjacentHTML('afterbegin', errorHTML);
}

function startCleanupTimer() {
    let timeLeft = 1800;
    const timerElement = document.getElementById('cleanupTimer');

    const timer = setInterval(() => {
        const minutes = Math.floor(timeLeft / 60);
        const seconds = timeLeft % 60;
        timerElement.textContent = `${minutes}:${seconds.toString().padStart(2, '0')}`;

        if (timeLeft <= 0) {
            clearInterval(timer);
            timerElement.textContent = 'Files deleted';
            timerElement.parentElement.style.background = 'rgba(220, 53, 69, 0.1)';
            timerElement.parentElement.style.borderColor = '#dc3545';
        }

        timeLeft--;
    }, 1000);
}

window.addEventListener('load', () => {
    setTimeout(() => {
        const flashMessages = document.querySelector('.flash-messages');
        if (flashMessages) {
            flashMessages.style.opacity = '0';
            flashMessages.style.transition = 'opacity 0.5s ease';
            setTimeout(() => { flashMessages.style.display = 'none'; }, 500);
        }
    }, 5000);
});
