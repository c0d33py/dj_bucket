// Import necessary modules
import S3FileFieldClient, { S3FileFieldProgressState } from './s3.js';

// Define the upload progress handler
function onUploadProgress(progress) {
    if (progress.state === S3FileFieldProgressState.Sending) {
        console.log(`Uploading ${progress.uploaded} / ${progress.total}`);
    }
}

// Create an Axios instance for custom configuration if needed
const apiClient = axios.create({
    // Set authentication headers or other configurations
});

// Create an instance of the S3FileFieldClient
const s3ffClient = new S3FileFieldClient({
    baseUrl: process.env.S3FF_BASE_URL, // Set the correct base URL
    onProgress: onUploadProgress, // Optional: progress handler
    apiConfig: apiClient.defaults, // Optional: Axios instance configuration
});

// Add event listener to handle file upload
document.getElementById('my-file-input').addEventListener('change', async (event) => {
    const file = event.target.files[0];

    try {
        const fieldValue = await s3ffClient.uploadFile(
            file,
            'core.File.blob' // The "<app>.<model>.<field>" to upload to
        );

        console.log('File upload successful', fieldValue);
    } catch (error) {
        console.error('File upload failed', error);
    }
});
