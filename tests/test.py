import sys

from python_core.types import items

sys.path.insert(0, items.AbstractItem(__file__).get_upstream(2))

from pipeline import commands  # noqa E402

path = r"C:\Users\Lenny\Documents\CODE_MesProjets\0020_Pipeline\tests\testProject"
commands.initialize(path)

# ~ abstract steps
assets = commands.add_abstract_step("asset", parent=0, name="ASSETS")
characters = commands.add_abstract_step("asset", parent=assets, name="characters")
chara = commands.add_abstract_step("asset", parent=characters, name="ch_{basename}")
props = commands.add_abstract_step("asset", parent=assets, name="props")
prop = commands.add_abstract_step("asset", parent=props, name="pr_{basename}")

# ~ concrete steps
assets = commands.add_concrete_step(assets, parent=0)
parent = commands.add_concrete_step(characters, parent=assets)
first_chara = commands.add_concrete_step(
    chara, parent=parent, basename="mon_premier_chara"
)
parent = commands.add_concrete_step(props, parent=assets)
first_prop = commands.add_concrete_step(
    prop, parent=parent, basename="mon_premier_prop"
)

commands.call("create", first_chara)
commands.call("create", first_prop)
