from app import create_app, db
from app.models.report import Report

app = create_app()
with app.app_context():
    db.create_all()
    print("Reports table created.")
