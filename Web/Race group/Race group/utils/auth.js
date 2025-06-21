
module.exports = {
  requireLogin: (req, res, next) => {
    if (!req.session.user) return res.redirect('/auth/login');
    next();
  },
  requireCreator: (req, res, next) => {
    if (!req.session.user || req.session.user.role !== 'creator') return res.send('403 Forbidden');
    next();
  }
};
