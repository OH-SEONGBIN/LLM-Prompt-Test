from .sets.baseline import BaselineSet
from .sets.structured_json import StructuredJSONSet

REGISTRY = {
    "baseline": BaselineSet(),
    "structured": StructuredJSONSet(),
}

def get_prompt_set(name: str):
    try:
        return REGISTRY[name]
    except KeyError:
        raise ValueError(f"unknown prompt set: {name}. available: {list(REGISTRY)}")