import { FileUploader } from './main'

import { csrftoken } from './csrftoken';


// Initialization
const headers = {
    'X-CSRFToken': csrftoken
};

const upload = new FileUploader('userSpecifiedDiv');
upload.init({
    setSignedUrl: 'http://localhost:8000/api/s3-upload/',
    setStorageUrl: 'http://localhost:8000/api/resources/',
    setModelsName: 'core.UploadedFile.file',
    setHeaders: headers,
    fileAccept: '*/*',
    multiple: true,
    btnTitle: 'Upload Files',
});