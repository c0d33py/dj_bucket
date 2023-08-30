// const uploadFiles = (() => {
//     const defaultOptions = {
//         url: '',
//         onAbort: () => { },
//         onError: () => { },
//         onProgress: () => { },
//         onCompleted: () => { },
//     }

//     const uploadFile = (file, options) => {
//         const formData = new FormData();
//         formData.append('file', file, file.name);

//         const req = new XMLHttpRequest();
//         req.open('POST', options.url, true);

//         req.onload = (e) => options.onCompleted(e, file);

//         req.onerror = (e) => options.onError(e, file);

//         req.ontimeout = (e) => options.onError(e, file);

//         req.upload.onprogress = (e) => options.onProgress(e, file);

//         req.onabort = (e) => options.onAbort(e, file);

//         req.send(formData);
//     }

//     return (files, options = defaultOptions) => {
//         [...files].forEach(file => uploadFile(file, options));
//     }
// })();

// const uploadAndTrackFiles = (() => {
//     const files = new Map();
//     const FILE_STATUS = {
//         PENDING: 'pending',
//         UPLOADING: 'uploading',
//         PAUSED: 'paused',
//         COMPLETED: 'completed',
//         FAILED: 'failed',
//     };

//     const progressBox = document.createElement('div');
//     progressBox.className = 'upload-progress-tracker';
//     progressBox.innerHTML = `
//                 <h3>Uploading 0 Files</h3>
// 				<div class="uploads-progress-bar" style="width: 0;"></div>
// 				<div class="file-progress-wrapper"></div>
//         `;


//     const updateFileElement = (fileObject) => {
//         const fileDetails = fileObject.element.querySelector('.file-details');
//         const status = fileDetails.querySelector('.status');
//         const progressBar = fileDetails.querySelector('.progress-bar');

//         requestAnimationFrame(() => {
//             status.textContent = fileObject.status === FILE_STATUS.COMPLETED ? fileObject.status : `${Math.round(fileObject.percentage)}%`;
//             status.className = `status ${fileObject.status}`;
//             progressBar.style.width = fileObject.percentage + '%';
//             progressBar.style.background = fileObject.status === FILE_STATUS.COMPLETED
//                 ? 'green' : fileObject.status === FILE_STATUS.FAILED
//                     ? 'red' : '#222';
//         });
//     };

//     const setFileElement = (file) => {
//         const extIndex = file.name.lastIndexOf('.');
//         const fileElement = document.createElement('div');
//         fileElement.className = 'file-progress';
//         fileElement.innerHTML = `
// 			<div class="file-details" style="position: relative">
// 				<p>
// 					<span class="status">pending</span>
// 					<span class="file-name">${file.name.substring(0, extIndex)}</span>
// 					<span class="file-ext">${file.name.substring(extIndex)}</span>
// 				</p>
// 				<div class="progress-bar" style="width: 0;"></div>
// 			</div>
// 		`;
//         files.set(file, {
//             element: fileElement,
//             size: file.size,
//             status: FILE_STATUS.PENDING,
//             percentage: 0,
//         });

//         progressBox.querySelector('.file-progress-wrapper').appendChild(fileElement);
//     };

//     const onProgress = (e, file) => {
//         const fileObj = files.get(file);

//         fileObj.status = FILE_STATUS.UPLOADING;
//         fileObj.percentage = e.loaded / e.total * 100;
//         updateFileElement(fileObj);
//     };

//     const onError = (e, file) => {
//         const fileObj = files.get(file);

//         fileObj.status = FILE_STATUS.FAILED;
//         fileObj.percentage = 100;
//         updateFileElement(fileObj);
//     };

//     const onAbort = (e, file) => {
//         const fileObj = files.get(file);

//         fileObj.status = FILE_STATUS.PAUSED;
//         updateFileElement(fileObj);
//     };

//     const onCompleted = (e, file) => {
//         const fileObj = files.get(file);

//         fileObj.status = FILE_STATUS.COMPLETED;
//         fileObj.percentage = 100;
//         updateFileElement(fileObj);
//     };

//     return (uploadedFiles) => {
//         [...uploadedFiles].forEach(setFileElement)

//         uploadFiles(uploadedFiles, {
//             url: 'http://localhost:1234/upload',
//             onCompleted,
//             onAbort,
//             onError,
//             onProgress,
//         });
//         document.body.appendChild(progressBox);
//     }
// })();

// const fileInput = document.getElementById('id_file');
// fileInput.addEventListener('change', e => {
//     uploadAndTrackFiles(e.currentTarget.files)
//     e.currentTarget.value = '';
// })


class UploadManager {
    constructor(options) {
        this.options = Object.assign({}, UploadManager.defaultOptions, options);
    }

