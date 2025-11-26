#!/usr/bin/env python3
"""
Day 5: SDR (Sales Development Representative) + Lead Capture
Voice agent that answers FAQs and captures lead information
UPDATED: Uses Murf AI (Falcon) for TTS + Gemini 2.0 + ENV-BASED LIVEKIT CONFIG
"""

import logging
import json
import os
import sys
from datetime import datetime
from typing import Annotated
from dotenv import load_dotenv

# ---------------------------
# Logging
# ---------------------------
logger = logging.getLogger("sdr-agent")
logging.basicConfig(level=logging.INFO)

# ---------------------------
# Load environment variables
# ---------------------------
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ENV_LOCAL = os.path.join(ROOT, ".env.local")
ENV_DEFAULT = os.path.join(ROOT, ".env")

if os.path.exists(ENV_LOCAL):
    load_dotenv(dotenv_path=ENV_LOCAL, override=True)
    logger.info(f"🧩 Loaded env from {ENV_LOCAL}")
elif os.path.exists(ENV_DEFAULT):
    load_dotenv(dotenv_path=ENV_DEFAULT, override=True)
    logger.info(f"🧩 Loaded env from {ENV_DEFAULT}")
else:
    load_dotenv()
    logger.warning("⚠️ .env / .env.local not found in backend root, loaded default env")

LIVEKIT_URL = os.getenv("LIVEKIT_URL")
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET")

# 👇 agent name from env, with a good default
LIVEKIT_AGENT_NAME = os.getenv("LIVEKIT_AGENT_NAME", "sdr-agent")

logger.info(f"🔧 LIVEKIT_URL: {LIVEKIT_URL}")
logger.info(f"🔧 LIVEKIT_API_KEY: {LIVEKIT_API_KEY}")
logger.info(f"🔧 LIVEKIT_AGENT_NAME: {LIVEKIT_AGENT_NAME}")
# Do NOT log secret

# Simple sanity check so failure is obvious
if not LIVEKIT_URL or not LIVEKIT_API_KEY or not LIVEKIT_API_SECRET:
    logger.error("❌ Missing one or more LiveKit env vars (LIVEKIT_URL / LIVEKIT_API_KEY / LIVEKIT_API_SECRET)")
    sys.exit(1)

# ---------------------------
# LiveKit / plugins imports
# ---------------------------
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

# ---------------------------
# Paths / data dirs
# ---------------------------
SHARED_DATA_DIR = os.path.join(ROOT, "shared_data")
LEADS_DIR = os.path.join(ROOT, "leads")
os.makedirs(SHARED_DATA_DIR, exist_ok=True)
os.makedirs(LEADS_DIR, exist_ok=True)

FAQ_FILE = os.path.join(SHARED_DATA_DIR, "razorpay_faq.json")

# ---------------------------
# FAQ Manager
# ---------------------------
class FAQManager:
    def __init__(self, faq_file: str):
        self.faq_file = faq_file
        self.data = self._load_faq()
    
    def _load_faq(self):
        if not os.path.exists(self.faq_file):
            logger.warning(f"⚠️ FAQ file not found at {self.faq_file}")
            return {}
        try:
            with open(self.faq_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load FAQ: {e}")
            return {}

    def search(self, query: str):
        query_lower = query.lower().split()
        results = []
        for faq in self.data.get("faq", []):
            score = 0
            q_text = faq.get("question", "").lower()
            a_text = faq.get("answer", "").lower()
            for word in query_lower:
                if word in q_text:
                    score += 3
                if word in a_text:
                    score += 1
            if score > 0:
                results.append({**faq, "score": score})
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:3]

    def get_company_info(self):
        return self.data.get("company", {})

# Global manager + lead state
faq_manager = None
current_lead = {}

# ---------------------------
# Tools
# ---------------------------
@function_tool
async def save_lead_field(context: RunContext, field_name: str, field_value: str):
    """Save a specific piece of lead info (name, email, company, role, etc.)"""
    current_lead[field_name] = field_value
    logger.info(f"💾 Captured {field_name}: {field_value}")
    return f"Saved {field_name}."

@function_tool
async def search_company_faq(context: RunContext, question: str):
    """Search the FAQ for an answer to the user's question"""
    if not faq_manager:
        return "I don't have access to the FAQ right now."
    results = faq_manager.search(question)
    if not results:
        return "I couldn't find an answer in my manual."
    return results[0]["answer"]

@function_tool
async def complete_call_and_save_lead(context: RunContext, summary: str):
    """Finalize the call and save the lead to disk"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    name_slug = current_lead.get("name", "unknown").replace(" ", "_")
    filename = f"lead_{name_slug}_{timestamp}.json"
    path = os.path.join(LEADS_DIR, filename)
    
    current_lead["summary"] = summary
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(current_lead, f, indent=2)
        logger.info(f"✅ Lead saved to {path}")
    except Exception as e:
        logger.error(f"❌ Failed to save lead: {e}")
    
    return "Lead saved successfully. Thank the user and say goodbye."

# ---------------------------
# Main Logic
# ---------------------------
def prewarm(proc: JobProcess):
    global faq_manager
    faq_manager = FAQManager(FAQ_FILE)
    if silero:
        proc.userdata["vad"] = silero.VAD.load()
        logger.info("✅ VAD Loaded")

async def entrypoint(ctx: JobContext):
    logger.info(f"🚀 Starting SDR Agent in room: {ctx.room.name}")
    
    global current_lead
    current_lead = {}
    
    await ctx.connect()

    # 🔥 FIXED: Use default Gemini model (gemini-2.0-flash-exp) - compatible with LiveKit plugin
    llm = google.LLM()  # ✅ Uses default compatible model
    tts = murf.TTS(voice="en-US-matthew")  # ✅ Matthew voice from Murf Falcon
    stt = deepgram.STT(model="nova-2")
    vad = ctx.proc.userdata.get("vad")

    info = faq_manager.get_company_info()
    company = info.get("name", "Razorpay")
    
    instructions = f"""
        You are a friendly Sales Rep for {company}.
        Your goal is to qualify leads and answer questions.
        
        1. Greet the user and ask what brought them here.
        2. Answer questions using the tool 'search_company_faq'.
        3. Collect Name, Company, Email, and Use Case using 'save_lead_field'.
        4. When the user is done, use 'complete_call_and_save_lead'.
        
        Be concise, professional, and helpful.
    """

    agent = Agent(
        instructions=instructions,
        tools=[save_lead_field, search_company_faq, complete_call_and_save_lead],
    )

    session = AgentSession(
        vad=vad,
        stt=stt,
        llm=llm,
        tts=tts,
    )

    # 🔥 Added await
    await session.start(agent=agent, room=ctx.room)
    
    try:
        await session.generate_reply(
            instructions=f"Say 'Hi! Welcome to {company}. How can I help you today?'"
        )
        logger.info("✅ Greeting sent successfully")
    except Exception as e:
        logger.error(f"❌ Error generating greeting: {e}")

if __name__ == "__main__":
    # 👇 Explicitly pass url, api_key, api_secret from environment
    worker_opts = WorkerOptions(
        entrypoint_fnc=entrypoint,
        prewarm_fnc=prewarm,
        agent_name=LIVEKIT_AGENT_NAME,
        # 🔥 Explicitly set these to force use of env variables
        ws_url=LIVEKIT_URL,
        api_key=LIVEKIT_API_KEY,
        api_secret=LIVEKIT_API_SECRET,
    )
    cli.run_app(worker_opts)
