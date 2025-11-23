#!/usr/bin/env python3
"""
Coffee Shop Barista Agent - LiveKit Agents v1.3.x
Uses Agent and AgentSession (new API)
"""


import logging
import json
import os
import sys
import asyncio
from datetime import datetime
from typing import Annotated, Optional
from dataclasses import dataclass, field


from dotenv import load_dotenv


# LiveKit core (v1.3.x uses different imports)
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
logger = logging.getLogger("coffee-barista")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s - %(message)s"
)


# Load environment variables
load_dotenv(dotenv_path=".env.local")


# Setup directories
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ORDERS_DIR = os.path.join(ROOT, "orders")
os.makedirs(ORDERS_DIR, exist_ok=True)


print("\n" + "☕" * 10)
print("🚀 MG'S CAFE - COFFEE SHOP AGENT v1.3")
print(f"📁 Orders will be saved to: {ORDERS_DIR}")
print("☕" * 10 + "\n")



# ---------------------------
# Order Management
# ---------------------------
@dataclass
class OrderState:
    drinkType: Optional[str] = None
    size: Optional[str] = None
    milk: Optional[str] = None
    extras: list[str] = field(default_factory=list)
    name: Optional[str] = None


    def to_dict(self) -> dict:
        return {
            "drinkType": self.drinkType,
            "size": self.size,
            "milk": self.milk,
            "extras": self.extras,
            "name": self.name
        }


    def get_summary(self) -> str:
        extras_text = f" with {', '.join(self.extras)}" if self.extras else ""
        return f"{self.size} {self.drinkType} with {self.milk} milk{extras_text} for {self.name}"



def save_order_to_json(order: OrderState) -> str:
    """Save order to JSON file and return the file path"""
    safe_name = "".join(
        c for c in (order.name or "guest") 
        if c.isalnum() or c in (" ", "_")
    ).strip().replace(" ", "_")
    
    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    filename = f"{safe_name}_{timestamp}.json"
    fullpath = os.path.join(ORDERS_DIR, filename)


    payload = order.to_dict()
    payload["timestamp"] = datetime.utcnow().isoformat()
    payload["order_number"] = timestamp


    with open(fullpath, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


    logger.info("✅ ORDER SAVED: %s", fullpath)
    print(f"\n{'='*60}")
    print(f"✅ ORDER SAVED SUCCESSFULLY!")
    print(f"{'='*60}")
    print(f"📄 File: {filename}")
    print(f"📦 Order: {order.get_summary()}")
    print(f"{'='*60}\n")
    
    return fullpath



# ---------------------------
# Function Tools (using @function_tool decorator for v1.3.x)
# ---------------------------


@function_tool
async def complete_order(
    context: RunContext,
    drinkType: Annotated[str, "Type of drink (e.g., latte, cappuccino, espresso)"],
    size: Annotated[str, "Size: small, medium, or large"],
    milk: Annotated[str, "Type of milk: whole, skim, oat, almond, soy, or none"],
    name: Annotated[str, "Customer's name for the order"],
    extras: Annotated[str, "Comma-separated extras or empty string if none"] = "",
):
    """Complete and save the customer's coffee order"""
    logger.info("🎉 complete_order called!")
    logger.info("   Drink: %s", drinkType)
    logger.info("   Size: %s", size)
    logger.info("   Milk: %s", milk)
    logger.info("   Name: %s", name)
    logger.info("   Extras: %s", extras or "none")
    
    # Parse extras
    extras_list = []
    if extras and extras.strip():
        extras_list = [e.strip() for e in extras.split(",") if e.strip()]


    # Create order
    order = OrderState(
        drinkType=drinkType,
        size=size,
        milk=milk,
        extras=extras_list,
        name=name,
    )
    
    try:
        filepath = save_order_to_json(order)
        order_number = os.path.basename(filepath).split("_")[-1].replace(".json", "")
        summary = order.get_summary()
        
        result_message = (
            f"Perfect! I've completed your order: {summary}. "
            f"Your order number is {order_number}. "
            f"It'll be ready in just a few minutes! "
            f"Thank you for choosing MG'S cafe!"
        )
        
        logger.info("✅ Order completed successfully")
        return result_message
        
    except Exception as e:
        logger.error("❌ Failed to save order: %s", e, exc_info=True)
        return "I apologize, there was an error saving your order. Could you please repeat your order?"



@function_tool
async def get_order_status(
    context: RunContext,
    name: Annotated[Optional[str], "Customer name to look up"] = None
):
    """Check order status for a customer"""
    logger.info("📋 Checking order status for: %s", name or "latest")
    
    try:
        files = sorted(
            [f for f in os.listdir(ORDERS_DIR) if f.endswith(".json")],
            reverse=True
        )
        
        if not files:
            return "No orders have been placed yet."
        
        if name:
            # Search for orders matching the name
            for filename in files:
                try:
                    with open(os.path.join(ORDERS_DIR, filename), "r") as f:
                        data = json.load(f)
                    if data.get("name", "").lower() == name.lower():
                        return (
                            f"Found order for {name}: "
                            f"{data.get('size')} {data.get('drinkType')} "
                            f"with {data.get('milk')} milk"
                        )
                except Exception:
                    continue
            return f"No orders found for {name}."
        
        # Return latest order
        latest_file = files[0]
        with open(os.path.join(ORDERS_DIR, latest_file), "r") as f:
            data = json.load(f)
        
        return (
            f"Most recent order: {data.get('size')} {data.get('drinkType')} "
            f"for {data.get('name')}"
        )
        
    except Exception as e:
        logger.exception("get_order_status failed: %s", e)
        return "Unable to check order status at the moment."



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
    """Main entry point for the voice assistant"""
    logger.info("=" * 60)
    logger.info("🚀 NEW SESSION STARTED")
    logger.info("Room: %s", ctx.room.name)
    logger.info("=" * 60)
    
    # Connect to room
    await ctx.connect()


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


    # System instructions for the barista agent
    instructions = """You are a friendly and efficient café barista at 'MG'S cafe'.


Your job is to take coffee orders by collecting:
1. Drink type (latte, cappuccino, espresso, americano, etc.)
2. Size (small, medium, or large)
3. Milk preference (whole, skim, oat, almond, soy, or none)
4. Extras - OPTIONAL (whipped cream, vanilla syrup, caramel, etc.)
5. Customer's name


IMPORTANT RULES:
- Ask ONE question at a time
- Be warm, friendly, and conversational
- Keep responses brief and natural
- When you have ALL required fields (drink, size, milk, name), immediately call complete_order()
- For extras, if customer says "no extras" or "nothing else", pass an empty string ""
- Don't repeat information back excessively


Start with a warm greeting and ask what they'd like to order."""


    # Create the Agent with instructions and tools
    agent = Agent(
        instructions=instructions,
        tools=[complete_order, get_order_status],
    )


    # Create the AgentSession with plugins
    session = AgentSession(
        vad=vad_plugin,
        stt=stt_plugin,
        llm=llm_plugin,
        tts=tts_plugin,
    )


    # Start the session
    logger.info("🎙️ Starting voice assistant session...")
    await session.start(agent=agent, room=ctx.room)
    
    # Generate initial greeting
    greeting = (
        "Hi! Welcome to MG'S cafe! "
        "I'm your virtual barista today. "
        "What can I get started for you?"
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
    logger.info("🚀 Starting Coffee Shop Agent...")
    logger.info("Orders directory: %s", ORDERS_DIR)
    
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
