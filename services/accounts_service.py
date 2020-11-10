from typing import Optional

from passlib.handlers.sha2_crypt import sha512_crypt as crypto
from py2neo import NodeMatcher, Relationship

from data.db_session import db_auth
from services.classes import User

graph = db_auth()


def find_user(email: str):
    user = User.match(graph, f"{email}")
    return user


def create_user(name: str, email: str, is_teacher: bool, password: str) -> Optional[User]:
    if find_user(email):
        return None
    user = User()
    user.name = name
    user.email = email
    if is_teacher:
        user.teacher_for_approval = True
    else:
        user.student = True
    user.hashed_password = hash_text(password)
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
    print(f"User {email} passed authentication")
    return user


def get_profile(usr: str) -> Optional[User]:
    user_profile = graph.run(
        f"MATCH (x:user) WHERE x.email='{usr}' RETURN x.name as name, x.email as email")
    return user_profile


def get_teachers_names() -> list:
    teachers = graph.run(
        f"MATCH (x:user:Teacher) RETURN x.name as name"
    ).data()

    names = [x["name"] for x in teachers]
    return names


def create_teacher_relationship(lesson_node, teacher):
    teacher_node = graph.run(f"MATCH (x:user) WHERE x.name='{teacher}' RETURN x").data()
    relationship = Relationship(lesson_node.__ogm__.node, "IS_TAUGHT_BY", teacher_node[0]["x"])
    graph.create(relationship)


def create_owner_relationship(lesson_node, owner):
    owner_node = graph.run(f"MATCH (x:user) WHERE x.email='{owner}' RETURN x").data()
    relationship = Relationship(lesson_node.__ogm__.node, "IS_OWNED_BY", owner_node[0]["x"])
    graph.create(relationship)
