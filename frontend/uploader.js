const fileTarget = document.getElementById('file-target');

const uploadFiles = (() => {
    const defaultOptions = {
        url: '',
        onAbort: () => { },
        onError: () => { },
        onProgress: () => { },
        onCompleted: () => { },
    }

    const uploadFile = (file, options) => {
        const formData = new FormData();
        formData.append('file', file, file.name);

        req = new XMLHttpRequest();
        req.open('POST', options.url, true);

        req.onload = (e) => options.onCompleted(e, file);

        req.onerror = (e) => options.onError(e, file);

        req.ontimeout = (e) => options.onError(e, file);

        req.upload.onprogress = (e) => options.onProgress(e, file);

        req.onabort = (e) => options.onAbort(e, file);

        req.send(formData);
    }

    return (files, options = defaultOptions) => {
        [...files].forEach(file => uploadFile(file, options));
    }
})();

const uploadAndTrackFiles = (() => {
    const files = new Map();
    const FILE_STATUS = {
        PENDING: 'pending',
        UPLOADING: 'uploading',
        PAUSED: 'paused',
        COMPLETED: 'completed',
        FAILED: 'failed',
    };

    const progressBox = document.createElement('div');
    progressBox.className = 'upload-progress-tracker';
    progressBox.innerHTML = `
        <h3>Upload Progress</h3>
        <div class="file-progress-wrapper"></div>
        `;

    const setFileElement = file => {
        const fileElement = document.createElement('div');
        fileElement.className = 'upload-progress-tracker';
        fileElement.innerHTML = `
            <div class="file-details">
                <p>
                    <span class="file-name">${file.name}</span>
                    <span class="file-status">${FILE_STATUS.PENDING}</span>
                </p>
                <div class="progress-bar" style="width: 0; height: 2px; background: green;"></div>
            </div>
            `;

        files.set(file, {
            status: 'pending',
            size: file.size,
            percentage: 0,
            fileElement,
        });

        progressBox.querySelector('.file-progress-wrapper').appendChild(fileElement);
    };

    const updateFileElement = fileObject => {
        const [
            { children: [{ children: [, fileStatus] }, progressBar] } // file-details
        ] = fileObject.fileElement.children;

        requestAnimationFrame(() => {
            progressBar.style.background = fileObject.status === FILE_STATUS.COMPLETED
                ? 'green' : fileObject.status === FILE_STATUS.FAILED
                    ? 'red' : '#222';
            fileStatus.textContent = fileObject.status;
            fileStatus.className = `status ${fileObject.status}`;
            progressBar.style.width = `${fileObject.percentage}%`;
        });
    };

    const onProgress = (e, file) => {
        const fileObj = files.get(file);

        fileObj.status = FILE_STATUS.UPLOADING;
        fileObj.percentage = e.loaded / e.total * 100;
        updateFileElement(fileObj);
    };

    const onError = (e, file) => {
        const fileObj = files.get(file);

        fileObj.status = FILE_STATUS.FAILED;
        fileObj.percentage = 100;
        updateFileElement(fileObj);
    };

    const onAbort = (e, file) => {
        const fileObj = files.get(file);

        fileObj.status = FILE_STATUS.PAUSED;
        updateFileElement(fileObj);
    };

    const onCompleted = (e, file) => {
        const fileObj = files.get(file);

        fileObj.status = FILE_STATUS.COMPLETED;
        fileObj.percentage = 100;
        updateFileElement(fileObj);
    };

    return (uploadedFiles) => {
        [...uploadedFiles].forEach(setFileElement)

        uploadFiles(uploadedFiles, {
            url: 'http://localhost:8000/upload',
            onCompleted,
            onAbort,
            onError,
            onProgress,
        });
        document.body.appendChild(progressBox);
    }
})();

fileTarget.addEventListener('change', (e) => {
    const selectedFiles = e.target.files
    uploadAndTrackFiles(selectedFiles);
});


