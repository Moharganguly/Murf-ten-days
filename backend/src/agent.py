import logging
import json
from dotenv import load_dotenv
from typing import Annotated
load_dotenv(dotenv_path=".env.local")

from livekit.agents import AutoSubscribe, JobContext, JobProcess, WorkerOptions, cli, llm

# --- IMPORT HUNTING ---
try:
    from livekit.agents.pipeline import VoicePipelineAgent
except ImportError:
    # This import works for some v1.x versions
    from livekit.agents import VoicePipelineAgent 

# --- TOOL DECORATOR FIX ---
try:
    # Old way
    ai_callable = llm.ai_callable
except AttributeError:
    # New way (v1.2+) - might be in function_context or just moved
    # Let's try to find it or define a dummy if we just want it to run
    try:
        from livekit.agents.llm import function_context
        ai_callable = function_context.ai_callable
    except ImportError:
         # If we really can't find it, we just define a wrapper so the code runs
         # (The tool won't work, but the agent will start)
         def ai_callable(description):
             def decorator(func):
                 func.description = description
                 return func
             return decorator
         print("⚠️ WARNING: ai_callable not found. Tools might not work.")

from livekit.plugins import openai, deepgram, silero, murf

logger = logging.getLogger("voice-agent")

class BaristaTools:
    @ai_callable(description="Save the customer's final coffee order to a file")
    def save_order(
        self,
        drink_type: Annotated[str, llm.TypeInfo(description="The type of coffee")],
        size: Annotated[str, llm.TypeInfo(description="The size of the drink")],
        milk: Annotated[str, llm.TypeInfo(description="Type of milk")],
        extras: Annotated[str, llm.TypeInfo(description="Any extras")],
        name: Annotated[str, llm.TypeInfo(description="The customer's name")]
    ):
        order_data = {"drink": drink_type, "size": size, "milk": milk, "extras": extras, "name": name}
        print(f"💾 Saving order: {order_data}")
        with open("order.json", "w") as f:
            json.dump(order_data, f, indent=2)
        return "Order saved."

def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()

async def entrypoint(ctx: JobContext):
    initial_ctx = llm.ChatContext().append(
        role="system",
        text="You are a friendly barista. Collect Drink, Size, Milk, Extras, Name. Then call save_order."
    )
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)
    participant = await ctx.wait_for_participant()

    agent = VoicePipelineAgent(
        vad=ctx.proc.userdata["vad"],
        stt=deepgram.STT(),
        llm=openai.LLM(),
        tts=murf.TTS(model="en-US-falcon", voice="en-US-falcon-medium"),
        fnc_ctx=BaristaTools(),
        chat_ctx=initial_ctx,
    )
    agent.start(ctx.room, participant)
    await agent.say("Hi! Welcome to Murf's.", allow_interruptions=True)

if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm))
