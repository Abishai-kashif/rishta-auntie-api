import os
import json
from dotenv import load_dotenv
from agents import (
        Agent, Runner, OpenAIChatCompletionsModel,
        AsyncOpenAI, function_tool, InputGuardrailTripwireTriggered,
        RunConfig
    )
from openai.types.responses import ResponseTextDeltaEvent
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from models import PromptRequest, GuardrailOutput
from fastapi import FastAPI

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

        @function_tool
        def get_user_data(min_age: int) -> list[dict]:
            "Retrieve user data based on a minimum age"
            users = [
                {"name": "Muneeb", "age": 22, "location": "Karachi", "interests": ["reading", "gaming"]},
                {"name": "Muhammad Ubaid Hussain", "age": 25, "location": "Lahore", "interests": ["coding", "music"]},
                {"name": "Azan", "age": 19, "location": "Islamabad", "interests": ["sports", "traveling"]},
            ]

            for user in users:
                if user["age"] < min_age:
                    users.remove(user)

            return users


        agent = Agent(
            name="Rishta Auntie",
            instructions="You’re a kind and helpful auntie who assists people in finding matches. You should only respond to questions related to matchmaking or simple greetings (like ‘hi’), and ignore all other types of queries.",
            tools=[get_user_data],
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
                    })
                elif (event.type == "run_item_stream_event"):
                    if event.item.type == "tool_call_output_item":
                        yield json.dumps({
                            "type": event.item.type,
                            "tool_result": event.item.output
                        })

        
        return StreamingResponse(
                event_generator(), media_type="application/json",
                headers={"Cache-Control": "no-cache"})

    except InputGuardrailTripwireTriggered as e:
        print(f"\n\n[GUARDRAIL TRIGGERED]: {e}\n\n")
    except Exception as e:
        print(f"\n\n[ERROR]: {e}\n\n")