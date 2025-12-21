"""
添加 pdf_content 字段到 reports 表
支持 SQLite 和 MySQL
"""
from app import create_app, db
from sqlalchemy import text
from sqlalchemy import inspect

app = create_app()
with app.app_context():
    try:
        # Check if column already exists
        inspector = inspect(db.engine)
        columns = [col['name'] for col in inspector.get_columns('reports')]
        
        if 'pdf_content' not in columns:
            # Add pdf_content column
            # SQLite uses BLOB, MySQL uses LONGBLOB
            db_url = str(db.engine.url)
            if 'sqlite' in db_url.lower():
                db.session.execute(text('ALTER TABLE reports ADD COLUMN pdf_content BLOB'))
            else:
                db.session.execute(text('ALTER TABLE reports ADD COLUMN pdf_content LONGBLOB'))
            db.session.commit()
            print("Successfully added pdf_content column to reports table.")
        else:
            print("pdf_content column already exists.")
        
        # Make file_path nullable (SQLite doesn't support MODIFY, so we'll skip this)
        # The model already has nullable=True, so new tables will be correct
        db_url = str(db.engine.url)
        if 'sqlite' not in db_url.lower():
            try:
                db.session.execute(text('ALTER TABLE reports MODIFY COLUMN file_path VARCHAR(255) NULL'))
                db.session.commit()
                print("Successfully updated file_path column to be nullable.")
            except Exception as e:
                print(f"Note: Could not modify file_path (may already be nullable): {e}")
        
    except Exception as e:
        db.session.rollback()
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

