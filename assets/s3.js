const axios = require('axios');

// Enum-like constants for result states
const S3FileFieldResultState = {
    Aborted: 0,
    Successful: 1,
    Error: 2
};

// Enum-like constants for progress states
const S3FileFieldProgressState = {
    Initializing: 0,
    Sending: 1,
    Finalizing: 2,
    Done: 3
};

class S3FileFieldClient {
    constructor(options) {
        const { baseUrl, apiConfig = {} } = options;
        this.api = axios.create(Object.assign({}, apiConfig, {
            baseURL: baseUrl.replace(/\/?$/, '/')
        }));
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
            const response = await axios.put(part.upload_url, chunk, {
                onUploadProgress: (e) => {
                    onProgress({
                        uploaded: fileOffset + e.loaded,
                        total: file.size,
                        state: S3FileFieldProgressState.Sending
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

module.exports = {
    S3FileFieldClient,
    S3FileFieldResultState,
    S3FileFieldProgressState
};
