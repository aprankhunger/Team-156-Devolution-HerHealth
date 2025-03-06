from flask import Flask, render_template, request, redirect, url_for, session, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate  # Add this line
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from datetime import datetime
from functools import wraps
from firebase_config import auth
from firebase_admin import auth as admin_auth
import pdfkit
from io import BytesIO
import os
from pathlib import Path
import platform

# For Windows development
WINDOWS_PATH = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
# For Linux/Unix deployment
LINUX_PATH = '/usr/bin/wkhtmltopdf'

# Detect the appropriate path based on OS 
if platform.system() == 'Windows':
    KHTMLTOPDF_PATH = WINDOWS_PATH
else:
    KHTMLTOPDF_PATH = LINUX_PATH
config = pdfkit.configuration(wkhtmltopdf=KHTMLTOPDF_PATH)
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///health_profiles.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your-secret-key-here'  # Add this after app initialization
db = SQLAlchemy(app)
migrate = Migrate(app, db)  # Add this line

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Add User model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    firebase_uid = db.Column(db.String(128), unique=True, nullable=False)
    name = db.Column(db.String(100))  # Add this line

class HealthProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    age = db.Column(db.Integer)
    gender = db.Column(db.String(20))
    height = db.Column(db.Float)
    weight = db.Column(db.Float)
    cycle_length = db.Column(db.Integer)
    period_length = db.Column(db.Integer)
    sleep = db.Column(db.Integer)
    water_intake = db.Column(db.Integer)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    activity_level = db.Column(db.String(20))
    symptoms = db.Column(db.String(200))
    conditions = db.Column(db.String(200))
    user_id = db.Column(db.String(128), nullable=False)  # Add this field

    def __repr__(self):
        return f'<HealthProfile {self.name}>'

class PeriodEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(128), db.ForeignKey('user.firebase_uid'), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    flow_level = db.Column(db.String(20), nullable=False)
    symptoms = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class HealthCalculator:
    @staticmethod
    def calculate_bmi(weight, height):
        """Calculate BMI (height in cm, weight in kg)"""
        height_in_meters = height / 100
        bmi = weight / (height_in_meters ** 2)
        return round(bmi, 2)
    
    @staticmethod
    def get_bmi_category(bmi):
        if bmi < 18.5:
            return "Underweight"
        elif 18.5 <= bmi < 25:
            return "Normal weight"
        elif 25 <= bmi < 30:
            return "Overweight"
        else:
            return "Obese"

    @staticmethod
    def calculate_water_recommendation(weight):
        return round(weight * 30)
    
    @staticmethod
    def calculate_sleep_recommendation(age):
        if age < 18:
            return "8-10 hours"
        elif 18 <= age <= 64:
            return "7-9 hours"
        else:
            return "7-8 hours"

    @staticmethod
    def calculate_pcod_risk(age, bmi, cycle_length, period_length, symptoms=None, conditions=None, activity_level=None):
        """Calculate PCOD risk score based on various factors"""
        try:
            risk_score = 0
            
            # BMI scoring
            if bmi >= 30:
                risk_score += 3
            elif bmi >= 25:
                risk_score += 2
            elif bmi < 18.5:
                risk_score += 1
            
            # Menstrual cycle scoring
            if cycle_length:
                cycle_length = int(cycle_length) if isinstance(cycle_length, str) else cycle_length
                if cycle_length > 35 or cycle_length < 21:
                    risk_score += 3
                elif cycle_length > 32 or cycle_length < 24:
                    risk_score += 2
            
            # Period length scoring
            if period_length:
                period_length = int(period_length) if isinstance(period_length, str) else period_length
                if period_length > 7:
                    risk_score += 2
                elif period_length < 2:
                    risk_score += 1

            # Symptoms scoring
            if isinstance(symptoms, list) and symptoms:
                high_risk_symptoms = ['mood_swings', 'fatigue', 'bloating']
                for symptom in symptoms:
                    if symptom in high_risk_symptoms:
                        risk_score += 1

            # Pre-existing conditions scoring
            if isinstance(conditions, list) and conditions:
                high_risk_conditions = ['pcos', 'thyroid', 'diabetes']
                for condition in conditions:
                    if condition in high_risk_conditions:
                        risk_score += 2

            # Activity level scoring
            if activity_level:
                if activity_level == 'sedentary':
                    risk_score += 2
                elif activity_level == 'light':
                    risk_score += 1

            # Final risk assessment
            if risk_score >= 8:
                return "High Risk"
            elif risk_score >= 5:
                return "Moderate Risk"
            else:
                return "Low Risk"
                
        except Exception as e:
            print(f"PCOD Risk Calculation Error: {str(e)}")
            return "Unable to calculate risk"

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/form')
def form():
    return render_template('formindex.html')

