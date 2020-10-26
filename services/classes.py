from py2neo.ogm import GraphObject, Property, RelatedTo, RelatedFrom
from enum import Enum


class User(GraphObject):
    __primarylabel__ = "user"
    __primarykey__ = "email"
    name = Property()
    email = Property()
    is_teacher = Property()
    password = Property()
    hashed_password = Property()

    lessons_taught = RelatedFrom("Lesson", "IS_TAUGHT_BY")
    lessons_own = RelatedFrom("Lesson", "IS_OWNED_BY")


class StudiesType(GraphObject):
    __primarylabel__ = "studies_type"
    __primarykey__ = "abbreviation"
    name = Property()
    abbreviation = Property()
    type = Property()

    lessons = RelatedFrom("Lesson", "IS_CONDUCTED_FOR")


class TypeEnum(Enum):
    SSI = 1
    NSI = 2
    SSM = 3
    NSM = 4


class FrequencyEnum(Enum):
    Jednorazowe = 1
    Tygodniowo = 2
    Parzyste = 3
    Nieparzyste = 4


class LessonType(GraphObject):
    __primarylabel__ = "lesson_type"
    __primarykey__ = "name"
    name = Property()
    color = Property()

    lessons = RelatedFrom("Lesson", "IS_TYPE")


class Lesson(GraphObject):
    __primarylabel__ = "lesson"
    name = Property()
    frequency = Property()
    section = Property()
    group = Property()
    studies_type = Property()
    duration = Property()
    start_time = Property()

    lesson_type = RelatedTo("LessonType")
    teacher = RelatedTo("User")
    owner = RelatedTo("User")
    studies_type = RelatedTo("StudiesType")

