import os
import json
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel

from agent.intent import classify_intent
from agent.system_prompt import build_intent
from agent.tools import get_tools
from agent.loop import stream_agent
from agent.sessions import get_history, get_intent, set_intent, update_history

app = FastAPI(title="Bookly Support Agent")
app.mount("/static", StaticFiles(directory="static"), name="static")


class ChatRequest(BaseModel):
    message: str
    session_id: str


@app.get("/")
def root():
    return FileResponse("static/index.html")


@app.post("/chat")
def chat(req: ChatRequest):
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    # Reclassify on every message, but only update if Haiku returns a confident intent
    current_intent = get_intent(req.session_id)
    new_intent = classify_intent(req.message)

    if new_intent not in ("unclear", "other"):
        intent = new_intent
    else:
        # Ambiguous follow-up — keep current intent if one exists, otherwise use new
        intent = current_intent if current_intent else new_intent

    set_intent(req.session_id, intent)

    system_prompt, tool_names = build_intent(intent)
    tools = get_tools(tool_names)
    history = get_history(req.session_id)

    def generate():
        yield f"data: {json.dumps({'intent': intent})}\n\n"
        for event_type, payload in stream_agent(req.message, history, system_prompt, tools):
            if event_type == "text":
                yield f"data: {json.dumps({'chunk': payload})}\n\n"
            elif event_type == "tool_call":
                yield f"data: {json.dumps({'tool_call': payload})}\n\n"
            elif event_type == "tool_result":
                yield f"data: {json.dumps({'tool_result': payload})}\n\n"
            elif event_type == "done":
                update_history(req.session_id, payload)
                yield f"data: {json.dumps({'done': True})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
