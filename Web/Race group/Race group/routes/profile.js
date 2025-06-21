const express = require('express');
const router = express.Router();
const { requireLogin } = require('../utils/auth'); // Assuming this middleware checks session/login

// Profile page with auth
router.get('/', requireLogin, (req, res) => {
  res.render('profile', { user: req.session.user });
});

module.exports = router;
