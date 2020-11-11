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

    lessons_own = RelatedFrom("Lesson", "IS_OWNED_BY")


class StudiesType(GraphObject):
    __primarylabel__ = "studies_type"
    name = Property()
    abbreviation = Property()
    type = Property()


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


class Lesson(GraphObject):
    __primarylabel__ = "lesson"
    name = Property()
    frequency = Property()
    section = Property()
    group = Property()
    studies_type = Property()
    end_time = Property()
    start_time = Property()

    lesson_type = RelatedTo("LessonType", "IS_TYPE")
    teacher = RelatedTo("User", "IS_TAUGHT_BY")
    studies_type = RelatedTo("StudiesType", "IS_CONDUCTED_FOR")
