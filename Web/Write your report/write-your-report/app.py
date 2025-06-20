import os
import sqlite3
import subprocess
from functools import wraps
import hashlib

from flask import (
    Flask, render_template, request, redirect, url_for,
    session, send_file, g
)
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash
from models import init_db

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE']   = True

# --------------------
# Configuration
# --------------------
DATABASE = 'shaptolisec.db'
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
init_db()

# --------------------
# Database helpers
# --------------------
def get_db():
    """
    Opens a new database connection (or returns the existing one)
    with WAL journaling, a long busy timeout, and NORMAL sync.
    """
    db = getattr(g, '_database', None)
    if db is None:
        db = sqlite3.connect(
            DATABASE,
            timeout=30.0,            
            check_same_thread=False  
        )
        db.row_factory = sqlite3.Row

        db.execute("PRAGMA journal_mode = WAL;")
        
        db.execute("PRAGMA synchronous = NORMAL;")
       
        db.execute("PRAGMA busy_timeout = 30000;")

        g._database = db
    return db

@app.teardown_appcontext
def close_db(exception):
    """Close the DB connection at the end of the request."""
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def login_required(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return wrapped

def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if session.get('role') not in roles:
                return "Unauthorized", 403
            return f(*args, **kwargs)
        return wrapped
    return decorator

@app.route('/')
def index():
    if 'user' in session:
        return render_template('index.html', logged_in=True)
    return render_template('index.html', logged_in=False)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        u = request.form['username']
        p = request.form['password']

        md5p = hashlib.md5(p.encode()).hexdigest()

        conn = get_db()
        user = conn.execute(
            'SELECT * FROM users WHERE username = ?',
            (u,)
        ).fetchone()

        if user and user['password'] == md5p:
            session['user'] = user['id']
            session['role'] = user['role']
            return redirect(url_for('dashboard'))

        error = 'Invalid credentials'

    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/contact', methods=['GET','POST'])
def contact():
    if request.method == 'POST':
        email = request.form['email']
        msg   = request.form['message']
        sql = f"INSERT INTO contacts(email, message) VALUES('{email}', ?)"

        conn = get_db()
        conn.execute(sql, (msg,))
        conn.commit()

        return render_template('contact.html', success=True)
    return render_template('contact.html')


@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/reports')
@login_required
def reports():
    conn = get_db()
    if session['role'] in ['manager', 'moderator', 'teamlead']:
        rows = conn.execute('SELECT r.*, u.username FROM reports r JOIN users u ON r.author_id=u.id').fetchall()
    elif session['role'] == 'pentester':
        rows = []
    else:
        rows = conn.execute('SELECT r.*, u.username FROM reports r JOIN users u ON r.author_id=u.id WHERE author_id=?', (session['user'],)).fetchall()
    return render_template('reports.html', reports=rows)

@app.route('/report/new', methods=['GET','POST'])
@login_required
@role_required('pentester','teamlead','moderator')
def new_report():
    if request.method == 'POST':
        title = request.form['title']; content = request.form['content']
        conn = get_db(); conn.execute('INSERT INTO reports(author_id, title, content) VALUES(?,?,?)', (session['user'], title, content)); conn.commit()
        return redirect(url_for('reports'))
    return render_template('report_form.html')

@app.route('/users')
@login_required
@role_required('teamlead','moderator')
def users():
    conn = get_db()
    rows = conn.execute(
        "SELECT id, username, role FROM users WHERE role!='moderator'"
    ).fetchall()
    return render_template('users.html', users=rows)

@app.route('/user/edit/<int:uid>')
@login_required
@role_required('teamlead','moderator')
def edit_user(uid):
    conn = get_db()
    user = conn.execute(
        "SELECT id, username, role FROM users WHERE id=?",
        (uid,)
    ).fetchone()
    if not user:
        abort(404)
    return render_template('user_edit.html', user=user)


@app.route('/user/update/<int:uid>', methods=['POST'])
@login_required
@role_required('teamlead','moderator')
def update_user(uid):
    new_role = request.form['role']
    conn = get_db()
    conn.execute("UPDATE users SET role=? WHERE id=?", (new_role, uid))
    conn.commit()
    return redirect(url_for('users'))

@app.route('/admin/backup')
@login_required
@role_required('moderator')
def backup():
    files = []
    for root, dirs, fs in os.walk('.'):
        for f in fs:
            if f.endswith(('app.py')):
                files.append(os.path.join(root, f))
    return render_template('backup.html', files=files)
    files = ['app.py'] if os.path.exists('app.py') else []
    return render_template('backup.html', files=files)

@app.route('/admin/backup/view')
@login_required
@role_required('moderator')
def backup_view():
    from flask import abort
    import os
    raw = request.args.get('file', '')
    base = os.path.abspath(os.getcwd())
    path = os.path.abspath(os.path.join(base, raw))
    if not path.startswith(base + os.sep):
        abort(403)

    _, ext = os.path.splitext(path)
    if ext.lower() not in {'.py', '.html', '.css', '.js'}:
        abort(403)

    try:
        with open(path, 'r', encoding='utf-8') as f:
            code = f.read()
    except OSError:
        abort(404)

    return render_template('backup_view.html', code=code)

@app.route('/admin/pdf/validate', methods=['GET','POST'])
@login_required
@role_required('moderator')
def pdf_validate():
    if request.method == 'POST':
        f = request.files['pdf']; fn = secure_filename(f.filename); path = os.path.join(UPLOAD_FOLDER, fn); f.save(path)
        cmd = f"pdfinfo '{path}' | grep Creator | cut -d':' -f2 | xargs -I{{}} sh -c \"echo {{}}\""
        out = subprocess.getoutput(cmd)
        return render_template('pdf_validate.html', result=out)
    return render_template('pdf_validate.html')

@app.route('/admin/docx/convert', methods=['POST'])
@login_required
@role_required('moderator')
def docx_convert():
    f = request.files['docx']; fn = secure_filename(f.filename); ip = os.path.join(UPLOAD_FOLDER, fn); f.save(ip)
    op = ip.rsplit('.',1)[0] + '.pdf'; os.system(f"docx2pdf {ip} {op}")
    return send_file(op, as_attachment=True)

@app.route('/notes', methods=['GET'])
@login_required
@role_required('teamlead')
def notes():
    # default “hidden” reminder comment for teamleads
    default_comment = '<!-- I always forget my password, so i can use this link to get my password before login :) /static/reports/random_x353yz/my-p4s5.txt -->'
    return render_template('notes.html', note=default_comment)

if __name__ == '__main__':
    app.run(debug=False)
