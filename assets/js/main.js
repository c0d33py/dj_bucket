/* global tus */
/* eslint-disable no-console, no-alert */
let upload = null
let uploadIsRunning = false
const inputSection = document.querySelector('#input-section')
const toggleBtn = document.querySelector('#toggle-btn')
const input = document.querySelector('#js-file-input')
const progressBar = document.querySelector('.progress-bar')
const alertBox = document.querySelector('#support-alert')
const uploadList = document.querySelector('#upload-list')
const textProgress = document.querySelector('#js-upload-text-progress')
const progressContainer = document.querySelector('#progress-section')
const textHeading = document.querySelector('#heading')

progressContainer.setAttribute("hidden", true);

function reset() {
  input.value = ''
  toggleBtn.textContent = 'start'
  upload = null
  uploadIsRunning = false
}

function startUpload() {

  textHeading.textContent = 'The upload is running:'
  inputSection.setAttribute("hidden", true);
  progressContainer.removeAttribute("hidden");

  const file = input.files[0]
  // Only continue if a file has actually been selected.
  // IE will trigger a change event even if we reset the input element
  // using reset() and we do not want to blow up later.
  if (!file) {
    return
  }

  const endpoint = 'http://localhost:8000/files/'
  let chunkSize = parseInt(5242880, 10)

  toggleBtn.textContent = 'pause'

  const options = {
    // headers: {
    //   // authorization is required for the endpoint
    //   'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjczNzEyMTQ2LCJpYXQiOjE2NzM3MDg1NDYsImp0aSI6IjY4NmJkMThkZWM2ZTQxMmM4NzZhMjMyNDBmNThmMThjIiwidXNlcl9pZCI6ODJ9.EmLRcBZoX2ly0GhhEWZw_QINpNKhDDsfhjr7jt8lLQw',
    // },
    endpoint,
    chunkSize,
    retryDelays: [0, 1000, 3000, 5000],
    metadata: {
      filename: file.name,
      filetype: file.type,
    },
    onError(error) {
      if (error.originalRequest) {
        if (window.confirm(`Failed because: ${error}\nDo you want to retry?`)) {
          upload.start()
          uploadIsRunning = true
          return
        }
      } else {
        window.alert(`Failed because: ${error}`)
      }
      reset()
    },
    onProgress(bytesUploaded, bytesTotal) {
      const percentage = ((bytesUploaded / bytesTotal) * 100).toFixed(2)
      progressBar.style.width = `${percentage}%`
      console.log(bytesUploaded, bytesTotal, `${percentage}%`)
      textProgress.textContent = `Uploaded ${formatBytes(bytesUploaded)} of ${formatBytes(bytesTotal)} (${percentage})`
    },
    onSuccess: function (res) {
      const anchor = document.createElement('a')
      anchor.textContent = `Download ${upload.file.name} (${upload.file.size} bytes)`
      anchor.href = upload.url
      anchor.className = 'btn btn-success'
      uploadList.appendChild(anchor)
      console.log(res)
      reset()
    },
  }

  upload = new tus.Upload(file, options)
  upload.findPreviousUploads().then(() => {
    upload.start()
    uploadIsRunning = true
  })
}

if (!tus.isSupported) {
  alertBox.classList.remove('hidden')
}

if (!toggleBtn) {
  throw new Error('Toggle button not found on this page. Aborting upload-demo. ')
}

toggleBtn.addEventListener('click', (e) => {
  e.preventDefault()

  if (upload) {
    if (uploadIsRunning) {
      upload.abort()
      textHeading.textContent = 'The upload is paused:'
      toggleBtn.textContent = 'resume'
      uploadIsRunning = false
    } else {
      upload.start()
      textHeading.textContent = 'The upload is running:'
      toggleBtn.textContent = 'pause'
      uploadIsRunning = true
    }
  } else if (input.files.length > 0) {
    startUpload()
  } else {
    input.click()
  }
})

/**
 * Turn a byte number into a human readable format.
 * Taken from https://stackoverflow.com/a/18650828
 */
function formatBytes(bytes, decimals = 2) {
  if (bytes === 0) return '0 Bytes'

  const k = 1024
  const dm = decimals < 0 ? 0 : decimals
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB']

  const i = Math.floor(Math.log(bytes) / Math.log(k))

  return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i]
}

input.addEventListener('change', startUpload)