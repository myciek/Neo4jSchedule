from typing import Optional

from py2neo import Relationship

from data.db_session import db_auth
from .accounts_service import get_teachers_names, find_user
from .classes import FrequencyEnum, Lesson, LessonType, User, StudiesType

from .lesson_types_services import get_lesson_type_names
from .studies_types_services import get_studies_type_names

graph = db_auth()


def create_relationship(lesson: Lesson, relation: str, partner: str, ):
    relationship = Relationship(lesson.__ogm__.node, relation, partner[0]["x"])
    graph.create(relationship)


def create_lesson(name: str, lesson_type: str, start_time: str, duration: str, frequency: str, teacher: str,
                  studies_type: str, group: str, section: str, owner: str) -> Optional[Lesson]:
    lesson = Lesson()
    lesson.name = name
    lesson.start_time = start_time
    lesson.duration = duration
    lesson.frequency = frequency
    lesson.group = group
    lesson.section = section
    graph.create(lesson)

    lesson_type_node = graph.run(f"MATCH (x:lesson_type) WHERE x.name='{lesson_type}' RETURN x").data()
    create_relationship(lesson, "IS_TYPE", lesson_type_node)
    studies_type = studies_type.split()
    studies_type_node = graph.run(
        f"MATCH (x:studies_type) WHERE x.abbreviation='{studies_type[0]}' AND x.type='{studies_type[1]}' RETURN x").data()
    create_relationship(lesson, "IS_CONDUCTED_FOR", studies_type_node)
    teacher_node = graph.run(f"MATCH (x:user) WHERE x.name='{teacher}' RETURN x").data()
    create_relationship(lesson, "IS_TAUGHT_BY", teacher_node)
    owner_node = graph.run(f"MATCH (x:user) WHERE x.email='{owner}' RETURN x").data()
    create_relationship(lesson, "IS_OWNED_BY", owner_node)
    return lesson


def get_lesson_initial_info() -> dict:
    info = {
        "lesson_types": get_lesson_type_names(),
        "teachers": get_teachers_names(),
        "frequency": FrequencyEnum._member_names_,
        "studies_types": get_studies_type_names()
    }
    return info
