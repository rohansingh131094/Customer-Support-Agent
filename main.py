import os
import json
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel

from agent.classify_intent import resolve_journey
from agent.journeys import build_journey, BOOKLY_AGENT
from agent.agent_loop import stream_agent
from agent.sessions import get_history, get_intent, set_intent, get_pending_journey, clear_pending_journey, update_history

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

    journey_name = resolve_journey(req.message, get_intent(req.session_id))
    set_intent(req.session_id, journey_name)
    pending_journey = get_pending_journey(req.session_id)

    system_prompt, tools = build_journey(journey_name, pending_journey)
    history = get_history(req.session_id)

    matched = next((j for j in BOOKLY_AGENT.journeys if j.name == journey_name), None)
    observation = matched.observation if matched else None

    def generate():
        yield f"data: {json.dumps({'journey': journey_name, 'observation': observation})}\n\n"
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
