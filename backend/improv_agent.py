#!/usr/bin/env python3
"""
Day 10: Voice Improv Battle
Interactive improv game show with AI host
"""

import logging
import json
import os
import sys
import random
from typing import Optional, Dict, List
from dotenv import load_dotenv

# Logging
logger = logging.getLogger("improv-agent")
logging.basicConfig(level=logging.INFO)

# Load environment variables
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ENV_LOCAL = os.path.join(ROOT, ".env.local")

if os.path.exists(ENV_LOCAL):
    load_dotenv(dotenv_path=ENV_LOCAL, override=True)
    logger.info(f"🧩 Loaded env from {ENV_LOCAL}")
else:
    load_dotenv()

LIVEKIT_URL = os.getenv("LIVEKIT_URL")
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET")
LIVEKIT_AGENT_NAME = os.getenv("LIVEKIT_AGENT_NAME", "improv-agent")

logger.info(f"🔧 LIVEKIT_URL: {LIVEKIT_URL}")
logger.info(f"🔧 LIVEKIT_API_KEY: {LIVEKIT_API_KEY}")
logger.info(f"🔧 LIVEKIT_AGENT_NAME: {LIVEKIT_AGENT_NAME}")

if not LIVEKIT_URL or not LIVEKIT_API_KEY or not LIVEKIT_API_SECRET:
    logger.error("❌ Missing LiveKit env vars")
    sys.exit(1)

# LiveKit imports
from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    JobProcess,
    WorkerOptions,
    cli,
    function_tool,
    RunContext,
)
from livekit.plugins import google, deepgram, murf

try:
    from livekit.plugins import silero
except ImportError:
    silero = None

# Load scenarios
SCENARIOS_FILE = os.path.join(os.path.dirname(__file__), "scenarios.json")
scenarios_data = []

