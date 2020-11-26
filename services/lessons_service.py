import json
from typing import Optional

from flask import url_for
from py2neo import Relationship, NodeMatcher, Node
from py2neo.ogm import Label

from data.db_session import db_auth
from .accounts_service import get_teachers_names, create_teacher_relationship, create_owner_relationship
from .classes import FrequencyEnum, Lesson, User, BlockEnum

graph = db_auth()


def create_lesson(name: str, lesson_type: str, start_time: str, end_time: str, frequency: str, block: str, teacher: str,
                  studies_type: str, group: str, section: str, owner: str) -> Optional[Lesson]:
    lesson = Lesson()
    lesson.name = name
    lesson.start_time = start_time
    lesson.end_time = end_time
    lesson.frequency = frequency
    lesson.group = group
    lesson.section = section
    graph.create(lesson)

    matcher = NodeMatcher(graph)
    created_lesson = matcher.match("lesson", name=name).first()
    created_lesson.add_label(studies_type)
    created_lesson.add_label(lesson_type)
    created_lesson.add_label(block)
    graph.push(created_lesson)
    create_teacher_relationship(lesson.__ogm__.node, teacher)
    create_owner_relationship(lesson, owner)
    return lesson


def update_lesson(name: str, start_time: str, end_time: str, frequency: str, teacher: str,
                  group: str, section: str, lesson_type: str, usr: str, id: str) -> Optional[Lesson]:
    lesson = Lesson.match(graph, int(id)).first()
    lesson.name = name
    lesson.start_time = start_time
    lesson.end_time = end_time
    lesson.frequency = frequency
    lesson.group = group
    lesson.section = section
    lesson.teacher.clear()

    lesson = change_lesson_type(lesson_type, lesson, usr)

    graph.push(lesson)

    create_teacher_relationship(lesson, teacher)

    return lesson


def get_lesson_initial_info(usr: str) -> dict:
    matcher = NodeMatcher(graph)
    user = matcher.match("user", email=usr).first()

    info = {
        "lesson_types": json.loads(user["lesson_types"]).keys(),
        "teachers": get_teachers_names(),
        "frequency": FrequencyEnum._member_names_,
        "blocks": BlockEnum._member_names_
    }
    return info


def find_lesson_type(lesson_types: dict, lesson: Node) -> str:
    lesson_type = None
    for label in lesson_types.keys():
        if lesson.has_label(label):
            lesson_type = label
            break
    return lesson_type


def change_lesson_type(lesson_type: str, lesson: Lesson, usr: str) -> Lesson:
    user = User.match(graph, f"{usr}").first()
    lesson = lesson.__ogm__.node
    lesson.remove_label(find_lesson_type(json.loads(user.lesson_types), lesson))
    lesson.add_label(lesson_type)
    return lesson


def get_lessons_list(usr: str) -> list:
    other_users_lessons = graph.run(
        f"MATCH(x:lesson), (y:user) WHERE y.email='{usr}'AND NOT (x)-[:IS_OWNED_BY]-(y) RETURN x as lessons, ID(x) as id").data()
    user = User.match(graph, usr).first()
    lesson_list = []
    for item in other_users_lessons:
        lesson = item["lessons"]
        lesson_list.append(
            {
                "name": lesson["name"],
                "type": find_lesson_type(json.loads(user.lesson_types), lesson),
                "start_time": lesson["start_time"],
                "end_time": lesson["end_time"],
                "frequency": lesson["frequency"],
                "teacher": lesson["teacher"],
                "group": lesson["group"],
                "section": lesson["section"],
                "add": url_for("lessons_add_to_user", id=item["id"])
            }
        )
    return lesson_list


def add_lesson_to_user(id: str, usr: str):
    lesson = Lesson.match(graph, int(id)).first()
    create_owner_relationship(lesson, usr)
