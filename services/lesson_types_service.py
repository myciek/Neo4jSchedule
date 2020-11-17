import json

from py2neo import NodeMatcher

from data.db_session import db_auth
from services.classes import User

graph = db_auth()


def create_lesson_type(name: str, color: str, usr: str) -> str:
    matcher = NodeMatcher(graph)
    user = matcher.match("user", email=usr).first()
    if name in user["lesson_types"] or color in user["lesson_types"]:
        return None
    lesson_types = json.loads(user["lesson_types"])
    lesson_types[name] = color
    user["lesson_types"] = json.dumps(lesson_types)
    graph.push(user)
    return name
