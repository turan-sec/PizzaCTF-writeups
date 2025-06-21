const express = require('express');
const router = express.Router();
const fs = require('fs');
const { v4: uuidv4 } = require('uuid');
const { requireLogin } = require('../utils/auth');

const USERS = './users.json';
const EMAILS = './emails.json';

let users = JSON.parse(fs.existsSync(USERS) ? fs.readFileSync(USERS) : '[]');
let emails = JSON.parse(fs.existsSync(EMAILS) ? fs.readFileSync(EMAILS) : '[]');

function saveUsers(data) {
  fs.writeFileSync(USERS, JSON.stringify(data, null, 2));
}

router.get('/', requireLogin, (req, res) => {
  res.render('home', { user: req.session.user });
});

router.get('/register', (req, res) => res.render('register'));
router.post('/register', (req, res) => {
  const { username, email, password } = req.body;
  if (users.find(u => u.email === email)) return res.send('Email already exists');
  const role = 'user';
  const user = { id: uuidv4(), username, email, password, role };
  users.push(user);
  saveUsers(users);
  req.session.user = user;
  res.redirect('/');
});

router.get('/login', (req, res) => res.render('login'));
router.post('/login', (req, res) => {
  const user = users.find(u => u.email === req.body.email && u.password === req.body.password);
  if (!user) return res.send('Invalid login');
  req.session.user = user;
  res.redirect('/profile');
});

router.get('/forgot', requireLogin, (req, res) => res.render('forgot'));
router.post('/forgot', requireLogin, (req, res) => {
  const target = users.find(u => u.email === req.body.targetEmail);
  if (!target) return res.send('User not found');

  const word = 'reset';
  const salt = 'xx';
  const seed = Math.floor(Date.now() / 500); // weak time window
  const token = `${word}-${(seed + salt).toString(36)}`;

  // 💣 TRUE race condition: read-modify-write without locking
  let emailsNow;
  try {
    emailsNow = JSON.parse(fs.readFileSync(EMAILS));
  } catch {
    emailsNow = [];
  }

  emailsNow.push({ token, uid: target.id });

  // 💥 Both processes write based on old copy
  fs.writeFileSync(EMAILS, JSON.stringify(emailsNow, null, 2));

  res.redirect('/auth/inbox');
});


router.get('/inbox', requireLogin, (req, res) => {
  // 🔄 Always reload emails from file
  let freshEmails = [];
  try {
    freshEmails = JSON.parse(fs.readFileSync(EMAILS));
  } catch {}

  const myEmails = freshEmails.filter(e => {
    const user = users.find(u => u.id === e.uid);
    return user && user.email === req.session.user.email;
  });

  res.render('emails', { emails: myEmails });
});


router.get('/reset/:token', (req, res) => {
  let freshEmails = [];
try {
  freshEmails = JSON.parse(fs.readFileSync(EMAILS));
} catch {}

const entry = freshEmails.find(e => e.token === req.params.token);
  if (!entry) return res.send('Invalid token');

  const user = users.find(u => u.id === entry.uid);
  if (!user) return res.send('No user for token');

  res.render('reset', { token: req.params.token, username: user.username });
});

router.post('/reset/:token', (req, res) => {
  const { username, password } = req.body;

  let freshEmails = [];
try {
  freshEmails = JSON.parse(fs.readFileSync(EMAILS));
} catch {}

const entry = freshEmails.find(e => e.token === req.params.token);
  if (!entry) return res.send('Invalid token');

  const user = users.find(u => u.username === username);
  if (!user) return res.send('Invalid username');

  if (user.id !== entry.uid) return res.send('Token does not match username');

  user.password = password;
  saveUsers(users);

  // Optional: remove used token
  emails = emails.filter(e => e.token !== req.params.token);
  fs.writeFileSync(EMAILS, JSON.stringify(emails, null, 2));

  res.send('✅ Password updated successfully');
});

module.exports = router;

router.get('/login', (req, res) => {
  res.render('login');
});

router.post('/login', (req, res) => {
  const { email, password } = req.body;
  const user = users.find(u => u.email === email && u.password === password);
  if (!user) return res.send('Invalid credentials');
  req.session.user = user;
  res.redirect('/');
});

