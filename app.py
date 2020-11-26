from flask import Flask, render_template, redirect, session, url_for, flash, request
from py2neo import NodeMatcher

from data.db_session import db_auth
from services.accounts_service import create_user, login_user, get_profile, update_user, is_admin, \
    get_teachers_for_approval_names, approve_teachers
from services.lessons_service import get_lesson_initial_info, create_lesson, update_lesson, find_lesson_type, \
    get_lessons_list, add_lesson_to_user
from services.classes import User, Lesson
import os
import json
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config["SECURITY_PASSWORD_SALT"] = os.urandom(24)
app.config["MAIL_DEFAULT_SENDER"] = "podwoozka@gmail.com"
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 465
app.config["MAIL_USE_TLS"] = False
app.config["MAIL_USE_SSL"] = True
app.config["MAIL_USERNAME"] ="yourmail"
app.config["MAIL_PASSWORD"] = "your password"

mail = Mail(app)
graph = db_auth()


def generate_confirmation_token(email):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    return serializer.dumps(email, salt=app.config['SECURITY_PASSWORD_SALT'])


def confirm_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    try:
        email = serializer.loads(
            token,
            salt=app.config['SECURITY_PASSWORD_SALT'],
            max_age=expiration
        )
    except:
        return False
    return email


def send_email(to, subject, template):
    msg = Message(
        subject,
        recipients=[to],
        html=template,
        sender=app.config["MAIL_DEFAULT_SENDER"]
    )
    mail.send(msg)
    print("wyslane")


@app.route('/')
def index():
    return redirect(url_for("register_get"))


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
    token = generate_confirmation_token(email)
    confirm_url = url_for("confirm_email_get", token=token, _external=True)
    html = render_template("accounts/email.html", confirm_url=confirm_url)
    send_email(email, "Potwierdz adres email", html)

    return render_template("accounts/register.html")


@app.route('/accounts/confirm/<token>', methods=['GET'])
def confirm_email_get(token):
    try:
        email = confirm_token(token)
    except:
        flash("Link aktywacyjny jest nieprawidlowy lub wygasl.")
    user = User.match(graph, f"{email}").first()
    if user.active:
        flash("Konto juz aktywowane.")
    else:
        user.active = True
        graph.push(user)
    return redirect(url_for("login_get"))


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
        flash("Nie znaleziono aktywnego konta z takimi danymi, spróbuj potwierdzic email lub wpisać inne dane.",
              "error")
        return render_template("accounts/login.html", email=email, password=password)
    usr = request.form["email"]
    session["usr"] = usr
    return redirect(url_for("calendar_get"))


@app.route('/accounts/profile', methods=['GET'])
def profile_get():
    if "usr" in session:
        usr = session["usr"]
        if is_admin(usr):
            return redirect(url_for("admin_get"))
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


@app.route('/accounts/admin', methods=['GET'])
def admin_get():
    if "usr" in session:
        if is_admin(session["usr"]):
            teachers = get_teachers_for_approval_names()
            return render_template("accounts/admin.html", teachers=teachers)
        else:
            return redirect(url_for("profile_get"))
    else:
        return redirect(url_for("login_get"))


@app.route('/accounts/admin', methods=['POST'])
def admin_post():
    if "usr" in session:
        if is_admin(session["usr"]):
            approved_teachers = request.form.getlist("teachers")
            approve_teachers(approved_teachers)
            teachers = get_teachers_for_approval_names()
            return render_template("accounts/admin.html", teachers=teachers)
        else:
            return redirect(url_for("profile_get"))
    else:
        return redirect(url_for("login_get"))


@app.route('/accounts/lesson_types', methods=['GET'])
def change_lesson_type_color_get():
    if "usr" in session:
        matcher = NodeMatcher(graph)
        user = matcher.match("user", email=session["usr"]).first()
        info = json.loads(user["lesson_types"])
        return render_template("accounts/color_change.html", info=info)
    return redirect(url_for("login_get"))


@app.route('/accounts/lesson_types', methods=['POST'])
def change_lesson_type_color_post():
    if "usr" in session:
        matcher = NodeMatcher(graph)
        user = matcher.match("user", email=session["usr"]).first()
        lesson_types = json.loads(user["lesson_types"])
        key_to_change = next((name for name, color in lesson_types.items() if color == request.form["name"]), None)
        lesson_types[key_to_change] = request.form["color"]
        user["lesson_types"] = json.dumps(lesson_types)
        graph.push(user)
        return redirect(url_for("change_lesson_type_color_get"))
    return redirect(url_for("login_get"))


