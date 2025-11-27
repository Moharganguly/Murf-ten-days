#!/usr/bin/env python3
"""
Day 6: Fraud Alert Voice Agent
Detects and verifies suspicious transactions with customers
"""

import logging
import os
import sys
from dotenv import load_dotenv
from fraud_db import FraudCaseDB

# Logging
logger = logging.getLogger("fraud-agent")
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
LIVEKIT_AGENT_NAME = os.getenv("LIVEKIT_AGENT_NAME", "fraud-agent")

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
fraud_db = None
current_case = {}
verification_passed = False

# Tools
@function_tool
async def verify_user_identity(context: RunContext, user_name: str, security_answer: str):
    """Verify user identity by checking username and security answer"""
    global current_case, verification_passed
    
    logger.info(f"🔍 Verifying user: {user_name}")
    
    # Get fraud case from database
    case = fraud_db.get_pending_case_by_username(user_name)
    
    if not case:
        logger.warning(f"⚠️ No pending case found for {user_name}")
        return "No pending fraud alert found for this user."
    
    current_case = case
    
    # Verify security answer (case-insensitive)
    expected_answer = case["securityAnswer"].lower().strip()
    provided_answer = security_answer.lower().strip()
    
    if provided_answer == expected_answer:
        verification_passed = True
        logger.info(f"✅ Verification successful for {user_name}")
        return f"Verification successful. I have a fraud alert regarding a transaction on your card ending in {case['cardEnding']}."
    else:
        verification_passed = False
        logger.warning(f"❌ Verification failed for {user_name}")
        return "I'm sorry, but the answer doesn't match our records. For your security, I cannot proceed with this call."

@function_tool
async def mark_transaction_safe(context: RunContext):
    """Mark the transaction as safe/legitimate"""
    global current_case
    
    if not current_case:
        return "No active fraud case to update."
    
    fraud_db.update_case_status(
        case_id=current_case["id"],
        status="confirmed_safe",
        outcome=f"Customer confirmed the ${current_case['transactionAmount']:.2f} transaction to {current_case['transactionName']} as legitimate."
    )
    
    logger.info(f"✅ Marked case {current_case['id']} as SAFE")
    return "Transaction marked as safe. No further action needed. Thank you for confirming."

@function_tool
async def mark_transaction_fraudulent(context: RunContext):
    """Mark the transaction as fraudulent and block the card"""
    global current_case
    
    if not current_case:
        return "No active fraud case to update."
    
    fraud_db.update_case_status(
        case_id=current_case["id"],
        status="confirmed_fraud",
        outcome=f"Customer denied the ${current_case['transactionAmount']:.2f} transaction to {current_case['transactionName']}. Card ending in {current_case['cardEnding']} blocked. Dispute raised."
    )
    
    logger.info(f"🚨 Marked case {current_case['id']} as FRAUDULENT")
    return f"I've immediately blocked your card ending in {current_case['cardEnding']} and initiated a dispute for this transaction. You will receive a replacement card within 5-7 business days."

# Main logic
def prewarm(proc: JobProcess):
    global fraud_db
    fraud_db = FraudCaseDB()
    
    if silero:
        proc.userdata["vad"] = silero.VAD.load()
        logger.info("✅ VAD Loaded")
    
    logger.info("✅ Fraud database initialized")

async def entrypoint(ctx: JobContext):
    logger.info(f"🚀 Starting Fraud Alert Agent in room: {ctx.room.name}")
    
    global current_case, verification_passed
    current_case = {}
    verification_passed = False
    
    await ctx.connect()

    llm = google.LLM()
    tts = murf.TTS(voice="en-US-matthew")
    stt = deepgram.STT(model="nova-2")
    vad = ctx.proc.userdata.get("vad")

    instructions = """
    You are a professional fraud detection agent for SecureBank.
    
    Your conversation flow:
    
    1. GREETING:
       - Introduce yourself: "Hello, this is the SecureBank Fraud Prevention Department."
       - Explain: "We've detected a suspicious transaction on your account and need to verify it with you."
    
    2. VERIFICATION:
       - Ask: "May I have your full name please?"
       - Then ask their security question using verify_user_identity tool
       - If verification fails, politely end the call
    
    3. TRANSACTION DETAILS (only if verified):
       - Read out the suspicious transaction details clearly:
         * Amount
         * Merchant name
         * Location
         * Time
         * Card ending
    
    4. CONFIRMATION:
       - Ask clearly: "Did you authorize this transaction?"
       - If YES → use mark_transaction_safe tool
       - If NO → use mark_transaction_fraudulent tool
    
    5. CLOSING:
       - Summarize the action taken
       - Thank them for their time
       - End professionally
    
    Important:
    - Be calm, professional, and reassuring
    - Never ask for full card numbers, PINs, or passwords
    - Keep responses concise and clear
    - Use the tools provided to verify identity and update case status
    """

    agent = Agent(
        instructions=instructions,
        tools=[verify_user_identity, mark_transaction_safe, mark_transaction_fraudulent],
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
            instructions="Introduce yourself as SecureBank Fraud Prevention Department and explain you're calling about a suspicious transaction."
        )
        logger.info("✅ Greeting sent successfully")
    except Exception as e:
        logger.error(f"❌ Error generating greeting: {e}")

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
