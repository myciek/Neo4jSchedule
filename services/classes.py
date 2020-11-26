from py2neo.ogm import GraphObject, Property, RelatedTo, RelatedFrom, Label
from enum import Enum


class User(GraphObject):
    __primarylabel__ = "user"
    __primarykey__ = "email"
    student = Label(name="student")
    teacher = Label(name="teacher")
    teacher_for_approval = Label(name="teacher_for_approval")
    admin = Label(name="admin")
    name = Property()
    email = Property()
    password = Property()
    hashed_password = Property()
    lesson_types = Property()
    active = Property()

    lessons_own = RelatedFrom("Lesson", "IS_OWNED_BY")


class FrequencyEnum(Enum):
    Jednorazowe = 1
    Tygodniowo = 2
    Parzyste = 3
    Nieparzyste = 4


class Lesson(GraphObject):
    __primarylabel__ = "lesson"
    name = Property()
    frequency = Property()
    section = Property()
    group = Property()
    studies_type = Property()
    end_time = Property()
    start_time = Property()

    teacher = RelatedTo("User", "IS_TAUGHT_BY")
    studies_type = RelatedTo("StudiesType", "IS_CONDUCTED_FOR")
