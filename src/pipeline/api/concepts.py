"""Manage the concepts."""

from pipeline.api import members


class Concept(members.DesignMember):
    """Manage every concept of the pipeline."""

    project_path = "concept.id"
