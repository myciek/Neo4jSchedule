from data.db_session import db_auth
from .classes import FrequencyEnum

graph = db_auth()


def get_lesson_type_names() -> list:
    lessons = graph.run(
        f"MATCH (x:lesson_type) RETURN x.name as name"
    ).data()

    names = [x["name"] for x in lessons]
    return names


def get_teachers_names() -> list:
    teachers = graph.run(
        f"MATCH (x:user) WHERE x.is_teacher=true RETURN x.name as name"
    ).data()

    names = [x["name"] for x in teachers]
    return names


def get_studies_type_names() -> list:
    studies = graph.run(
        f"MATCH (x:studies_type) RETURN x.name as name"
    ).data()

    names = [f'{x["abbreviation"]}  {x["type"]}' for x in studies]
    return names


def get_lesson_initial_info() -> dict:
    info = {
        "lesson_types": get_lesson_type_names(),
        "teachers": get_teachers_names(),
        "frequency": FrequencyEnum._member_names_,
        "studies_types": get_studies_type_names()
    }
    return info
