import { S3FileFieldClient } from './client.js'

export class FileUploader {
    constructor(divId) {
        this.fileInput = null;
        this.section = document.getElementById(divId);
        this.progressBox = this.createProgressBox();
        this.files = new Map();
        this.FILE_STATUS = {
            PENDING: 'pending',
            UPLOADING: 'uploading',
            PAUSED: 'paused',
            COMPLETED: 'completed',
            FAILED: 'failed',
        };
        this.uploadedFileId = [];
    }

    init(options = {}) {
        this.options = options;
        this.configureFileInput();
        this.fileInput.addEventListener('change', this.trackUploadedFiles.bind(this));
    }

    configureFileInput() {
        const input = document.createElement('input');
        input.type = 'file';
        input.id = 'id_file';
        input.name = 'file';
        input.style.display = 'none';
        input.setAttribute('accept', this.options.fileAccept || 'image/*');
        if (this.options.multiple) {
            input.multiple = true;
        }
        const label = document.createElement('label');
        label.htmlFor = input.id;
        label.id = 'file-target';
        label.className = 'upload-btn';
        label.textContent = this.options.title || 'Upload File';

        label.appendChild(input);

        const specifiedDiv = this.section;
        specifiedDiv.appendChild(label);

        this.fileInput = input;
    }

    createProgressBox() {
        const progressBox = document.createElement('div');
        progressBox.className = 'upload-progress-tracker';
        progressBox.innerHTML = `
                <h3>Uploading 0 Files</h3>
                <div class="file-progress-wrapper"></div>
            `;
        return progressBox;
    };

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
    };

    setFileElement(file) {
        const extIndex = file.name.lastIndexOf('.');
        const fileElement = document.createElement('div');
        fileElement.className = 'file-progress';
        fileElement.dataset.file = file.name;
        fileElement.innerHTML = `
            <div class="file-details" style="position: relative">
                <p>
                    <span class="status">pending</span>
                    <span class="file-name">${file.name.substring(0, extIndex)}</span>
                    <span class="file-ext">${file.name.substring(extIndex)}</span>
                </p>
                <div class="progress-bar" style="width: 0;"></div>
            </div>`;
        this.files.set(file, {
            element: fileElement,
            size: file.size,
            status: this.FILE_STATUS.PENDING,
            percentage: 0,
        });
        this.progressBox.querySelector('.file-progress-wrapper').appendChild(fileElement);
    };

    onProgress(e, file) {
        const fileObj = this.files.get(file);
        if (!fileObj) {
            return;
        }
        fileObj.status = this.FILE_STATUS.UPLOADING;
        fileObj.percentage = Math.round((e.loaded / e.total) * 100);
        this.updateFileElement(fileObj);
    };

    onError(e, file) {
        const fileObj = this.files.get(file);

        fileObj.status = this.FILE_STATUS.FAILED;
        fileObj.percentage = 100;
        this.updateFileElement(fileObj);
    };

    onCompleted(file) {
        const fileObj = this.files.get(file);

        fileObj.status = this.FILE_STATUS.COMPLETED;
        fileObj.percentage = 100;
        this.updateFileElement(fileObj);
    };

    trackUploadedFiles(event) {
        const uploadedFiles = event.target.files;
        this.s3ffClient = new S3FileFieldClient({
            baseUrl: this.options.s3baseUrl,
            onCompleted: (e, file) => this.onCompleted(e, file),
            onError: (e, file) => this.onError(e, file),
            onProgress: (e, file) => this.onProgress(e, file),
            apiConfig: this.options.apiConfig || {},

        });

        [...uploadedFiles].forEach(async (file) => {
            this.setFileElement(file);
            const fieldValue = await this.s3ffClient.uploadFile(
                file,
                this.options.modelPoint,
            );

            if (fieldValue) {
                (async () => {
                    try {
                        const response = await this.s3ffClient.api.post(this.options.finalPath, {
                            file: fieldValue,
                        });
                        const dataId = response.data.id;
                        this.uploadedFileId.push(dataId);

                        this.onCompleted(file);
                    } catch (error) {
                        this.onError(error, file);
                        console.error('Error uploading file:', error.message);
                    }
                })();
            }
        });
        document.body.appendChild(this.progressBox);
    };

    getUploadedFileId() {
        return this.uploadedFileId;
    }
}

export default FileUploader;