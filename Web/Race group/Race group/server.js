const express = require('express');
const session = require('express-session');
const bodyParser = require('body-parser');
const fs = require('fs');
const path = require('path');

const app = express();
app.use(bodyParser.urlencoded({ extended: true }));
app.use(express.static('public'));
app.use(session({ secret: 'supersecret', resave: false, saveUninitialized: true }));
app.set('view engine', 'ejs');

app.use('/', require('./routes/home'));
app.use('/auth', require('./routes/auth')); // All /profile routes are now handled by auth.js
app.use('/profile', require('./routes/profile')); // All /profile routes are now handled by auth.js
app.use('/creator', require('./routes/creator'));
// app.use('/admin', require('./routes/admin')); // Uncomment if you have an admin route

app.listen(80, () => console.log('Web CTF running at http://localhost:80'));
