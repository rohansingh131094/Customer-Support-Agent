from __future__ import annotations
import anthropic
from agent.journeys import BOOKLY_AGENT, Journey

_client = anthropic.Anthropic()


def _build_classifier_prompt(journeys: list[Journey]) -> str:
    options = "\n".join(
        f"- {j.name}: {j.observation}"
        for j in journeys
    )
    return (
        "You are a customer intent classifier for Bookly, an online bookstore.\n"
        "Given a customer message, identify which journey observation is true.\n\n"
        "Journeys:\n"
        f"{options}\n\n"
        "Reply with only the exact journey name from the list above. Nothing else."
    )


def classify_journey(message: str) -> str:
    journeys = BOOKLY_AGENT.journeys
    valid_names = {j.name for j in journeys}

    response = _client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=20,
        system=_build_classifier_prompt(journeys),
        messages=[{"role": "user", "content": message}],
    )
    name = response.content[0].text.strip()
    return name if name in valid_names else "Unclear Request"