    uploadFile(file) {
        const formData = new FormData();
        formData.append('file', file, file.name);

        const req = new XMLHttpRequest();
        req.open('POST', this.options.url, true);

        req.onload = (e) => this.options.onCompleted(e, file);
        req.onerror = (e) => this.options.onError(e, file);
        req.ontimeout = (e) => this.options.onError(e, file);
        req.upload.onprogress = (e) => this.options.onProgress(e, file);
        req.onabort = (e) => this.options.onAbort(e, file);

        req.send(formData);
    }
}

UploadManager.defaultOptions = {
    url: '',
    onAbort: () => { },
    onError: () => { },
    onProgress: () => { },
    onCompleted: () => { },
};

class FileUploadTracker {
    constructor() {
        this.files = new Map();
        this.FILE_STATUS = {
            PENDING: 'pending',
            UPLOADING: 'uploading',
            PAUSED: 'paused',
            COMPLETED: 'completed',
            FAILED: 'failed',
        };
        this.progressBox = this.createProgressBox();
    }

    createProgressBox() {
        const progressBox = document.createElement('div');
        progressBox.className = 'upload-progress-tracker';
        progressBox.innerHTML = `
            <h3>Uploading 0 Files</h3>
            <div class="uploads-progress-bar" style="width: 0;"></div>
            <div class="file-progress-wrapper"></div>uploadFile
        `;
        return progressBox;
    }

    updateFileElement(fileObject) {
        const fileDetails = fileObject.element.querySelector('.file-details');
        const status = fileDetails.querySelector('.status');
        const progressBar = fileDetails.querySelector('.progress-bar');

        requestAnimationFrame(() => {
            status.textContent = fileObject.status === this.FILE_STATUS.COMPLETED
                ? fileObject.status
                : `${Math.round(fileObject.percentage)}%`;
            status.className = `status ${fileObject.status}`;
            progressBar.style.width = fileObject.percentage + '%';
            progressBar.style.background =
                fileObject.status === this.FILE_STATUS.COMPLETED
                    ? 'green'
                    : fileObject.status === this.FILE_STATUS.FAILED
                        ? 'red'
                        : '#222';
        });
    }

    setFileElement(file) {
        const extIndex = file.name.lastIndexOf('.');
        const fileElement = document.createElement('div');
        fileElement.className = 'file-progress';
        fileElement.innerHTML = `
            <div class="file-details" style="position: relative">
                <p>
                    <span class="status">pending</span>
                    <span class="file-name">${file.name.substring(0, extIndex)}</span>
                    <span class="file-ext">${file.name.substring(extIndex)}</span>
                </p>
                <div class="progress-bar" style="width: 0;"></div>
            </div>
        `;
        this.files.set(file, {
            element: fileElement,
            size: file.size,
            status: this.FILE_STATUS.PENDING,
            percentage: 0,
        });

        this.progressBox.querySelector('.file-progress-wrapper').appendChild(fileElement);
    }

    onProgress(e, file) {
        const fileObj = this.files.get(file);

        fileObj.status = this.FILE_STATUS.UPLOADING;
        fileObj.percentage = (e.loaded / e.total) * 100;
        this.updateFileElement(fileObj);
    }

    onError(e, file) {
        const fileObj = this.files.get(file);

        fileObj.status = this.FILE_STATUS.FAILED;
        fileObj.percentage = 100;
        this.updateFileElement(fileObj);
    }

    onAbort(e, file) {
        const fileObj = this.files.get(file);

        fileObj.status = this.FILE_STATUS.PAUSED;
        this.updateFileElement(fileObj);
    }

    onCompleted(e, file) {
        const fileObj = this.files.get(file);

        fileObj.status = this.FILE_STATUS.COMPLETED;
        fileObj.percentage = 100;
        this.updateFileElement(fileObj);
    }

    trackUploadedFiles(uploadedFiles) {
        [...uploadedFiles].forEach((file) => this.setFileElement(file));

        const uploadManager = new UploadManager({
            url: 'http://localhost:1234/upload',
            onCompleted: (e, file) => this.onCompleted(e, file),
            onAbort: (e, file) => this.onAbort(e, file),
            onError: (e, file) => this.onError(e, file),
            onProgress: (e, file) => this.onProgress(e, file),
        });

        [...uploadedFiles].forEach((file) => uploadManager.uploadFile(file));

        document.body.appendChild(this.progressBox);
    }
}

const fileInput = document.getElementById('id_file');
const fileUploadTracker = new FileUploadTracker();

fileInput.addEventListener('change', (e) => {
    fileUploadTracker.trackUploadedFiles(e.currentTarget.files);
    e.currentTarget.value = '';
});