@app.route('/lessons', methods=['GET'])
def lessons_get():
    if "usr" not in session:
        return redirect(url_for("login_get"))
    info = get_lesson_initial_info(session["usr"])
    return render_template("lessons/index.html", info=info)


@app.route('/lessons', methods=['POST'])
def lessons_post():
    if "usr" not in session:
        return redirect(url_for("login_get"))
    name = request.form["name"]
    lesson_type = request.form.get("lesson_type")
    start_time = request.form["start_time"]
    end_time = request.form["end_time"]
    frequency = request.form.get("frequency")
    block = request.form.get("block")
    teacher = request.form.get("teacher")
    studies_type = request.form["studies_type"]
    group = request.form["group"]
    section = request.form["section"]
    owner = session["usr"]
    if not lesson_type or not frequency or not teacher or not block:
        flash("Wybierz element z każdej listy!")
        info = get_lesson_initial_info(session["usr"])
        return render_template("lessons/index.html", info=info, name=name, start_time=start_time, end_time=end_time,
                               group=group, section=section, studies_type=studies_type)
    lesson = create_lesson(name, lesson_type, start_time, end_time, frequency, block, teacher, studies_type, group, section,
                           owner)
    return redirect(url_for("calendar_get"))


@app.route('/calendar', methods=['GET'])
def calendar_get():
    if "usr" not in session:
        return redirect(url_for("login_get"))
    return render_template("calendar/calendar.html")


@app.route('/data', methods=['GET'])
def data_get():
    data = []
    user = User.match(graph, session["usr"]).first()
    lessons = user.lessons_own
    lesson_types = json.loads(user.lesson_types)
    for lesson in lessons:
        lesson_type = find_lesson_type(lesson_types, lesson.__ogm__.node)
        lesson_data = {
            "title": f"{lesson.name} {lesson_type}",
            "start": lesson.start_time,
            "end": lesson.end_time,
            "color": lesson_types[lesson_type],
            "url": url_for("lessons_get") + str(lesson.__primaryvalue__)
        }
        data.append(lesson_data)

    return json.dumps(data)


@app.route('/lessons/<id>', methods=['GET'])
def lesson_details_get(id):
    if "usr" not in session:
        return redirect(url_for("login_get"))
    lesson = Lesson.match(graph, int(id)).first()
    user = User.match(graph, session["usr"]).first()
    info = get_lesson_initial_info(session["usr"])
    info["name"] = lesson.name
    info["start_time"] = lesson.start_time
    info["end_time"] = lesson.end_time
    info["group"] = lesson.group
    info["section"] = lesson.section
    info["selected_frequency"] = lesson.frequency
    info["selected_lesson_type"] = find_lesson_type(json.loads(user.lesson_types), lesson.__ogm__.node)

    for teacher in lesson.teacher:
        info["selected_teacher"] = teacher.name

    return render_template("lessons/lesson_details.html", info=info)


@app.route('/lessons/<id>', methods=['POST'])
def lesson_details_post(id):
    if "usr" not in session:
        return redirect(url_for("login_get"))
    name = request.form["name"]
    lesson_type = request.form["lesson_type"]
    start_time = request.form["start_time"]
    end_time = request.form["end_time"]
    frequency = request.form["frequency"]
    teacher = request.form["teacher"]
    group = request.form["group"]
    section = request.form["section"]

    lesson = update_lesson(name, start_time, end_time, frequency, teacher, group, section,
                           lesson_type, session["usr"], id)
    return redirect(url_for("calendar_get"))


@app.route('/lessons/all', methods=["GET"])
def lessons_all_get():
    if "usr" not in session:
        return redirect(url_for("login_get"))
    lessons_list = get_lessons_list(session["usr"])
    return render_template("lessons/lesson_list.html", info=lessons_list)


@app.route('/lessons/add/<id>', methods=["GET"])
def lessons_add_to_user(id):
    if "usr" not in session:
        return redirect(url_for("login_get"))
    add_lesson_to_user(id, session["usr"])
    return redirect(url_for("lessons_get"))


@app.route('/accounts/logout')
def logout():
    session.pop("usr", None)
    flash("You have successfully been logged out.", "info")
    return redirect(url_for("login_get"))


if __name__ == '__main__':
    app.run(debug=True)
