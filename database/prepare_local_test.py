"""Create a separate test database/account for the project-local MySQL instance."""
import secrets

from local_mysql import ROOT, connection

env = ROOT / 'backend/.env.test'
if env.exists():
    raise SystemExit('backend/.env.test already exists; no credentials were changed.')
password = secrets.token_urlsafe(32)
with connection() as conn:
    with conn.cursor() as cursor:
        cursor.execute("SELECT User FROM mysql.user WHERE User='campuslink_test'")
        if cursor.fetchone():
            raise SystemExit('Test account already exists. Configure .env.test manually; no account was changed.')
        cursor.execute('CREATE DATABASE IF NOT EXISTS campuslink_test CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci')
        cursor.execute("CREATE USER 'campuslink_test'@'localhost' IDENTIFIED BY %s", (password,))
        cursor.execute('GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, REFERENCES ON campuslink_test.* TO campuslink_test@localhost')
env.write_text(
    'TEST_DATABASE_HOST=127.0.0.1\nTEST_DATABASE_PORT=3306\n'
    f'TEST_DATABASE_NAME=campuslink_test\nTEST_DATABASE_USER=campuslink_test\nTEST_DATABASE_PASSWORD={password}\n',
    encoding='utf-8',
)
print('Separate test database and credentials prepared. No development tables were modified.')
