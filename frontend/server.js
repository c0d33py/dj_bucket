const express = require('express');
const cors = require('cors');

const app = express();

app.use(cors());

app.get('/', (req, res) => {
    res.send('Hello World!');
});


app.post('/upload', (req, res) => {
    res.sendStatus(200);
});


app.listen(1234, () => {
    console.log('Example app listening on port 8000!');
});