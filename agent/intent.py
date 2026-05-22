import anthropic

_client = anthropic.Anthropic()

_CLASSIFIER_PROMPT = """Classify the customer's message into exactly one of these intents:

- order_status: asking about an order, tracking, delivery, where is my package
- return: wanting to return, refund, or exchange an item
- policy: questions about shipping times, payment methods, password reset, general policies
- escalation: wants to speak to a human agent
- other: anything outside Bookly support scope
- unclear: the message is too vague or ambiguous to confidently classify

Reply with only the intent label. Nothing else."""

VALID_INTENTS = {"order_status", "return", "policy", "escalation", "other", "unclear"}


def classify_intent(message: str) -> str:
    response = _client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=10,
        system=_CLASSIFIER_PROMPT,
        messages=[{"role": "user", "content": message}],
    )
    intent = response.content[0].text.strip().lower()
    return intent if intent in VALID_INTENTS else "other"
