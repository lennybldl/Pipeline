import json


class Property(object):
    def __init__(self, name, value, visibility="public"):
        self.name = name
        self.value = value
        self.visibility = visibility  # public protected private
        super(Property, self).__init__()

    def serialize(self):
        return self.value


class Member(object):

    parent = None

    def __init__(self, parent=None):
        super(Member, self).__init__()

        if not parent:
            self.name = Property("name", "toto")
            self.age = Property("age", 0)
            self.last_name = Property("last_name", "Doe", "protected")
            self.properties = {
                "name": self.name,
                "age": self.age,
                "last_name": self.last_name,
            }
        else:
            self.parent = parent
            self.properties = dict()

    def __setattr__(self, name, value):
        if hasattr(self, name):
            _property = getattr(self, name)
            if isinstance(_property, Property):
                if _property in self.properties:
                    _property.value = value
                elif _property.visibility == "public":
                    self.add_property(name, value)
                return
        super(Member, self).__setattr__(name, value)

    def __getattribute__(self, name):
        try:
            return object.__getattribute__(self, name)
        except:
            return object.__getattribute__(self.parent, name)

    def add_property(self, name, value, **kwargs):
        _property = Property(name, value, **kwargs)
        super(Member, self).__setattr__(name, _property)
        self.properties[name] = _property

    def delete_property(self, name):
        if name in self.properties:
            self.properties.pop(name)
            delattr(self, name)

    def serialize(self):
        serialization = dict()
        for name, _property in self.properties.items():
            serialization[name] = _property.serialize()
        return serialization


class Project(dict):
    def __repr__(self):
        return json.dumps(self.serialize(), indent=4)

    def add_member(self, _id, *args, **kwargs):
        member = Member(*args, **kwargs)
        self[_id] = member
        return member

    def get_member(self, _id):
        return self[_id]

    def serialize(self):
        serialization = dict()
        for _id, member in self.items():
            serialization[_id] = member.serialize()
        return serialization


project = Project()
parent = project.add_member(0)
member = project.add_member(1, parent=parent)
print(member.name.value)
member = project.get_member(1)
member.name = "titine"
print(member.name.value)
member.delete_property("name")
print(member.name.value)
member.age = 5
member.last_name = "truc"
print(project)
