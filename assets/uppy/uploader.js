"use strict";

const fileInput = document.getElementById('media-uuid')
const windowPath = window.location.href;

function stripQueryStringAndHashFromPath(URL) {
    return URL.split("vnr")[0].split("#")[0];
};

let _idArray = []
function getFiles(id) {
    _idArray.push(id)
    fileInput.value = _idArray
};

var uppy = new Uppy.Core({
    debug: false,
    allowMultipleUploadBatches: true,
    autoProceed: true,
    restrictions: {
        allowedFileTypes: ['image/*', 'video/*', '.mkv',],
    },
})
    .use(Uppy.Dashboard, {
        inline: true,
        target: '#drag-drop-area',
        proudlyDisplayPoweredByUppy: false,
        showProgressDetials: true,
        hideUploadButton: true,
        hideProgressAfterFinish: true,
        hideCancelButton: true,
        showRemoveButtonAfterComplete: true,
    })
    .use(Uppy.Tus, {
        endpoint: stripQueryStringAndHashFromPath(windowPath) + "/api/upload/",
        // headers: { 'X-CSRFToken': '{{ csrf_token }}' },
        height: 250,
        chunkSize: parseInt(512000, 10),
        retryDelays: [0, 1000, 3000, 5000],
        fileDate: true,
        fileName: 'file'
    })
uppy.on('complete', result => {
    result.successful.forEach(index => {
        console.log(index.response.uploadURL)
        // var file_id = /[^/]*$/.exec(index.response.uploadURL)[0];
        // getFiles(file_id);
    });
});
uppy.on('file-removed', (file, reason) => {
    removeFileFromUploadingCounterUI(file)

    if (reason === 'removed-by-user') {
        sendDeleteRequestForFile(file) // You need to implement this yourself
    }
})

var uploadBtn = $(id + ' .uppy-btn');
uploadBtn.click(function () {
    uppyDrag.upload();
});
