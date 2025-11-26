#!/usr/bin/env python3
"""
Health & Wellness Voice Companion - LiveKit Agents v1.3.x
Uses Agent and AgentSession (new API)
A supportive daily check-in agent that tracks mood, energy, and daily goals.
"""

import logging
import json
import os
import sys
from datetime import datetime
from typing import Annotated
from dotenv import load_dotenv

# LiveKit core (v1.3.x)
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

# Cloud plugins
from livekit.plugins import openai, deepgram, cartesia

# Try to import silero for VAD (optional)
try:
    from livekit.plugins import silero
except Exception:
    silero = None
    print("⚠️ Silero VAD not available (optional)")

# Setup logging
logger = logging.getLogger("wellness-companion")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s - %(message)s"
)

# Load environment variables
load_dotenv(dotenv_path=".env.local")

# Setup directories
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
WELLNESS_DIR = os.path.join(ROOT, "wellness_data")
os.makedirs(WELLNESS_DIR, exist_ok=True)

# Wellness log file
WELLNESS_LOG_FILE = os.path.join(WELLNESS_DIR, "wellness_log.json")

print("\n" + "🌟" * 10)
print("🧘 WELLNESS COMPANION - DAILY CHECK-IN AGENT v1.3")
print(f"📁 Check-ins will be saved to: {WELLNESS_DIR}")
print("🌟" * 10 + "\n")


