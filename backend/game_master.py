#!/usr/bin/env python3
"""
Day 8: Voice Game Master (D&D-Style Adventure)
Interactive storytelling with voice-driven RPG experience
"""

import logging
import json
import os
import sys
from datetime import datetime
from typing import Optional, Dict, List
from dotenv import load_dotenv

# Logging
logger = logging.getLogger("game-master")
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
LIVEKIT_AGENT_NAME = os.getenv("LIVEKIT_AGENT_NAME", "game-master")

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

# Global state
adventure_state = {
    "player_name": "Adventurer",
    "location": "Starting Village",
    "inventory": [],
    "turn_count": 0
}

# Tools (optional, for stat tracking)
@function_tool
async def record_player_choice(context: RunContext, choice: str):
    """Record a significant player choice for continuity"""
    global adventure_state
    adventure_state['turn_count'] += 1
    logger.info(f"🎲 Turn {adventure_state['turn_count']}: Player chose: {choice}")
    return f"Noted: {choice}"

@function_tool
async def add_to_inventory(context: RunContext, item: str):
    """Add an item to player's inventory"""
    global adventure_state
    if item not in adventure_state['inventory']:
        adventure_state['inventory'].append(item)
        logger.info(f"🎒 Added to inventory: {item}")
        return f"You obtained: {item}!"
    return f"You already have: {item}"

@function_tool
async def check_inventory(context: RunContext):
    """Check player's current inventory"""
    global adventure_state
    if not adventure_state['inventory']:
        return "Your inventory is empty."
    items = ", ".join(adventure_state['inventory'])
    return f"Your inventory: {items}"

# Main logic
def prewarm(proc: JobProcess):
    if silero:
        proc.userdata["vad"] = silero.VAD.load()
        logger.info("✅ VAD Loaded")

async def entrypoint(ctx: JobContext):
    logger.info(f"🚀 Starting Game Master in room: {ctx.room.name}")
    
    global adventure_state
    # Reset state for new game
    adventure_state = {
        "player_name": "Adventurer",
        "location": "Starting Village",
        "inventory": [],
        "turn_count": 0
    }
    
    await ctx.connect()

    llm = google.LLM()
    tts = murf.TTS(voice="en-US-ken")  # Ken for dramatic storytelling voice
    stt = deepgram.STT(model="nova-2")
    vad = ctx.proc.userdata.get("vad")

    # Epic Game Master Instructions
    instructions = """
    You are an experienced Dungeon Master running a fantasy D&D adventure in the realm of Eldoria.
    
    UNIVERSE & SETTING:
    - Fantasy medieval world with magic, dragons, and ancient ruins
    - Player is a brave adventurer seeking the legendary Crystal of Eternity
    - Tone: Dramatic, immersive, with moments of danger and wonder
    - NPCs have personality and memorable quirks
    
    YOUR ROLE AS GAME MASTER:
    
    1. OPENING (First Message):
       - Welcome player warmly as the Game Master
       - Set the scene dramatically: "You stand at the edge of Whispering Woods..."
       - Ask for their character name
       - Once they give a name, begin the adventure
    
    2. STORYTELLING STYLE:
       - Use vivid, sensory descriptions (sights, sounds, smells)
       - Create tension and atmosphere
       - Keep descriptions concise (2-3 sentences max)
       - End EVERY response with: "What do you do?"
    
    3. PLAYER AGENCY:
       - Accept ANY reasonable action the player suggests
       - If they try something creative, reward it with interesting outcomes
       - If they try something impossible, offer a dramatic failure or alternative
       - Remember their past choices and reference them
    
    4. STORY PROGRESSION:
       - Guide them through 3 main story beats:
         a) Starting village → Learn about the Crystal quest
         b) Journey through dangerous location (forest/dungeon/mountain)
         c) Encounter with guardian/obstacle → Mini climax
       - Aim for 8-15 exchanges total
       - Build to a satisfying mini-conclusion
    
    5. INTERACTIVE ELEMENTS:
       - Include NPCs they can talk to
       - Present choices (but let them decide how to respond)
       - Add combat encounters (describe dramatically, let them say actions)
       - Include puzzles or mysteries
    
    6. CONTINUITY:
       - Remember:
         * Player's name
         * Items they've found/taken
         * NPCs they've met
         * Decisions they've made
       - Reference these naturally in the story
    
    7. ENDING:
       - After 8-12 exchanges, start guiding toward conclusion
       - Give them a sense of accomplishment
       - End with: "This adventure has concluded. Would you like to start a new quest?"
    
    EXAMPLE FLOW:
    
    GM: "Welcome, brave soul! You stand at the edge of Whispering Woods, where ancient magic still lingers. What is your name, adventurer?"
    
    Player: "I'm Thorin"
    
    GM: "Well met, Thorin! The village elder beckons you to the town square. His eyes are filled with worry. What do you do?"
    
    Player: "I approach the elder"
    
    GM: "The old man's voice trembles as he speaks: 'The Crystal of Eternity has been stolen by shadow creatures! Without it, our crops will wither.' He points toward the dark forest. What do you do?"
    
    IMPORTANT:
    - Be dramatic and engaging
    - Keep the pace moving
    - ALWAYS end with a question/prompt for action
    - Make the player feel like a hero
    - Have fun with it!
    """

    agent = Agent(
        instructions=instructions,
        tools=[record_player_choice, add_to_inventory, check_inventory],
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
            instructions="Welcome the player as Game Master and set the opening scene in Eldoria. Ask for their character name."
        )
        logger.info("✅ Adventure started!")
    except Exception as e:
        logger.error(f"❌ Error starting adventure: {e}")

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
