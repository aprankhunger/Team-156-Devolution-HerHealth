from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///health_profiles.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class HealthProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    age = db.Column(db.Integer)
    gender = db.Column(db.String(20))
    height = db.Column(db.Float)
    weight = db.Column(db.Float)
    cycle_length = db.Column(db.Integer)
    period_length = db.Column(db.Integer)
    sleep = db.Column(db.Integer)
    water_intake = db.Column(db.Integer)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<HealthProfile {self.name}>'
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



@app.route('/')
def home():
    return render_template('index.html')

@app.route('/form')
def form():
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
            'height': request.form.get('height'),
            'weight': request.form.get('weight'),
            'cycle_length': request.form.get('cycle_length'),
            'period_length': request.form.get('period_length'),
            'sleep': request.form.get('sleep'),
            'water_intake': request.form.get('water_intake')
        }

        # Validate required fields
        required_fields = ['name', 'email', 'age', 'gender', 'height', 'weight']
        for field in required_fields:
            if not form_data.get(field):
                return render_template('formindex.html', error=f"{field.replace('_', ' ').title()} is required")

        # Validate numeric fields
        try:
            age = int(form_data['age'])
            height = float(form_data['height'])
            weight = float(form_data['weight'])
            if any(x <= 0 for x in [age, height, weight]):
                return render_template('formindex.html', error="Age, height, and weight must be positive numbers")
        except ValueError:
            return render_template('formindex.html', error="Please enter valid numbers for age, height, and weight")

        # Create new health profile
        calculator = HealthCalculator()
        
        # Calculate BMI
        bmi = calculator.calculate_bmi(float(form_data['weight']), float(form_data['height']))
        bmi_category = calculator.get_bmi_category(bmi)
        
        # Calculate recommendations
        water_recommendation = calculator.calculate_water_recommendation(float(form_data['weight']))
        sleep_recommendation = calculator.calculate_sleep_recommendation(int(form_data['age']))
        
        # Add calculations to form_data
        form_data.update({
            'bmi': bmi,
            'bmi_category': bmi_category,
            'water_recommendation': water_recommendation,
            'sleep_recommendation': sleep_recommendation
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
            water_intake=form_data.get('water_intake')
        )

        db.session.add(new_profile)
        db.session.commit()
        print("Apran")
        # Pass all form data to result template
        return render_template('result.html', profile=form_data)

    except Exception as e:
        return render_template('formindex.html', error="An unexpected error occurred")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create database tables
    app.run(debug=True)