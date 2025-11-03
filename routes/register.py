from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import User
from extensions import db  # ✅ Fixed: import db from extensions, not app
from werkzeug.security import generate_password_hash

register_bp = Blueprint('register_bp', __name__)

@register_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        role = request.form.get('role', 'customer')

        # Check if email or username already exists
        if User.query.filter_by(email=email).first() or User.query.filter_by(username=username).first():
            flash('Email or username already exists', 'danger')
            return redirect(url_for('register_bp.register'))

        # Create new user
        new_user = User(
            email=email,
            username=username,
            role=role,
            profile_image='default.jpg'
        )
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login_bp.login'))

    return render_template('register.html')