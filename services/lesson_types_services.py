from typing import Optional

from py2neo import Relationship

from data.db_session import db_auth

graph = db_auth()


def create_lesson_type_relationship(lesson_node, lesson_type):
    lesson_type_node = graph.run(f"MATCH (x:lesson_type) WHERE x.name='{lesson_type}' RETURN x").data()
    relationship = Relationship(lesson_node.__ogm__.node, "IS_TYPE", lesson_type_node[0]["x"])
    graph.create(relationship)


def find_lesson_type(name: str, color: str):
    lesson_type = graph.run(
        f"MATCH (x:lesson_type) WHERE x.name='{name}' OR x.color='{color}' RETURN x").data()
    return lesson_type


def get_lesson_type_names() -> list:
    lessons = graph.run(
        f"MATCH (x:lesson_type) RETURN x.name as name"
    ).data()

    names = [x["name"] for x in lessons]
    return names
