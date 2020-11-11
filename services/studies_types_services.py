from typing import Optional

from py2neo import Relationship

from data.db_session import db_auth

graph = db_auth()


def create_studies_type_relationship(lesson_node, studies_type):
    studies_type = studies_type.split()
    studies_type_node = graph.run(
        f"MATCH (x:studies_type) WHERE x.abbreviation='{studies_type[0]}' AND x.type='{studies_type[1]}' RETURN x").data()
    relationship = Relationship(lesson_node.__ogm__.node, "IS_CONDUCTED_FOR", studies_type_node[0]["x"])
    graph.create(relationship)


def find_studies_type(abbreviation: str, type: str):
    studies_type = graph.run(
        f"MATCH (x:studies_type) WHERE x.abbreviation='{abbreviation}' AND x.type='{type}' RETURN x").data()
    return studies_type


def get_studies_type_names() -> list:
    studies = graph.run(
        f"MATCH (x:studies_type) RETURN x.abbreviation as abbreviation, x.type as type"
    ).data()

    names = [f'{x["abbreviation"]} {x["type"]}' for x in studies]
    return names
