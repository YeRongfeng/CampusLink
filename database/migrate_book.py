"""Add Book tables without changing existing data. Run with backend/.venv Python."""
import sys
from pathlib import Path
from sqlalchemy import text

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'backend'))
from app.common.database import engine

if __name__ == '__main__':
    sql = (ROOT / 'database/migrations/002_add_book.sql').read_text(encoding='utf-8')
    with engine.begin() as connection:
        name = connection.scalar(text('SELECT DATABASE()'))
        print(f'Applying Book migration to configured database: {name}')
        for statement in sql.split(';'):
            if statement.strip():
                connection.execute(text(statement))
        for table in ('book_listing', 'book_favorite'):
            connection.execute(text(f'SELECT * FROM {table} LIMIT 0'))
    print('Book tables ready; existing data preserved.')