# ---------------------------
# Data Management
# ---------------------------
class WellnessDataManager:
    """Manages reading and writing wellness check-in data."""
    
    def __init__(self, log_file: str = WELLNESS_LOG_FILE):
        self.log_file = log_file
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        """Create the JSON file if it doesn't exist."""
        if not os.path.exists(self.log_file):
            with open(self.log_file, 'w') as f:
                json.dump({"check_ins": []}, f, indent=2)
    
    def load_history(self) -> dict:
        """Load all check-in history."""
        try:
            with open(self.log_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            logger.warning("Could not load history, returning empty data")
            return {"check_ins": []}
    
    def get_last_check_in(self) -> dict | None:
        """Get the most recent check-in."""
        data = self.load_history()
        check_ins = data.get("check_ins", [])
        return check_ins[-1] if check_ins else None
    
    def save_check_in(self, check_in_data: dict):
        """Save a new check-in entry."""
        data = self.load_history()
        check_in_data["timestamp"] = datetime.utcnow().isoformat()
        data["check_ins"].append(check_in_data)
        
        with open(self.log_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info("✅ CHECK-IN SAVED: %s", check_in_data)
        print(f"\n{'='*60}")
        print(f"✅ CHECK-IN SAVED SUCCESSFULLY!")
        print(f"{'='*60}")
        print(f"📅 Date: {check_in_data['timestamp'][:10]}")
        print(f"😊 Mood: {check_in_data.get('mood_summary', 'N/A')}")
        print(f"🎯 Objectives: {', '.join(check_in_data.get('objectives', []))}")
        print(f"{'='*60}\n")


# Global data manager instance
data_manager = WellnessDataManager()

# Session state to track current check-in
current_check_in = {}


def create_system_instructions(last_check_in: dict | None) -> str:
    """Create context-aware system instructions."""
    base_instructions = """You are a supportive health and wellness companion conducting a daily check-in.

Your role:
- Be warm, empathetic, and grounded (not overly cheerful or clinical)
- Have a natural conversation - don't follow a rigid script
- Ask about mood, energy levels, and what's on their mind
- Ask about their intentions and goals for the day (1-3 things)
- Offer simple, realistic, actionable suggestions when appropriate
- NEVER diagnose, provide medical advice, or act as a therapist
- Keep the conversation focused and relatively brief (5-10 minutes)

Conversation flow:
1. Greet warmly and ask how they're feeling today
2. Explore their current mood and energy naturally (ask ONE question at a time)
3. Once you understand their mood, call record_mood() to save it
4. Ask about their goals or intentions for the day
5. Once you know their objectives, call record_objectives() to save them
6. Offer 1-2 small, practical suggestions if helpful
7. Recap their mood and main objectives briefly
8. Ask "Does this sound right?" to confirm
9. Once confirmed, call complete_check_in() to save everything

Advice guidelines:
- Keep suggestions small and immediately actionable
- Examples: take short breaks, break big tasks into steps, 5-minute walks, hydration reminders
- Avoid anything that sounds like medical or mental health treatment
- Be realistic about what's achievable

IMPORTANT:
- Ask ONE question at a time
- Don't rush - let the conversation flow naturally
- Use the tools (record_mood, record_objectives, complete_check_in) at the right moments
- Keep responses brief and conversational

Remember: You're a supportive companion, not a coach, therapist, or medical professional."""

    # Add context from previous check-in if available
    if last_check_in:
        date = last_check_in.get("timestamp", "last time")[:10]  # Just the date
        mood = last_check_in.get("mood_summary", "")
        objectives = last_check_in.get("objectives", [])
        
        context = f"\n\nPrevious check-in context (from {date}):\n"
        if mood:
            context += f"- They mentioned feeling: {mood}\n"
        if objectives:
            context += f"- Their goals were: {', '.join(objectives[:3])}\n"
        context += "\nReference this naturally early in the conversation to show continuity."
        
        return base_instructions + context
    
    return base_instructions


# ---------------------------
# Function Tools (Basic - No MCP)
# ---------------------------

@function_tool
async def record_mood(
    context: RunContext,
    mood_summary: Annotated[str, "A brief summary of how the user is feeling today (mood and energy)"],
):
    """Save the user's mood and energy summary from today's check-in"""
    logger.info("😊 record_mood called!")
    logger.info("   Mood: %s", mood_summary)
    
    global current_check_in
    current_check_in["mood_summary"] = mood_summary
    
    logger.info("✅ Mood recorded successfully")
    return f"Got it - I've noted that you're feeling: {mood_summary}"


@function_tool
async def record_objectives(
    context: RunContext,
    objectives: Annotated[str, "Comma-separated list of 1-3 main things the user wants to accomplish today"],
):
    """Save the user's main objectives or intentions for today"""
    logger.info("🎯 record_objectives called!")
    logger.info("   Objectives: %s", objectives)
    
    # Parse objectives
    objectives_list = []
    if objectives and objectives.strip():
        objectives_list = [obj.strip() for obj in objectives.split(",") if obj.strip()]
    
    global current_check_in
    current_check_in["objectives"] = objectives_list
    
    logger.info("✅ Objectives recorded successfully")
    return f"Perfect! I've noted your goals: {', '.join(objectives_list)}"


@function_tool
async def complete_check_in(
    context: RunContext,
    agent_summary: Annotated[str, "A one-sentence summary of the check-in from the agent's perspective"],
):
    """Complete and save today's check-in after confirming the recap with the user"""
    logger.info("✨ complete_check_in called!")
    logger.info("   Summary: %s", agent_summary)
    
    global current_check_in
    
    # Add agent summary
    current_check_in["agent_summary"] = agent_summary
    
    # Validate we have the required fields
    if "mood_summary" not in current_check_in or "objectives" not in current_check_in:
        logger.warning("⚠️ Incomplete check-in data")
        return (
            "I notice we haven't captured all the information yet. "
            "Let me make sure I have your mood and goals before we finish."
        )
    
    try:
        # Save to file
        data_manager.save_check_in(current_check_in)
        
        mood = current_check_in.get('mood_summary', 'Your mood')
        obj_count = len(current_check_in.get('objectives', []))
        
        result_message = (
            f"Perfect! I've saved today's check-in. "
            f"You're feeling {mood.lower()} and have {obj_count} goal{'s' if obj_count != 1 else ''} for the day. "
            f"Have a wonderful day, and I'll check in with you again tomorrow!"
        )
        
        logger.info("✅ Check-in completed successfully")
        
        # Reset for next session
        current_check_in.clear()
        
        return result_message
        
    except Exception as e:
        logger.error("❌ Failed to save check-in: %s", e, exc_info=True)
        return "I apologize, there was an error saving your check-in. Could we try again?"


# ---------------------------
# Prewarm Function
# ---------------------------
def prewarm(proc: JobProcess):
    """Prewarm VAD if available"""
    print("🔥 Prewarming...")
    
    if silero is None:
        print("⚠️ Silero VAD not available (using fallback)")
        proc.userdata["vad"] = None
        return
    
    try:
        if hasattr(silero, "VAD") and hasattr(silero.VAD, "load"):
            proc.userdata["vad"] = silero.VAD.load()
            print("✅ Silero VAD loaded successfully")
        else:
            proc.userdata["vad"] = None
            print("⚠️ VAD not available")
    except Exception as e:
        print(f"⚠️ VAD prewarm failed: {e}")
        proc.userdata["vad"] = None


# ---------------------------
# Main Entrypoint
# ---------------------------
async def entrypoint(ctx: JobContext):
    """Main entry point for the wellness companion"""
    logger.info("=" * 60)
    logger.info("🧘 NEW WELLNESS CHECK-IN SESSION STARTED")
    logger.info("Room: %s", ctx.room.name)
    logger.info("=" * 60)
    
    # Connect to room
    await ctx.connect()
    
    # Load previous check-in for context
    last_check_in = data_manager.get_last_check_in()
    check_in_count = len(data_manager.load_history().get("check_ins", []))
    
    # Create context-aware system instructions
    instructions = create_system_instructions(last_check_in)
    
    # Initialize plugins
    logger.info("🔌 Initializing plugins...")
    
    try:
        # STT: Deepgram
        stt_plugin = deepgram.STT(model="nova-2")
        logger.info("✅ Deepgram STT initialized")
        
        # LLM: OpenAI
        llm_plugin = openai.LLM(model="gpt-4o-mini")
        logger.info("✅ OpenAI LLM initialized (gpt-4o-mini)")
        
        # TTS: Cartesia
        tts_plugin = cartesia.TTS()
        logger.info("✅ Cartesia TTS initialized")
        
        # VAD: Silero (from prewarm)
        vad_plugin = ctx.proc.userdata.get("vad")
        if vad_plugin:
            logger.info("✅ Using prewarmed Silero VAD")
        else:
            logger.info("⚠️ No VAD available (will use fallback)")
        
    except Exception as e:
        logger.error("❌ Plugin initialization failed: %s", e, exc_info=True)
        logger.error("Please check your API keys in .env.local:")
        logger.error("  - OPENAI_API_KEY")
        logger.error("  - DEEPGRAM_API_KEY")
        logger.error("  - CARTESIA_API_KEY")
        return
    
    # Create the Agent with instructions and tools
    agent = Agent(
        instructions=instructions,
        tools=[record_mood, record_objectives, complete_check_in],
    )
    
    # Create the AgentSession with plugins
    session = AgentSession(
        vad=vad_plugin,
        stt=stt_plugin,
        llm=llm_plugin,
        tts=tts_plugin,
    )
    
    # Start the session
    logger.info("🎙️ Starting wellness check-in session...")
    await session.start(agent=agent, room=ctx.room)
    
    # Generate initial greeting based on history
    if last_check_in and check_in_count > 1:
        greeting = (
            f"Hi! Welcome back to your daily check-in. "
            f"This is check-in number {check_in_count}. "
            f"How are you feeling today?"
        )
    elif last_check_in:
        greeting = (
            "Hi! Welcome back! "
            "How are you feeling today?"
        )
    else:
        greeting = (
            "Hello! Welcome to your first wellness check-in. "
            "I'm here to support you with a quick daily check-in. "
            "How are you feeling today?"
        )
    
    try:
        await session.generate_reply(instructions=greeting)
        logger.info("✅ Greeting generated successfully")
    except Exception as e:
        logger.error("❌ Failed to generate greeting: %s", e)
    
    # The session will continue until participant disconnects
    logger.info("✅ Session active - agent is listening...")


# ---------------------------
# CLI Entry Point
# ---------------------------
if __name__ == "__main__":
    logger.info("🚀 Starting Wellness Companion Agent...")
    logger.info("Wellness data directory: %s", WELLNESS_DIR)
    
    # Check for required API keys
    required_keys = ["OPENAI_API_KEY", "DEEPGRAM_API_KEY", "CARTESIA_API_KEY"]
    missing_keys = [key for key in required_keys if not os.getenv(key)]
    
    if missing_keys:
        logger.error("❌ Missing required API keys in .env.local:")
        for key in missing_keys:
            logger.error("   - %s", key)
        logger.error("Please add these keys to your .env.local file")
        sys.exit(1)
    
    logger.info("✅ All required API keys found")
    logger.info("Starting LiveKit worker...")
    
    cli.run_app(WorkerOptions(
        entrypoint_fnc=entrypoint,
        prewarm_fnc=prewarm
    ))