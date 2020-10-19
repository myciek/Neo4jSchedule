from flask import Flask, render_template, redirect, session, url_for, flash, request
from data.db_session import db_auth
from services.accounts_service import create_user, login_user, get_profile
import os

app = Flask(__name__)


@app.route('/')
def index():
    return render_template("home/index.html")


@app.route('/accounts/register', methods=['GET'])
def register_get():
    return render_template("accounts/register.html")


@app.route('/accounts/register', methods=['POST'])
def register_post():
    # Get the form data from register.html
    name = request.form.get('name')
    email = request.form.get('email').lower().strip()
    company = request.form.get('company').strip()
    password = request.form.get('password').strip()
    confirm = request.form.get('confirm').strip()
    # Check for blank fields in the registration form
    if not name or not email or not company or not password or not confirm:
        flash("Please populate all the registration fields", "error")
        return render_template("accounts/register.html", name=name, email=email, company=company, password=password,
                               confirm=confirm)
    # Check if password and confirm match
    if password != confirm:
        flash("Passwords do not match")
        return render_template("accounts/register.html", name=name, email=email, company=company)
    # Create the user
    user = create_user(name, email, company, password)
    # Verify another user with the same email does not exist
    if not user:
        flash("A user with that email already exists.")
        return render_template("accounts/register.html", name=name, email=email, company=company)
    return render_template("accounts/register.html")


if __name__ == '__main__':
    app.run(debug=True)
