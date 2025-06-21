
const express = require('express');
const router = express.Router();
const fs = require('fs');
const { exec } = require('child_process');
const { requireCreator } = require('../utils/auth');

router.get('/pdf', requireCreator, (req, res) => {
  res.render('pdf');
});

router.post('/pdf', requireCreator, (req, res) => {
  const content = req.body.content;
  const name = Date.now();
  const htmlFile = `./temp/${name}.html`;
  const pdfFile = `./temp/${name}.pdf`;

  fs.mkdirSync('./temp', { recursive: true });
  fs.writeFileSync(htmlFile, `<html><body>${content}</body></html>`);

  exec(`wkhtmltopdf --enable-local-file-access ${htmlFile} ${pdfFile}`, (err) => {
    if (err) return res.send('Error generating PDF');
    res.download(pdfFile);
  });
});

module.exports = router;
