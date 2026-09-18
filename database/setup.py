"""Initialize an existing local MySQL server and write backend/.env."""

import argparse
import getpass
import secrets
from pathlib import Path

import pymysql
from dotenv import dotenv_values

ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = ROOT / 'backend' / '.env'


def main():
    parser = argparse.ArgumentParser(description='初始化 CampusLink 数据库和本地配置')
    parser.add_argument('--host', choices=['127.0.0.1', 'localhost'], default='127.0.0.1')
    parser.add_argument('--port', type=int, default=3306)
    parser.add_argument('--user', default='root', help='用于初始化的 MySQL 管理账号')
    args = parser.parse_args()

    if ENV_FILE.exists():
        config = dotenv_values(ENV_FILE)
        with pymysql.connect(
            host=config.get('DATABASE_HOST') or '127.0.0.1',
            port=int(config.get('DATABASE_PORT') or 3306),
            user=config.get('DATABASE_USER'), password=config.get('DATABASE_PASSWORD'),
            database=config.get('DATABASE_NAME'), connect_timeout=5,
        ) as db:
            with db.cursor() as cursor:
                cursor.execute('SELECT 1 FROM `user` LIMIT 1')
        print('已有配置和用户表可用，未覆盖 .env。')
        return

    password = getpass.getpass('MySQL 管理账号密码：')
    app_user = 'campuslink_' + secrets.token_hex(4)
    app_password = secrets.token_urlsafe(32)
    jwt_secret = secrets.token_urlsafe(48)
    with pymysql.connect(
        host=args.host, port=args.port, user=args.user, password=password,
        charset='utf8mb4', connect_timeout=5, autocommit=True,
    ) as db:
        with db.cursor() as cursor:
            sql = (ROOT / 'database' / 'init.sql').read_text(encoding='utf-8')
            sql = '\n'.join(line for line in sql.splitlines() if not line.lstrip().startswith('--'))
            for statement in sql.split(';'):
                if statement.strip():
                    cursor.execute(statement)
            cursor.execute("CREATE USER %s@'localhost' IDENTIFIED BY %s", (app_user, app_password))
            try:
                cursor.execute("GRANT SELECT, INSERT, UPDATE, DELETE ON campuslink.* TO %s@'localhost'", (app_user,))
                content = (
                    f'DATABASE_HOST={args.host}\nDATABASE_PORT={args.port}\n'
                    f'DATABASE_NAME=campuslink\nDATABASE_USER={app_user}\n'
                    f'DATABASE_PASSWORD={app_password}\nJWT_SECRET={jwt_secret}\n'
                )
                with ENV_FILE.open('x', encoding='utf-8') as env:
                    env.write(content)
            except Exception:
                cursor.execute("DROP USER %s@'localhost'", (app_user,))
                raise
    print('数据库初始化完成，已自动生成 backend/.env、应用账号和 JWT 密钥。')


if __name__ == '__main__':
    try:
        main()
    except pymysql.MySQLError as error:
        raise SystemExit(f'MySQL 连接或初始化失败（错误码 {error.args[0]}），请检查服务、账号权限及配置。') from None