@app.route('/submit', methods=['POST'])
@login_required
def submit():
    try:
        form_data = {
            'name': request.form.get('name'),
            'email': request.form.get('email'),
            'age': request.form.get('age'),
            'gender': request.form.get('gender'),
            'height': request.form.get('height'),
            'weight': request.form.get('weight'),
            'cycle_length': request.form.get('cycle_length'),
            'period_length': request.form.get('period_length'),
            'sleep': request.form.get('sleep'),
            'water_intake': request.form.get('water_intake'),
            'activity_level': request.form.get('activity'),
            'symptoms': request.form.getlist('symptoms'),
            'conditions': request.form.getlist('conditions')
        }

        required_fields = ['name', 'email', 'age', 'gender', 'height', 'weight']
        for field in required_fields:
            if not form_data.get(field):
                return render_template('formindex.html', error=f"{field.replace('_', ' ').title()} is required")

        try:
            age = int(form_data['age'])
            height = float(form_data['height'])
            weight = float(form_data['weight'])
            if any(x <= 0 for x in [age, height, weight]):
                return render_template('formindex.html', error="Age, height, and weight must be positive numbers")
        except ValueError:
            return render_template('formindex.html', error="Please enter valid numbers for age, height, and weight")

        calculator = HealthCalculator()
        
        bmi = calculator.calculate_bmi(float(form_data['weight']), float(form_data['height']))
        bmi_category = calculator.get_bmi_category(bmi)
        water_recommendation = calculator.calculate_water_recommendation(float(form_data['weight']))
        sleep_recommendation = calculator.calculate_sleep_recommendation(int(form_data['age']))
        pcod_risk = calculator.calculate_pcod_risk(
            age=int(form_data['age']),
            bmi=bmi,
            cycle_length=form_data.get('cycle_length'),
            period_length=form_data.get('period_length'),
            symptoms=form_data.get('symptoms', []),
            conditions=form_data.get('conditions', []),
            activity_level=form_data.get('activity_level', '')
        )
        
        # Add calculations to form_data
        form_data.update({
            'bmi': bmi,
            'bmi_category': bmi_category,
            'water_recommendation': water_recommendation,
            'sleep_recommendation': sleep_recommendation,
            'pcod_risk': pcod_risk
        })
        
        new_profile = HealthProfile(
            name=form_data['name'],
            email=form_data['email'],
            age=age,
            gender=form_data['gender'],
            height=height,
            weight=weight,
            cycle_length=form_data.get('cycle_length'),
            period_length=form_data.get('period_length'),
            sleep=form_data.get('sleep'),
            water_intake=form_data.get('water_intake'),
            activity_level=form_data['activity_level'],
            symptoms=','.join(form_data['symptoms']) if form_data['symptoms'] else None,
            conditions=','.join(form_data['conditions']) if form_data['conditions'] else None,
            user_id=current_user.firebase_uid  # Changed from session['user_id']
        )

        db.session.add(new_profile)
        db.session.commit()
        # print("Apran")
        # Pass all form data to result template
        return render_template('result.html', profile=form_data)

    except Exception as e:
        return render_template('formindex.html', error="An unexpected error occurred")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            email = request.form['email']
            password = request.form['password']
            
            # Authenticate with Firebase
            firebase_user = auth.sign_in_with_email_and_password(email, password)
            
            # Get or create user in database
            user = User.query.filter_by(firebase_uid=firebase_user['localId']).first()
            if not user:
                user = User(
                    email=email,
                    firebase_uid=firebase_user['localId']
                )
                db.session.add(user)
                db.session.commit()
            
            # Login user with Flask-Login
            login_user(user)
            return redirect(url_for('profile'))
        except Exception as e:
            print(f"Login Error: {str(e)}")  # For debugging
            return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        try:
            email = request.form.get('email')
            password = request.form.get('password')
            
            # Create user in Firebase
            firebase_user = auth.create_user_with_email_and_password(email, password)
            
            # Create user in local database with default name
            default_name = email.split('@')[0]  # Use email username as default name
            user = User(
                email=email,
                firebase_uid=firebase_user['localId'],
                name=default_name
            )
            db.session.add(user)
            db.session.commit()
            
            # Login user
            login_user(user)
            return redirect(url_for('profile'))
        except Exception as e:
            print(f"Signup Error: {str(e)}")
            return render_template('login.html', error="Signup failed")
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/profile')
@login_required
def profile():
    
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    
    # Set default name if none exists
    if not current_user.name:
        current_user.name = current_user.email.split('@')[0]  # Use email username as default
        db.session.commit()
    
    user_profile = HealthProfile.query.filter_by(
        user_id=current_user.firebase_uid
    ).order_by(HealthProfile.id.desc()).first()
    
    period_entries = PeriodEntry.query.filter_by(
        user_id=current_user.firebase_uid
    ).order_by(PeriodEntry.start_date.desc()).all()
    
    if user_profile:
        calculator = HealthCalculator()
        user_profile.pcod_risk = calculator.calculate_pcod_risk(
            age=user_profile.age,
            bmi=calculator.calculate_bmi(user_profile.weight, user_profile.height),
            cycle_length=user_profile.cycle_length,
            period_length=user_profile.period_length,
            symptoms=user_profile.symptoms.split(',') if user_profile.symptoms else [],
            conditions=user_profile.conditions.split(',') if user_profile.conditions else [],
            activity_level=user_profile.activity_level
        )
    
    return render_template('ProfilePage.html', 
                         profile=user_profile, 
                         period_entries=period_entries)

