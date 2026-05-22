import json
import os

_policies = None


def _load() -> dict:
    global _policies
    if _policies is None:
        path = os.path.join(os.path.dirname(__file__), "policies.json")
        with open(path) as f:
            _policies = json.load(f)
    return _policies


def get_policy_text(topic: str) -> str:
    policies = _load()
    text = policies.get(topic)
    if not text:
        return f"No policy information found for topic '{topic}'."
    return text
