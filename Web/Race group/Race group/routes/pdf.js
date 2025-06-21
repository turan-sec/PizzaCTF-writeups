
const express = require('express');
const router = express.Router();
const { requireLogin, requireAdmin } = require('../utils/auth');
const { exec } = require('child_process');
const fs = require('fs');

router.get('/', requireAdmin, (req, res) => {
  res.send(`<form method="POST"><textarea name="content" rows="4" cols="50"></textarea><button>Generate PDF</button></form>`);
});

router.post('/', requireAdmin, (req, res) => {
  const input = req.body.content;
  const htmlPath = `./temp/${Date.now()}.html`;
  const pdfPath = `./temp/${Date.now()}.pdf`;
  fs.mkdirSync('./temp', { recursive: true });
  fs.writeFileSync(htmlPath, `<html><body>${input}</body></html>`);
  exec(`wkhtmltopdf ${htmlPath} ${pdfPath}`, (err) => {
    if (err) return res.send('Error generating PDF');
    res.download(pdfPath);
  });
});

module.exports = router;
