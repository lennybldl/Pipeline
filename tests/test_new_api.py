import sys

sys.path.insert(0, r"C:\Users\Lenny\Documents\CODE_MesProjets\dev\0000_python_core\src")

from python_core.types import items

# remove the pipeline project to make it relaunchable
path = items.Folder(
    r"C:\Users\Lenny\Documents\CODE_MesProjets\dev\0020_Pipeline\tests\Nouveau dossier"
)


from pipeline import commands
from pipeline.internal import core


def create():
    if path.exists():
        path.remove()

    commands.start("windows")
    commands.create_project(path)
    commands.load_project(path)

    concept1 = commands.add_concept()
    print(concept1.properties)
    concept2 = commands.add_concept(concept1)
    print(concept2.properties)
    print(concept1.get_property("name"))
    print(concept2.get_property("name"))
    concept1.set_property("name", "test")
    print(concept1.get_property("name"))
    print(concept2.get_property("name"))
    print(concept2.properties)
    concept2.set_property("name", "Concept2")
    print(concept2.properties)
    concept2.set_property("name", "test")
    print(concept2.properties)
    concept2.set_property("super_member", None)
    print(concept2.properties)
    concept2.set_property("super_member", concept1)
    concept1.set_property("index.visibility", core.PRIVATE)
    concept1.set_property("index.min", -5)
    print(concept2.properties)
    commands.save()
    return
    concept1.create_property("str", "custom", "custom property")
    print(concept1.properties)
    print(concept2.properties)
    print(concept2.get_property("custom"))
    concept2.get_property("commands").add_command("create", "linux")
    print(concept2.get_property("commands"))

    abstract = commands.add_abstract_step(concept2)
    abstract.set_property(
        "name",
        "ch_{index}_{padding}_{super_member.name}_{super_member.super_member.name}_rig",
    )
    print(abstract.get_formated_name())
    abstract.get_property("commands").add_command("create", "windows")
    print(abstract.get_property("commands"))
    create_command = abstract.get_property("commands.windows.create")
    create_command.extend(["create.py", "isolate.py"])

    concrete = commands.add_concrete_step(abstract)
    compound = concrete.create_property("compound", "compound")
    print(compound)
    compound.create_property("str", "name", "nom a la con")
    compound.create_property("int", "index", 0)
    print(compound)
    print(concrete.get_property("compound.name"))
    # compound2 = compound.create_property("compound", "compound")
    # compound2.create_property("str", "name", "test2")
    # print(compound)

    commands.save()


def load():
    commands.start("windows")
    commands.load_project(path)

    concept1 = commands.get_concept(1)
    print(concept1.properties)
    concept2 = commands.get_concept(2)
    print(concept2.properties)
    return
    print(concept2.custom)
    print(commands.get_property(concept2, "custom"))
    commands.set_property(concept2, "custom", "voila")
    print(commands.get_property(concept2, "custom"))

    abstract = commands.get_abstract_step(1)
    commands.call(abstract.full_project_path, "create")

    concrete = commands.get_concrete_step(1)
    print(concrete.custom)
    print(concrete.compound)
    print(concrete.compound.name)
    concrete.compound.name = "truc"
    print(concrete.compound.name)
    print(concrete.compound)
    print(concrete.compound.index)
    print(concrete.compound.compound.name)
    print(concrete.compound.get_property("index"))
    concrete.compound.delete_property("index")
    print(concrete.compound)


create()
# load()
