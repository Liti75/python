from flask import Flask, render_template, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from utils import check_strength, is_expired, is_reused, translate, generate_password

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'your-secret-key'
db = SQLAlchemy(app)

from models import PasswordEntry

@app.before_first_request
def create_tables():
    db.create_all()

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    generated_password = None
    language = 'en'

    if request.method == 'POST':
        password = request.form['password']
        language = request.form['language']

        if is_reused(password):
            result = translate("Password reused, please choose a new one", language)
        elif is_expired():
            result = translate("Password expired, please change it", language)
        else:
            strength = check_strength(password)
            if strength == 'Weak':
                result = translate("Password is not strong enough, generating a strong one", language)
                password = generate_password(12)
                generated_password = password
            else:
                result = translate(f"Password is {strength.lower()}", language)

            entry = PasswordEntry(password=password, created_at=datetime.now())
            db.session.add(entry)
            db.session.commit()

    return render_template('index.html', result=result, generated_password=generated_password, language=language)

if __name__ == "__main__":
    app.run(debug=True)
