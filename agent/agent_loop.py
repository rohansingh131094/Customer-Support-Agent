import logging
import anthropic
from anthropic import APIConnectionError, APIStatusError, RateLimitError
from agent.tools import execute_tool

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

client = anthropic.Anthropic()
MODEL = "claude-sonnet-4-6"

_ERROR_MESSAGES = {
    RateLimitError: "I'm getting a lot of requests right now — please try again in a moment.",
    APIConnectionError: "I'm having trouble connecting. Please check your connection and try again.",
}


def _serialize_content(content) -> list[dict]:
    result = []
    for block in content:
        if block.type == "text":
            result.append({"type": "text", "text": block.text})
        elif block.type == "tool_use":
            result.append({
                "type": "tool_use",
                "id": block.id,
                "name": block.name,
                "input": block.input,
            })
    return result


def stream_agent(user_message: str, history: list[dict], system_prompt: str, tools: list):
    """
    Yields ("text", chunk) for each streamed text chunk.
    Yields ("done", updated_messages) once complete.

    Text produced before a tool call is buffered and discarded — it's filler.
    Only text from turns that end cleanly (end_turn) is streamed to the client.
    """
    messages = history + [{"role": "user", "content": user_message}]
    tool_called = False
    iterations = 0
    max_iterations = 10

    log.debug("▶ stream_agent start | user: %r | history turns: %d", user_message[:80], len(history))

    try:
        while iterations < max_iterations:
            iterations += 1
            text_buffer = []
            log.debug("→ calling Claude (messages in context: %d, iteration: %d)", len(messages), iterations)

            with client.messages.stream(
                model=MODEL,
                max_tokens=1024,
                system=system_prompt,
                tools=tools or [],
                messages=messages,
            ) as stream:
                for text_chunk in stream.text_stream:
                    if tool_called:
                        yield ("text", text_chunk)
                    else:
                        text_buffer.append(text_chunk)

                final = stream.get_final_message()

            log.debug("← stop_reason: %s | output tokens: %d", final.stop_reason, final.usage.output_tokens)
            messages.append({"role": "assistant", "content": _serialize_content(final.content)})

            if final.stop_reason == "end_turn":
                log.debug("✓ end_turn — flushing %d buffered text chunks", len(text_buffer))
                for chunk in text_buffer:
                    yield ("text", chunk)
                yield ("done", messages)
                return

            if final.stop_reason == "tool_use":
                tool_called = True
                tool_results = []
                for block in final.content:
                    if block.type == "tool_use":
                        log.debug("🔧 tool_call: %s | inputs: %s", block.name, block.input)
                        yield ("tool_call", {"name": block.name, "inputs": block.input})
                        result = execute_tool(block.name, block.input)
                        log.debug("   tool_result: %s", str(result)[:200])
                        yield ("tool_result", {"name": block.name, "result": result})
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": result,
                        })
                messages.append({"role": "user", "content": tool_results})

        log.warning("max iterations (%d) reached", max_iterations)
        yield ("text", "I'm having trouble completing this request. Please try again or contact support.")
        yield ("done", messages)
        return

    except RateLimitError:
        log.warning("rate limit hit")
        yield ("text", _ERROR_MESSAGES[RateLimitError])
        yield ("done", messages)
    except APIConnectionError:
        log.warning("API connection error")
        yield ("text", _ERROR_MESSAGES[APIConnectionError])
        yield ("done", messages)
    except APIStatusError as e:
        log.error("APIStatusError: %s", e.status_code)
        yield ("text", f"Something went wrong on our end (error {e.status_code}). Please try again.")
        yield ("done", messages)
