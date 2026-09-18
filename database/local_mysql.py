"""Manage this repository's optional Windows MySQL ZIP development instance.

Usage: backend/.venv/Scripts/python.exe database/local_mysql.py setup|start|stop
Download and extract the official mysql-8.4.11-winx64.zip into .local first.
Never touches an existing installation or overwrites an existing backend/.env.
"""

import argparse
import secrets
import socket
import subprocess
import time
from pathlib import Path

import pymysql

ROOT = Path(__file__).resolve().parents[1]
LOCAL = ROOT / '.local'
MYSQL = LOCAL / 'mysql-8.4.11-winx64'
CONFIG = LOCAL / 'mysql.ini'
ADMIN = LOCAL / 'mysql-admin.cnf'
DATA = LOCAL / 'mysql-data'


def connection():
    return pymysql.connect(read_default_file=str(ADMIN), connect_timeout=2)


def start(init_file: Path | None = None):
    if not CONFIG.exists() or not ADMIN.exists():
        raise SystemExit('Run setup first.')
    with socket.socket() as sock:
        if sock.connect_ex(('127.0.0.1', 3306)) == 0:
            raise SystemExit('Port 3306 is already occupied; no process was changed.')
    # Keep argv ASCII too: MySQL's Windows argument parser mishandles Unicode paths.
    args = [str((MYSQL / 'bin/mysqld.exe').relative_to(ROOT)), '--defaults-file=.local/mysql.ini']
    if init_file:
        # mysqld resolves init-file against datadir after startup.
        args.append(f'--init-file=../{init_file.name}')
    with (LOCAL / 'mysql-process.log').open('ab') as log:
        process = subprocess.Popen(
            args, cwd=ROOT, stdout=log, stderr=log, creationflags=subprocess.CREATE_NO_WINDOW
        )
    for _ in range(60):
        if process.poll() is not None:
            raise SystemExit('MySQL exited; inspect .local/mysql-error.log and mysql-process.log.')
        try:
            with connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute('SELECT VERSION()')
                    print(f'MySQL {cursor.fetchone()[0]} ready on 127.0.0.1:3306')
            return
        except pymysql.MySQLError:
            time.sleep(0.5)
    raise SystemExit('Startup timed out; inspect .local/mysql-error.log before retrying.')


def setup():
    if any(path.exists() for path in (DATA, CONFIG, ADMIN, ROOT / 'backend/.env')):
        raise SystemExit('Existing data/config found. Setup refuses to overwrite; use start instead.')
    if not (MYSQL / 'bin/mysqld.exe').exists():
        raise SystemExit('Extract the official MySQL 8.4.11 Windows ZIP into .local first.')
    with socket.socket() as sock:
        if sock.connect_ex(('127.0.0.1', 3306)) == 0:
            raise SystemExit('Port 3306 is in use. Configure the existing server manually instead.')
    admin_password = secrets.token_urlsafe(32)
    app_password = secrets.token_urlsafe(32)
    CONFIG.write_text(
        f'[mysqld]\nbasedir="{MYSQL.as_posix()}"\ndatadir="{DATA.as_posix()}"\n'
        'port=3306\nbind-address=127.0.0.1\nmysqlx=0\n'
        'character-set-server=utf8mb4\ncollation-server=utf8mb4_0900_ai_ci\n'
        # Windows MySQL reads option-file paths using the system ANSI code page.
        f'log-error="{(LOCAL / "mysql-error.log").as_posix()}"\n', encoding='mbcs'
    )
    ADMIN.write_text(
        f'[client]\nhost=127.0.0.1\nport=3306\nuser=root\npassword={admin_password}\n',
        encoding='utf-8',
    )
    subprocess.run(
        [str((MYSQL / 'bin/mysqld.exe').relative_to(ROOT)), '--defaults-file=.local/mysql.ini', '--initialize'],
        cwd=ROOT, check=True, creationflags=subprocess.CREATE_NO_WINDOW,
    )
    bootstrap = LOCAL / 'mysql-bootstrap.sql'
    bootstrap.write_text(
        f"ALTER USER 'root'@'localhost' IDENTIFIED BY '{admin_password}';\n"
        f"CREATE USER 'campuslink'@'localhost' IDENTIFIED BY '{app_password}';\n"
        "GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, ALTER, INDEX, REFERENCES "
        "ON campuslink.* TO 'campuslink'@'localhost';\n", encoding='utf-8'
    )
    start(bootstrap)
    with connection() as conn:
        with conn.cursor() as cursor:
            sql = (ROOT / 'database/init.sql').read_text(encoding='utf-8')
            sql = '\n'.join(line for line in sql.splitlines() if not line.lstrip().startswith('--'))
            for statement in sql.split(';'):
                if statement.strip():
                    cursor.execute(statement)
    bootstrap.unlink()
    (ROOT / 'backend/.env').write_text(
        'DATABASE_HOST=127.0.0.1\nDATABASE_PORT=3306\nDATABASE_NAME=campuslink\n'
        f'DATABASE_USER=campuslink\nDATABASE_PASSWORD={app_password}\n'
        f'JWT_SECRET={secrets.token_urlsafe(48)}\n', encoding='utf-8'
    )
    print('Database initialized; backend/.env generated. Credentials were not printed.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['setup', 'start', 'stop'])
    action = parser.parse_args().action
    if action == 'setup':
        setup()
    elif action == 'start':
        start()
    else:
        with connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute('SHUTDOWN')
        print('Shutdown requested for the project MySQL instance.')
