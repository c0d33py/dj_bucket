const express = require('express');
const cors = require('cors');
const app = express();
const path = require('path');
const router = express.Router();

app.use(cors());

app.use(express.static(path.join(__dirname, 'public')));

router.get('/', function (req, res) {
    res.sendFile(path.join(__dirname + '/index.html'));
});

app.post('/upload', (req, res) => {
    res.sendStatus(200);
});

app.use('/', router);
app.listen(1234, () => {
    console.log('Example app listening on port 8000!');
});