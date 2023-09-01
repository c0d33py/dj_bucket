import '../assets/style.css';
import { FileUploader } from './element'

import axios from 'axios';
import { csrftoken } from './csrftoken';

const username = 'c0d3'
const password = 'testing123@'

// const token = Buffer.from(`${username}:${password}`, 'utf8').toString('base64')

const apiClient = axios.create({
    headers: {
        // 'Authorization': `Basic ${token}`

        // 'X-CSRFToken': csrftoken
    }
});


const upload = new FileUploader('userSpecifiedDiv');
upload.init({
    set_signed_url: 'http://localhost:8000/api/s3-upload/',
    set_storage_url: 'http://localhost:8000/api/resources/',
    set_models_name: 'core.UploadedFile.file',
    set_headers: apiClient,
    fileAccept: '*/*',
    multiple: true,
    title: 'Upload Files',
});