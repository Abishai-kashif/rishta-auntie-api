import os
import json
from fastapi import FastAPI
from dotenv import load_dotenv
from models import PromptRequest
from agents import (
        Agent, Runner, OpenAIChatCompletionsModel,
        AsyncOpenAI, InputGuardrailTripwireTriggered,
        RunConfig, set_tracing_disabled
    )
from openai.types.responses import ResponseTextDeltaEvent
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from tools import get_user_data, send_whatsapp_sms, web_search

load_dotenv()
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"])


@app.get("/")
def root_route():
    return {
        "message": "Welcome to the Rishta App Agent Backend"
    }

@app.post("/auntie")
async def auntie_route(req: PromptRequest):
    try:
        set_tracing_disabled(disabled=True)

        external_client = AsyncOpenAI(
            api_key=os.getenv("GEMINI_API_KEY"),
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        )

        model = OpenAIChatCompletionsModel(
            model="gemini-2.0-flash",
            openai_client=external_client,
        )

        config = RunConfig(
            model=model,
            model_provider=external_client,
            tracing_disabled=True
        )

        agent = Agent(
            name="Rishta Auntie",
            instructions="""
                You’re a kind and helpful auntie who assists people in finding matches. You should only respond to questions related to matchmaking or simple greetings (like ‘hi’), and ignore all other types of queries.
                
                When the user asks to send match details on WhatsApp, use the list of user profiles you've retrieved ( from `get_user_data` ) and pass it directly into send_whatsapp_sms as the 'users' argument. "Do not request or craft
                the message outside this function—internal formatter will do that."
                """,
            tools=[get_user_data, send_whatsapp_sms, web_search],
        )

        messages = [
            {"role": item.role, "content": item.content}
            for item in req.history
        ]

        result = Runner.run_streamed(starting_agent=agent, input=messages, run_config=config)

        async def event_generator():
            """
            Generator function to yield events from the result stream.
            This allows for real-time updates to the client.
            """
            async for event in result.stream_events():
                if (event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent)):
                    yield json.dumps({
                        "type": event.type,
                        "delta": event.data.delta
                    }) + "\n"

                elif (event.type == "run_item_stream_event"):
                    if event.item.type == "tool_call_output_item":
                        output = event.item.output

                        if isinstance(output, list):
                            yield json.dumps({
                                "type": event.item.type,
                                "tool_result": output
                            }) + "\n"
            
        return StreamingResponse(
                event_generator(), media_type="application/json",
                headers={"Cache-Control": "no-cache"})

    except InputGuardrailTripwireTriggered as e:
        print(f"\n\n[GUARDRAIL TRIGGERED]: {e}\n\n")
    except Exception as e:
        print(f"\n\n[ERROR]: {e}\n\n")