@app.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    if request.method == 'POST':
        try:
            current_user.name = request.form.get('name')
            db.session.commit()
            return redirect(url_for('profile'))
        except Exception as e:
            print(f"Profile update error: {str(e)}")
            return redirect(url_for('profile'))

@app.route('/add_period', methods=['POST'])
@login_required
def add_period():
    try:
        start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d').date()
        end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d').date()
        
        entry = PeriodEntry(
            user_id=current_user.firebase_uid,
            start_date=start_date,
            end_date=end_date,
            flow_level=request.form['flow_level'],
            symptoms=','.join(request.form.getlist('symptoms'))
        )
        
        db.session.add(entry)
        db.session.commit()
        
        return redirect(url_for('profile'))
    except Exception as e:
        print(f"Error adding period entry: {str(e)}")
        return redirect(url_for('profile'))

# Add these imports at the top

@app.route('/download-pdf')
@login_required
def download_pdf():
    try:
        # Get the user's profile
        profile = HealthProfile.query.filter_by(user_id=current_user.firebase_uid).first()
        
        # Get the absolute path to your templates directory
        template_dir = os.path.join(Path(__file__).parent, 'templates')
        static_dir = os.path.join(Path(__file__).parent, 'static')
        
        # Render the template with the profile data
        html = render_template('result.html', profile=profile)
        
        # Configure pdfkit options
        options = {
            'page-size': 'A4',
            'margin-top': '0.75in',
            'margin-right': '0.75in',
            'margin-bottom': '0.75in',
            'margin-left': '0.75in',
            'encoding': "UTF-8",
            'enable-local-file-access': None,
            'custom-header': [('Accept-Encoding', 'gzip')],
            'no-outline': None,
            'quiet': None
        }
        
        # Create temporary HTML file
        temp_html = os.path.join(template_dir, 'temp_report.html')
        with open(temp_html, 'w', encoding='utf-8') as f:
            f.write(html)
        
        # Create PDF using the configuration
        pdf = pdfkit.from_file(temp_html, False, options=options, configuration=config)
        
        # Clean up temporary file
        os.remove(temp_html)
        
        # Create response
        buffer = BytesIO(pdf)
        buffer.seek(0)
        
        return send_file(
            buffer,
            download_name=f'health_report_{current_user.name}.pdf',
            mimetype='application/pdf'
        )
    
    except Exception as e:
        print(f"PDF generation error: {str(e)}")
        return redirect(url_for('profile'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create database tables
    app.run(debug=True)

