import os
import uuid
from datetime import datetime
from flask import (
    Flask, render_template, request, redirect,
    url_for, flash, send_from_directory, session
)
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from config import Config

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# ✅ Initialize Flask + SQLAlchemy
app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)

# ---------------- Models ----------------
class Owner(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(30))
    houses = db.relationship('House', backref='owner', lazy=True)


class HouseImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(300), nullable=False)
    house_id = db.Column(db.Integer, db.ForeignKey('house.id'), nullable=False)


class House(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    bhk_type = db.Column(db.String(10), nullable=False)  # 1BHK, 2BHK, 3BHK
    rent = db.Column(db.Integer, nullable=False)
    address = db.Column(db.String(300), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    owner_id = db.Column(db.Integer, db.ForeignKey('owner.id'), nullable=False)
    images = db.relationship('HouseImage', backref='house', lazy=True)


class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    house_id = db.Column(db.Integer, db.ForeignKey('house.id'), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(30))
    date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(30), default='pending')
    house = db.relationship('House', backref='booking')   # ✅ fixed

# ---------------- Helper ----------------
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ---------------- Routes ----------------
@app.route('/')
def index():
    latest = House.query.order_by(House.created_at.desc()).limit(6).all()
    return render_template('index.html', latest=latest)


@app.route('/list/<bhk>')
def listing(bhk):
    bhk_map = {'1bhk': '1BHK', '2bhk': '2BHK', '3bhk': '3BHK'}
    bhk_type = bhk_map.get(bhk.lower())
    if not bhk_type:
        return redirect(url_for('index'))
    houses = House.query.filter_by(bhk_type=bhk_type).order_by(House.created_at.desc()).all()
    return render_template('list.html', houses=houses, bhk_type=bhk_type)


@app.route('/house/<int:house_id>')
def house_detail(house_id):
    house = House.query.get_or_404(house_id)
    return render_template('house_detail.html', house=house)


@app.route('/book/<int:house_id>', methods=['POST'])
def book_visit(house_id):
    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    date_str = request.form.get('date')
    try:
        date = datetime.fromisoformat(date_str)
    except Exception:
        flash('Invalid date format. Use YYYY-MM-DDTHH:MM', 'danger')
        return redirect(url_for('house_detail', house_id=house_id))
    booking = Booking(house_id=house_id, name=name, email=email, phone=phone, date=date)
    db.session.add(booking)
    db.session.commit()
    flash('Booking request sent!', 'success')
    return redirect(url_for('house_detail', house_id=house_id))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        phone = request.form.get('phone')
        if Owner.query.filter_by(email=email).first():
            flash('Email already registered', 'danger')
            return redirect(url_for('register'))
        owner = Owner(name=name, email=email, password=password, phone=phone)
        db.session.add(owner)
        db.session.commit()
        flash('Registered! Please login.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        owner = Owner.query.filter_by(email=email, password=password).first()
        if owner:
            session['owner_id'] = owner.id
            session['owner_name'] = owner.name
            flash('Logged in', 'success')
            return redirect(url_for('owner_dashboard'))
        flash('Invalid credentials', 'danger')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out', 'info')
    return redirect(url_for('index'))


@app.route('/owner')
def owner_dashboard():
    if 'owner_id' not in session:
        return redirect(url_for('login'))
    owner = Owner.query.get(session['owner_id'])
    houses = owner.houses
    return render_template('owner_dashboard.html', houses=houses)


@app.route('/owner/add', methods=['GET', 'POST'])
def add_house():
    if 'owner_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        title = request.form.get('title')
        bhk_type = request.form.get('bhk_type')
        rent = request.form.get('rent')
        address = request.form.get('address')
        description = request.form.get('description')

        house = House(
            title=title, bhk_type=bhk_type, rent=int(rent),
            address=address, description=description, owner_id=session['owner_id']
        )
        db.session.add(house)
        db.session.commit()

        files = request.files.getlist('images')
        upload_folder = app.config['UPLOAD_FOLDER']
        os.makedirs(upload_folder, exist_ok=True)
        for f in files:
            if f and allowed_file(f.filename):
                filename = secure_filename(f.filename)
                unique = f"{uuid.uuid4().hex}_{filename}"
                path = os.path.join(upload_folder, unique)
                f.save(path)
                img = HouseImage(filename=unique, house_id=house.id)
                db.session.add(img)
        db.session.commit()
        flash('House added!', 'success')
        return redirect(url_for('owner_dashboard'))

    return render_template('add_house.html')


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Use Render's PORT env variable
    app.run(host="0.0.0.0", port=port)
