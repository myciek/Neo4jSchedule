import json
from typing import Optional

from passlib.handlers.sha2_crypt import sha512_crypt as crypto
from py2neo import NodeMatcher, Relationship

from data.db_session import db_auth
from services.classes import User

graph = db_auth()


def create_user(name: str, email: str, is_teacher: bool, password: str) -> Optional[User]:
    if User.match(graph, f"{email}"):
        return None
    user = User()
    user.name = name
    user.email = email
    user.active = False
    if is_teacher:
        user.teacher_for_approval = True
    else:
        user.student = True
    user.hashed_password = hash_text(password)
    user.lesson_types = json.dumps({
        "Wykład": "#42A142",
        "Ćwiczenia": "#094BB9",
        "Laboratorium": "#E61515",
        "Projekt": "#ECDC14",
        "Konsultacje": "#EC8E14",
        "Seminarium dyplomowe": "#16DB78",
        "Egzamin": "#6B0B81",
        "Kolokwium": "#EB1FD8",
        "Kartkówka": "#0F1A5E",
        "Sprawozdanie": "#D6D9EB"
    })
    graph.create(user)
    return user


def update_user(name: str, email: str, original_email: str) -> Optional[User]:
    matcher = NodeMatcher(graph)
    updated_user = matcher.match("user", email=original_email).first()
    updated_user["email"] = email
    updated_user["name"] = name
    graph.push(updated_user)
    return updated_user


def hash_text(text: str) -> str:
    hashed_text = crypto.encrypt(text, rounds=171204)
    return hashed_text


def verify_hash(hashed_text: str, plain_text: str) -> bool:
    return crypto.verify(plain_text, hashed_text)


def login_user(email: str, password: str) -> Optional[User]:
    user = User.match(graph, f"{email}").first()
    if not user:
        print(f"Invalid User - {email}")
        return None
    if not verify_hash(user.hashed_password, password):
        print(f"Invalid Password for {email}")
        return None
    if not user.active:
        print(f"{email} is not active")
        return None
    print(f"User {email} passed authentication")
    return user


def get_profile(usr: str) -> Optional[User]:
    user_profile = graph.run(
        f"MATCH (x:user) WHERE x.email='{usr}' RETURN x.name as name, x.email as email")
    return user_profile


def is_admin(usr: str):
    admin_profile = graph.run(
        f"MATCH (x:admin) RETURN x.email as email").data()
    return usr == admin_profile[0]["email"]


def get_teachers_names() -> list:
    teachers = graph.run(
        f"MATCH (x:teacher) RETURN x.name as name"
    ).data()

    names = [x["name"] for x in teachers]
    return names


def get_teachers_for_approval_names() -> list:
    teachers = graph.run(
        f"MATCH (x:teacher_for_approval) RETURN x.name as name"
    ).data()

    names = [x["name"] for x in teachers]
    return names


def approve_teachers(teachers: list):
    for teacher in teachers:
        matcher = NodeMatcher(graph)
        user = matcher.match("user", name=teacher).first()
        user.remove_label("teacher_for_approval")
        user.add_label("teacher")
        graph.push(user)


def create_teacher_relationship(lesson_node, teacher):
    teacher_node = graph.run(f"MATCH (x:user) WHERE x.name='{teacher}' RETURN x").data()
    relationship = Relationship(lesson_node, "IS_TAUGHT_BY", teacher_node[0]["x"])
    graph.create(relationship)


def create_owner_relationship(lesson_node, owner):
    owner_node = graph.run(f"MATCH (x:user) WHERE x.email='{owner}' RETURN x").data()
    relationship = Relationship(lesson_node.__ogm__.node, "IS_OWNED_BY", owner_node[0]["x"])
    graph.create(relationship)
