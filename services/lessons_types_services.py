from data.db_session import db_auth

graph = db_auth()

def get_lesson_type_names() -> list:
    lessons = graph.run(
        f"MATCH (x:lesson_type) RETURN x.name as name"
    ).data()

    names = [x["name"] for x in lessons]
    return names