"""Initilize variables to access elements classes."""

from pipeline.api import elements, abstract_steps, concrete_steps

CONCEPT = elements.Concept

ABSTRACT_STEPS = {
    "asset": abstract_steps.AbstractAsset,
    "task": abstract_steps.AbstractTask,
    "workfile": abstract_steps.AbstractWorkfile,
}

CONCRETE_STEPS = {
    "asset": concrete_steps.ConcreteAsset,
    "task": concrete_steps.ConcreteTask,
    "workfile": concrete_steps.ConcreteWorkfile,
}
