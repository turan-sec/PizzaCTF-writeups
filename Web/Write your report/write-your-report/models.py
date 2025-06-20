import sqlite3
import hashlib
import os

# Path to the SQLite database file
db_path = 'shaptolisec.db'


def init_db():
    """
    Initialize the database:
    1) Remove any existing DB file for a clean start
    2) Create tables with strict role constraints
    3) Install trigger to forbid role changes
    4) Seed default users with MD5-hashed passwords
    """
    # 1) Remove old database
    if os.path.exists(db_path):
        os.remove(db_path)

    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # 2) Create users table with CHECK constraint on role
    c.execute('''
        CREATE TABLE users (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT    UNIQUE NOT NULL,
            password TEXT    NOT NULL,
            role     TEXT    NOT NULL
                CHECK(role IN ('manager','pentester','teamlead','moderator'))
        )
    ''')

    # 3) Trigger to prevent any UPDATE on `role` column
#    c.execute('''
#        CREATE TRIGGER IF NOT EXISTS prevent_role_change
#        BEFORE UPDATE OF role ON users
#        WHEN OLD.role <> NEW.role
#        BEGIN
#            SELECT RAISE(ABORT, 'Role modification forbidden');
#        END;
#    ''')


    c.execute('DROP TRIGGER IF EXISTS forbid_role_update;')

    # Create contacts table
    c.execute('''
        CREATE TABLE contacts (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            email   TEXT,
            message TEXT
        )
    ''')

    # Create reports table
    c.execute('''
        CREATE TABLE reports (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            author_id  INTEGER,
            title      TEXT,
            content    TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(author_id) REFERENCES users(id)
        )
    ''')

    # 4) Seed default users (passwords are MD5 of their plaintext)
    seed_users = [
        ('pmanager',  hashlib.md5('joyland1'.encode()).hexdigest(),               'manager'),
        ('appsecchi', hashlib.md5('AppSec1s_MyW1fe&*$'.encode()).hexdigest(),    'pentester'),
        ('teamlead1', hashlib.md5('Il1k3freepizzzzzzaa#$%'.encode()).hexdigest(), 'teamlead'),
        ('mod1',       hashlib.md5('Moderator#Pass1534'.encode()).hexdigest(),     'moderator'),
    ]
    c.executemany(
        'INSERT INTO users(username, password, role) VALUES(?, ?, ?)',
        seed_users
    )

    conn.commit()
    conn.close()