def load_scenarios():
    """Load improv scenarios from JSON"""
    global scenarios_data
    try:
        with open(SCENARIOS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            scenarios_data = data.get("scenarios", [])
        logger.info(f"✅ Loaded {len(scenarios_data)} improv scenarios")
    except Exception as e:
        logger.error(f"❌ Failed to load scenarios: {e}")
        scenarios_data = []

# Game state
improv_state = {
    "player_name": None,
    "current_round": 0,
    "max_rounds": 4,  # 4 improv scenes
    "rounds": [],  # {"scenario": str, "player_performance": str, "host_reaction": str}
    "phase": "intro",  # "intro" | "awaiting_improv" | "reacting" | "done"
    "used_scenario_ids": []
}

# Tools
@function_tool
async def start_improv_round(context: RunContext):
    """Start a new improv round with a fresh scenario"""
    global improv_state, scenarios_data
    
    if improv_state["current_round"] >= improv_state["max_rounds"]:
        logger.info("🎬 All rounds complete")
        return "All rounds complete! Time for the final summary."
    
    # Select random unused scenario
    available = [s for s in scenarios_data if s["id"] not in improv_state["used_scenario_ids"]]
    
    if not available:
        logger.warning("⚠️ No more scenarios, resetting pool")
        improv_state["used_scenario_ids"] = []
        available = scenarios_data
    
    scenario = random.choice(available)
    improv_state["used_scenario_ids"].append(scenario["id"])
    improv_state["current_round"] += 1
    improv_state["phase"] = "awaiting_improv"
    
    round_data = {
        "round_number": improv_state["current_round"],
        "scenario": scenario["scenario"],
        "player_performance": "",
        "host_reaction": ""
    }
    improv_state["rounds"].append(round_data)
    
    logger.info(f"🎭 Round {improv_state['current_round']}: {scenario['scenario']}")
    
    return f"Round {improv_state['current_round']} of {improv_state['max_rounds']}: {scenario['scenario']}"


@function_tool
async def record_host_reaction(context: RunContext, reaction: str):
    """Record the host's reaction to the player's performance"""
    global improv_state
    
    if improv_state["rounds"]:
        improv_state["rounds"][-1]["host_reaction"] = reaction
        improv_state["phase"] = "reacting"
        logger.info(f"💬 Host reaction recorded for round {improv_state['current_round']}")
    
    return "Reaction recorded"


@function_tool
async def end_improv_show(context: RunContext):
    """End the improv show and prepare for summary"""
    global improv_state
    
    improv_state["phase"] = "done"
    logger.info("🎬 Improv show ended")
    
    return "Show ended. Provide final summary now."


@function_tool
async def get_game_status(context: RunContext):
    """Get current game status"""
    global improv_state
    
    status = f"Round {improv_state['current_round']} of {improv_state['max_rounds']}\n"
    status += f"Phase: {improv_state['phase']}\n"
    status += f"Player: {improv_state['player_name'] or 'Unknown'}"
    
    return status


# Main logic
def prewarm(proc: JobProcess):
    load_scenarios()
    
    if silero:
        proc.userdata["vad"] = silero.VAD.load()
        logger.info("✅ VAD Loaded")


async def entrypoint(ctx: JobContext):
    logger.info(f"🚀 Starting Improv Battle in room: {ctx.room.name}")
    
    global improv_state
    # Reset state for new game
    improv_state = {
        "player_name": None,
        "current_round": 0,
        "max_rounds": 4,
        "rounds": [],
        "phase": "intro",
        "used_scenario_ids": []
    }
    
    await ctx.connect()

    llm = google.LLM()
    tts = murf.TTS(voice="en-US-alicia")  # Alicia for energetic host voice
    stt = deepgram.STT(model="nova-2")
    vad = ctx.proc.userdata.get("vad")

    instructions = """
    You are the energetic, witty host of "IMPROV BATTLE" - a fast-paced improv comedy game show!
    
    YOUR PERSONALITY:
    - High-energy, enthusiastic, and entertaining
    - Quick with reactions - sometimes impressed, sometimes playfully critical
    - Honest but never mean - you want players to have fun
    - Mix of supportive and teasing (like a friendly comedy club host)
    - Use humor and pop culture references
    - Keep the energy UP!
    
    GAME FLOW:
    
    1. OPENING (First interaction):
       - Welcome them with excitement: "WELCOME to IMPROV BATTLE! I'm your host!"
       - Ask for their name enthusiastically
       - Once you have their name, explain the game briefly:
         * "We're doing 4 quick improv scenes"
         * "I'll give you a scenario, you act it out"
         * "I'll react to your performance"
         * "Ready to make me laugh?"
       - Then use start_improv_round to begin Round 1
    
    2. EACH ROUND:
       a) Call start_improv_round to get the scenario
       b) Present it dramatically: "Alright [name], here's your scene: [scenario]. And... ACTION!"
       c) Listen to their improv performance (let them perform for 20-30 seconds or until they say "scene" or pause)
       d) React authentically based on what they did:
          
          REACTION STYLES (vary these):
          
          If they were creative/funny:
          - "HA! That was brilliant! The way you [specific thing] was *chef's kiss*!"
          - "Okay okay, I did NOT see that coming! Love it!"
          
          If they were okay but could improve:
          - "Not bad! Though you could've really leaned into the [character aspect] more"
          - "I see what you were going for, but the energy felt a bit flat"
          
          If they were flat or confused:
          - "Ehhh, that felt a little rushed. You had a good setup but didn't commit!"
          - "I'm not sure you really understood the scenario, but hey, points for trying!"
          
          If they were absurdly good:
          - "STOP. THAT WAS INCREDIBLE. How did you even think of that?!"
          - "Someone get this person a Netflix special!"
       
       e) After your reaction, use record_host_reaction to save it
       f) Move to next round immediately with energy: "Let's keep this rolling! Round [X]!"
    
    3. BETWEEN ROUNDS:
       - Keep the energy flowing
       - Quick transitions: "No time to rest! Next scene!"
       - Maybe tease them a bit: "Can you top that last one?"
    
    4. FINAL ROUND:
       - Build up the drama: "This is it! Your FINAL scene!"
       - Give them the hardest/weirdest scenario
       - React BIG to their final performance
    
    5. CLOSING (After 4 rounds):
       - Call end_improv_show
       - Give a fun summary of their improv style:
         * "You brought ENERGY but sometimes rushed the punchlines"
         * "You're an absurdist comedian - everything got weird fast!"
         * "You committed HARD to every character, respect!"
       - Mention 1-2 specific moments that stood out
       - Thank them with energy: "Thanks for playing IMPROV BATTLE! You were [adjective]!"
    
    IMPORTANT RULES:
    - Keep responses SHORT (2-3 sentences max between scenes)
    - Use start_improv_round tool to get each scenario
    - Don't make up scenarios - always use the tool
    - React AUTHENTICALLY - not every performance is amazing, be honest
    - Keep it FAST-PACED - no long speeches
    - Have FUN with it!
    
    PACING:
    - Intro: 30 seconds
    - Each round: 1-2 minutes (30s scenario + 30s improv + 30s reaction)
    - Total game: 5-6 minutes
    
    Let's make this show LEGENDARY!
    """

    agent = Agent(
        instructions=instructions,
        tools=[start_improv_round, record_host_reaction, end_improv_show, get_game_status],
    )

    session = AgentSession(
        vad=vad,
        stt=stt,
        llm=llm,
        tts=tts,
    )

    await session.start(agent=agent, room=ctx.room)
    
    try:
        await session.generate_reply(
            instructions="Welcome the player to IMPROV BATTLE with huge energy! Ask for their name."
        )
        logger.info("🎭 Improv Battle started!")
    except Exception as e:
        logger.error(f"❌ Error starting game: {e}")


if __name__ == "__main__":
    worker_opts = WorkerOptions(
        entrypoint_fnc=entrypoint,
        prewarm_fnc=prewarm,
        agent_name=LIVEKIT_AGENT_NAME,
        ws_url=LIVEKIT_URL,
        api_key=LIVEKIT_API_KEY,
        api_secret=LIVEKIT_API_SECRET,
    )
    cli.run_app(worker_opts)
