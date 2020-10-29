from typing import Optional

from py2neo import Relationship

from data.db_session import db_auth
from .accounts_service import get_teachers_names, create_teacher_relationship, create_owner_relationship
from .classes import FrequencyEnum, Lesson
from .lesson_types_services import get_lesson_type_names, create_lesson_type_relationship
from .studies_types_services import get_studies_type_names, create_studies_type_relationship

graph = db_auth()


def create_lesson(name: str, lesson_type: str, start_time: str, end_time: str, frequency: str, teacher: str,
                  studies_type: str, group: str, section: str, owner: str) -> Optional[Lesson]:
    lesson = Lesson()
    lesson.name = name
    lesson.start_time = start_time
    lesson.end_time = end_time
    lesson.frequency = frequency
    lesson.group = group
    lesson.section = section
    graph.create(lesson)

    create_lesson_type_relationship(lesson, lesson_type)
    create_studies_type_relationship(lesson, studies_type)
    create_teacher_relationship(lesson, teacher)
    create_owner_relationship(lesson, owner)
    return lesson


def update_lesson(name: str, lesson_type: str, start_time: str, end_time: str, frequency: str, teacher: str,
                  studies_type: str, group: str, section: str, id: str) -> Optional[Lesson]:
    lesson = Lesson.match(graph, int(id)).first()
    lesson.name = name
    lesson.start_time = start_time
    lesson.end_time = end_time
    lesson.frequency = frequency
    lesson.group = group
    lesson.section = section

    lesson.lesson_type.clear()
    lesson.studies_type.clear()
    lesson.teacher.clear()

    graph.push(lesson)

    create_lesson_type_relationship(lesson, lesson_type)
    create_studies_type_relationship(lesson, studies_type)
    create_teacher_relationship(lesson, teacher)

    return lesson


def get_lesson_initial_info() -> dict:
    info = {
        "lesson_types": get_lesson_type_names(),
        "teachers": get_teachers_names(),
        "frequency": FrequencyEnum._member_names_,
        "studies_types": get_studies_type_names()
    }
    return info
