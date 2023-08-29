// Enum-like constants for result states
const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
const S3FileFieldResultState = {
    Aborted: 0,
    Successful: 1,
    Error: 2
};

const S3FileFieldProgressState = {
    Initializing: 0,
    Sending: 1,
    Finalizing: 2,
    Done: 3
};
class S3FileFieldClient {
    constructor(options) {
        const { baseUrl, apiConfig = {}, onProgress } = options;
        this.api = axios.create({
            ...apiConfig,
            baseURL: baseUrl.replace(/\/?$/, '/')
        });
        this.onProgress = onProgress;
    }

    async initializeUpload(file, fieldId) {
        const response = await this.api.post('upload-initialize/', {
            field_id: fieldId,
            file_name: file.name,
            file_size: file.size
        });
        return response.data;
    }

    async uploadParts(file, parts, onProgress) {
        const uploadedParts = [];
        let fileOffset = 0;
        for (const part of parts) {
            const chunk = file.slice(fileOffset, fileOffset + part.size);
            const response = await this.api.put(part.upload_url, chunk, {
                onUploadProgress: (e) => {
                    this.onProgress({
                        uploaded: fileOffset + e.loaded,
                        total: part.size,
                        state: S3FileFieldProgressState.Sending,
                        name: file.name
                    });
                }
            });
            uploadedParts.push({
                part_number: part.part_number,
                size: part.size,
                etag: response.headers.etag
            });
            fileOffset += part.size;
        }
        return uploadedParts;
    }

    async completeUpload(multipartInfo, parts) {
        const response = await this.api.post('upload-complete/', {
            upload_signature: multipartInfo.upload_signature,
            upload_id: multipartInfo.upload_id,
            parts
        });
        const { complete_url: completeUrl, body } = response.data;
        await axios.post(completeUrl, body, {
            headers: {
                'Content-Type': null
            }
        });
    }

    async finalize(multipartInfo) {
        const response = await this.api.post('finalize/', {
            upload_signature: multipartInfo.upload_signature
        });
        return response.data.field_value;
    }
    async uploadFile(file, fieldId, onProgress = () => { }) {
        onProgress({ state: S3FileFieldProgressState.Initializing });
        const multipartInfo = await this.initializeUpload(file, fieldId);
        onProgress({ state: S3FileFieldProgressState.Sending, uploaded: 0, total: file.size });
        const parts = await this.uploadParts(file, multipartInfo.parts, onProgress);
        onProgress({ state: S3FileFieldProgressState.Finalizing });
        await this.completeUpload(multipartInfo, parts);
        const value = await this.finalize(multipartInfo);
        onProgress({ state: S3FileFieldProgressState.Done });
        return {
            value,
            state: S3FileFieldResultState.Successful
        };
    }
}

function onUploadProgress(progress) {
    console.log(progress);
    if (progress.state == S3FileFieldProgressState.Sending) {
        console.log(`Uploading ${progress.uploaded} / ${progress.total}`);
    }
}

const s3ffClient = new S3FileFieldClient({
    baseUrl: 'http://localhost:8000/api/s3-upload/',
    onProgress: onUploadProgress,
    apiConfig: {
        headers: {
            'X-CSRFToken': csrfToken
        }
    },
});

const fileInput = document.getElementById('id_file');
fileInput.addEventListener('change', async (e) => {
    file = e.currentTarget.files[0];
    const { value, state } = await s3ffClient.uploadFile(file, 'core.UploadedFile.file');
    console.log('value', value, 'state', state);
})

// const uploadFiles = (() => {
//     const defaultOptions = {
//         url: '',
//         fieldId: '',
//         onError: () => { },
//         onProgress: () => { },
//         onCompleted: () => { },
//     }


//     const uploadFile = (file, options) => {
//         axios.post(options.url + 'upload-initialize/', {
//             field_id: 'core.UploadedFile.file',
//             file_name: file.name,
//             file_size: file.size
//         }, {
//             headers: {
//                 'X-CSRF-Token': csrfToken,
//                 'Content-Type': 'application/json'
//             }
//         })
//             .then(response => {
//                 data = response.data;
//                 uploadFileChunks(file, data, options);
//             }).catch(e => {
//                 options.onError(e, file)
//             });
//     };

//     return (files, options = defaultOptions) => {
//         [...files].forEach(file => uploadFile(file, { ...defaultOptions, ...options }));
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
//         console.log(e)
//         fileObj.status = FILE_STATUS.UPLOADING;
//         fileObj.percentage = e.loaded / e.total * 100;
//         updateFileElement(fileObj);
//     };

//     const onError = (e, file) => {
//         const fileObj = files.get(file);
//         console.log(e)

//         fileObj.status = FILE_STATUS.FAILED;
//         fileObj.percentage = 100;
//         updateFileElement(fileObj);
//     };

//     const onComplete = (e, file) => {
//         const fileObj = files.get(file);
//         console.log(e)

//         fileObj.status = FILE_STATUS.COMPLETED;
//         fileObj.percentage = 100;
//         updateFileElement(fileObj);
//     };

//     return (uploadedFiles) => {
//         [...uploadedFiles].forEach(setFileElement)

//         uploadFiles(uploadedFiles, {
//             url: 'http://localhost:8000/api/s3-upload/',
//             fieldId: 'core.UploadedFile.file',
//             onComplete,
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
