from py2neo.ogm import GraphObject, Property


class User(GraphObject):
    __primarylabel__ = "user"
    __primarykey__ = "email"
    name = Property()
    email = Property()
    is_teacher = Property()
    password = Property()
    hashed_password = Property()
