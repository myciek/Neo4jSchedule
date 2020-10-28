from flask import Flask, render_template, redirect, session, url_for, flash, request
from data.db_session import db_auth
from services.accounts_service import create_user, login_user, get_profile, update_user, find_user
from services.lesson_types_services import create_lesson_type
from services.lessons_services import get_lesson_initial_info, create_lesson
from services.classes import TypeEnum, User
import os
import json
from services.studies_types_services import create_studies_type

app = Flask(__name__)
app.secret_key = os.urandom(24)
graph = db_auth()


@app.route('/')
def index():
    return render_template("home/index.html")


@app.route('/accounts/register', methods=['GET'])
def register_get():
    return render_template("accounts/register.html")


@app.route('/accounts/register', methods=['POST'])
def register_post():
    name = request.form.get('name')
    email = request.form.get('email').lower().strip()
    if request.form.get('is_teacher'):
        is_teacher = True
    else:
        is_teacher = False
    password = request.form.get('password').strip()
    confirm = request.form.get('confirm').strip()
    if not name or not email or not password or not confirm:
        flash("Please populate all the registration fields", "error")
        return render_template("accounts/register.html", name=name, email=email, is_teacher=is_teacher,
                               password=password, confirm=confirm)
    if password != confirm:
        flash("Passwords do not match")
        return render_template("accounts/register.html", name=name, email=email, is_teacher=is_teacher)
    user = create_user(name, email, is_teacher, password)
    if not user:
        flash("A user with that email already exists.")
        return render_template("accounts/register.html", name=name, email=email, is_teacher=is_teacher)
    return render_template("accounts/register.html")


@app.route('/accounts/login', methods=['GET'])
def login_get():
    if "usr" in session:
        return redirect(url_for("profile_get"))
    else:
        return render_template("accounts/login.html")


@app.route('/accounts/login', methods=['POST'])
def login_post():
    email = request.form['email']
    password = request.form['password']
    if not email or not password:
        return render_template("accounts/login.html", email=email, password=password)
    user = login_user(email, password)
    if not user:
        flash("No account for that email address or the password is incorrect", "error")
        return render_template("accounts/login.html", email=email, password=password)
    usr = request.form["email"]
    session["usr"] = usr
    return redirect(url_for("lessons_get"))


@app.route('/accounts/profile', methods=['GET'])
def profile_get():
    if "usr" in session:
        usr = session["usr"]
        session["usr"] = usr
        user_profile = get_profile(usr)
        return render_template("accounts/index.html", user_profile=user_profile)
    else:
        return redirect(url_for("login_get"))


@app.route('/accounts/profile', methods=['POST'])
def profile_post():
    if "usr" in session:
        usr = session["usr"]
        name = request.form["name"]
        email = request.form["email"]
        updated_user = update_user(name, email, usr)
        session["usr"] = updated_user["email"]
        user_profile = get_profile(session["usr"])
        return render_template("accounts/index.html", user_profile=user_profile)
    else:
        return redirect(url_for("login_get"))


@app.route('/lessons', methods=['GET'])
def lessons_get():
    if "usr" not in session:
        return redirect(url_for("login_get"))
    info = get_lesson_initial_info()
    return render_template("lessons/index.html", info=info)


@app.route('/lessons', methods=['POST'])
def lessons_post():
    if "usr" not in session:
        return redirect(url_for("login_get"))
    name = request.form["name"]
    lesson_type = request.form["lesson_type"]
    start_time = request.form["start_time"]
    end_time = request.form["end_time"]
    frequency = request.form["frequency"]
    teacher = request.form["teacher"]
    studies_type = request.form["studies_type"]
    group = request.form["group"]
    section = request.form["section"]
    owner = session["usr"]
    lesson = create_lesson(name, lesson_type, start_time, end_time, frequency, teacher, studies_type, group, section,
                           owner)
    return redirect(url_for("lessons_get"))


@app.route('/lessons/studies_type', methods=['GET'])
def studies_type_get():
    if "usr" not in session:
        return redirect(url_for("login_get"))
    info = {
        "types": TypeEnum._member_names_
    }
    return render_template("lessons/studies_type.html", info=info)


@app.route('/lessons/studies_type', methods=['POST'])
def studies_type_post():
    name = request.form["name"]
    abbreviation = request.form["abbreviation"]
    type = request.form["type"]
    studies_type = create_studies_type(name, abbreviation, type)
    if not studies_type:
        flash("Studia takiego typu już istnieją")
        info = {
            "types": TypeEnum._member_names_
        }
        return render_template("lessons/studies_type.html", info=info)
    return redirect(url_for("lessons_get"))


@app.route('/lessons/lesson_type', methods=['GET'])
def lesson_type_get():
    if "usr" not in session:
        return redirect(url_for("login_get"))
    return render_template("lessons/lesson_type.html")


@app.route('/lessons/lesson_type', methods=['POST'])
def lesson_type_post():
    name = request.form["name"]
    color = request.form["color"]
    lesson_type = create_lesson_type(name, color)
    if not lesson_type:
        flash("Nazwa i kolor muszą być unikalne")
        return render_template("lessons/lesson_type.html")
    return redirect(url_for("lessons_get"))


@app.route('/calendar', methods=['GET'])
def calendar_get():
    if "usr" not in session:
        return redirect(url_for("login_get"))
    return render_template("calendar/calendar.html")


@app.route('/data')
def data_get():
    data = []
    user = User.match(graph, session["usr"]).first()
    lessons = user.lessons_own
    for lesson in lessons:
        for lesson_type in lesson.lesson_type:
            lesson_data = {
                "title": f"{lesson.name} {lesson_type.name}",
                "start": lesson.start_time,
                "end": lesson.end_time,
                "color": lesson_type.color
            }
            data.append(lesson_data)

    return json.dumps(data)


@app.route('/accounts/logout')
def logout():
    session.pop("usr", None)
    flash("You have successfully been logged out.", "info")
    return redirect(url_for("login_get"))


if __name__ == '__main__':
    app.run(debug=True)
