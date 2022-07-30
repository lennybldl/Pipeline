import sys

from python_core.types import items

sys.path.insert(0, items.File(__file__).get_upstream(2) + "/src")

from pipeline import commands  # noqa E402

path = items.Folder(
    r"C:\Users\Lenny\Documents\CODE_MesProjets\0020_Pipeline\tests\testProject"
)
if path.exists():
    path.remove()

commands.initialize(path)


# ~ abstract steps
assets = commands.add_abstract_step(concept=2, parent=0, name="ASSETS")
characters = commands.add_abstract_step(concept=2, parent=assets, name="characters")
chara = commands.add_abstract_step(concept=2, parent=characters, name="ch_{basename}")
props = commands.add_abstract_step(concept=2, parent=assets, name="props")
prop = commands.add_abstract_step(concept=2, parent=props, name="pr_{basename}")

# ~ add concepts
concept = commands.add_abstract_concept(
    name="Tasks",
    rules={
        "_same_as_": ["c3"],
        "publish_unreal": {"windows": {"commands": ["publish_unreal.py"]}},
    },
)
rig_task = commands.add_abstract_step(
    concept=concept, parent=chara, name="rig", task="rig"
)
rig_workfile = commands.add_abstract_step(
    concept=4, parent=rig_task, name="{asset}_{index}_{comment}_{task}"
)


# ~ concrete steps
assets = commands.add_concrete_step(assets, parent=0)
parent = commands.add_concrete_step(characters, parent=assets)
first_chara = commands.add_concrete_step(
    chara, parent=parent, basename="mon_premier_chara"
)
first_chara_rig_task = commands.add_concrete_step(rig_task, parent=first_chara)
first_chara_rig_task = commands.add_concrete_step(
    rig_workfile, parent=first_chara_rig_task, index=5, comment="firstFile"
)

parent = commands.add_concrete_step(props, parent=assets)
first_prop = commands.add_concrete_step(
    prop, parent=parent, basename="mon_premier_prop"
)

# ~ calls
commands.call("create", first_chara)
commands.call("create", first_prop)

print(commands.get_rules(rig_task).dumps())
print(commands.get_rules(prop).dumps())
