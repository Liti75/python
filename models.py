from app import db

class PasswordEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    password = db.Column(db.String(255), unique=False, nullable=False)
    created_at = db.Column(db.DateTime, default=None)
