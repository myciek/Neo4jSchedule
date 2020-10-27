from typing import Optional

from data.db_session import db_auth
from services.classes import LessonType

graph = db_auth()


def find_lesson_type(name: str, color: str):
    lesson_type = graph.run(
        f"MATCH (x:lesson_type) WHERE x.name='{name}' OR x.color='{color}' RETURN x").data()
    return lesson_type


def create_lesson_type(name: str, color: str) -> Optional[LessonType]:
    if find_lesson_type(name, color):
        return None
    lesson_type = LessonType()
    lesson_type.name = name
    lesson_type.color = color
    graph.create(lesson_type)
    return lesson_type


def get_lesson_type_names() -> list:
    lessons = graph.run(
        f"MATCH (x:lesson_type) RETURN x.name as name"
    ).data()

    names = [x["name"] for x in lessons]
    return names
