from flask import Flask, render_template, request, redirect, url_for
from models import db, HealthProfile
from datetime import datetime

app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///health_profiles.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)

@app.route('/')
def home():
    return render_template('formindex.html')

@app.route('/submit', methods=['POST'])
def submit():
    try:
        # Get form data
        form_data = {
            'name': request.form.get('name'),
            'email': request.form.get('email'),
            'age': request.form.get('age'),
            'gender': request.form.get('gender'),
            'height': request.form.get('height')
        }

        # Validate required fields
        if not all([form_data['name'], form_data['email'], form_data['age'], 
                   form_data['gender'], form_data['height']]):
            raise ValueError("All fields are required")

        # Create new health profile
        new_profile = HealthProfile(
            name=form_data['name'],
            email=form_data['email'],
            age=int(form_data['age']),
            gender=form_data['gender'],
            height=float(form_data['height'])
        )

        # Add to database
        db.session.add(new_profile)
        db.session.commit()

        return render_template('result.html', form_data=form_data)
    
    except ValueError as e:
        return f"Validation error: {str(e)}"
    except Exception as e:
        return f"An error occurred: {str(e)}"

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create database tables
    app.run(debug=True)