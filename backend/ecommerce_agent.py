#!/usr/bin/env python3
"""
Day 9: E-commerce Voice Agent (ACP-inspired)
Voice-driven shopping with structured commerce protocol
"""

import logging
import os
import sys
from typing import Optional, List, Dict
from dotenv import load_dotenv
from catalog import (
    list_products,
    get_product_by_id,
    create_order,
    get_last_order,
    format_product_list,
    format_order_summary
)

# Logging
logger = logging.getLogger("ecommerce-agent")
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
LIVEKIT_AGENT_NAME = os.getenv("LIVEKIT_AGENT_NAME", "ecommerce-agent")

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

# Session state
browsing_results = []  # Store current search results for reference

# Tools (ACP-inspired commerce functions)
@function_tool
async def browse_products(
    context: RunContext,
    category: Optional[str] = None,
    max_price: Optional[int] = None,
    color: Optional[str] = None,
    size: Optional[str] = None
):
    """
    Browse product catalog with filters.
    
    Args:
        category: Product category (mug, tshirt, hoodie, bag, cap)
        max_price: Maximum price in INR
        color: Color filter
        size: Size filter (for clothing)
    """
    global browsing_results
    
    filters = {}
    if category:
        filters["category"] = category
    if max_price:
        filters["max_price"] = max_price
    if color:
        filters["color"] = color
    if size:
        filters["size"] = size
    
    logger.info(f"🔍 Browsing products with filters: {filters}")
    
    products = list_products(filters)
    browsing_results = products  # Store for later reference
    
    result = format_product_list(products)
    logger.info(f"Found {len(products)} products")
    
    return result


@function_tool
async def place_order(
    context: RunContext,
    product_id: str,
    quantity: int = 1
):
    """
    Place an order for a product.
    
    Args:
        product_id: Product ID (e.g., mug-001, tshirt-002)
        quantity: Number of items to order
    """
    logger.info(f"🛒 Creating order: {product_id} x{quantity}")
    
    line_items = [{"product_id": product_id, "quantity": quantity}]
    
    try:
        order = create_order(line_items)
        summary = format_order_summary(order)
        logger.info(f"✅ Order created: {order['id']}")
        return summary
    except Exception as e:
        logger.error(f"❌ Order creation failed: {e}")
        return f"Sorry, I couldn't create your order. Error: {str(e)}"


@function_tool
async def get_product_details(context: RunContext, product_id: str):
    """Get detailed information about a specific product"""
    logger.info(f"📋 Getting details for: {product_id}")
    
    product = get_product_by_id(product_id)
    
    if not product:
        return f"Sorry, I couldn't find product {product_id}."
    
    details = f"{product['name']}\n"
    details += f"Price: ₹{product['price']}\n"
    details += f"Description: {product['description']}\n"
    if 'color' in product:
        details += f"Color: {product['color']}\n"
    if 'size' in product:
        details += f"Size: {product['size']}\n"
    details += f"In Stock: {'Yes' if product.get('in_stock', True) else 'No'}"
    
    return details


@function_tool
async def view_last_order(context: RunContext):
    """View the most recent order"""
    logger.info("📦 Retrieving last order")
    
    order = get_last_order()
    
    if not order:
        return "You haven't placed any orders yet."
    
    return format_order_summary(order)


# Main logic
def prewarm(proc: JobProcess):
    if silero:
        proc.userdata["vad"] = silero.VAD.load()
        logger.info("✅ VAD Loaded")
    
    logger.info("✅ Product catalog loaded")


async def entrypoint(ctx: JobContext):
    logger.info(f"🚀 Starting E-commerce Agent in room: {ctx.room.name}")
    
    global browsing_results
    browsing_results = []
    
    await ctx.connect()

    llm = google.LLM()
    tts = murf.TTS(voice="en-US-matthew")
    stt = deepgram.STT(model="nova-2")
    vad = ctx.proc.userdata.get("vad")

    instructions = """
    You are a helpful shopping assistant for StyleHub, an e-commerce store.
    
    YOUR ROLE:
    
    1. GREETING:
       - Welcome warmly: "Hi! Welcome to StyleHub!"
       - Explain: "I can help you find and buy products. We have mugs, t-shirts, hoodies, bags, and caps."
       - Ask: "What are you looking for today?"
    
    2. PRODUCT BROWSING:
       - Use browse_products tool when user wants to see products
       - Support natural queries like:
         * "Show me coffee mugs"
         * "Do you have black hoodies?"
         * "I want a t-shirt under 700 rupees"
         * "Any blue items?"
       - Extract filters from user intent:
         * Category (mug, tshirt, hoodie, bag, cap)
         * Max price
         * Color
         * Size
    
    3. PRODUCT DETAILS:
       - When user asks about a specific product, use get_product_details
       - Provide clear, concise information
    
    4. ORDERING:
       - When user wants to buy, use place_order tool
       - User might say:
         * "I'll buy the first one"
         * "Order the black hoodie"
         * "I want 2 of those mugs"
       - Map their reference to the correct product_id
       - If they mentioned a product from the last browse results, use that
       - Confirm order details clearly
    
    5. ORDER HISTORY:
       - Use view_last_order when user asks "What did I buy?" or "Show my order"
    
    6. CONVERSATIONAL TIPS:
       - Keep responses concise (2-3 sentences max)
       - Always confirm actions: "I found 5 hoodies..." or "Order placed!"
       - If unclear, ask for clarification
       - Be friendly and helpful
    
    IMPORTANT:
    - Product IDs follow pattern: category-number (e.g., mug-001, hoodie-002)
    - Prices are in INR (Indian Rupees)
    - Always use the tools - don't make up product information
    - When user references "the second one" or "that hoodie", use context from browse_products results
    """

    agent = Agent(
        instructions=instructions,
        tools=[browse_products, place_order, get_product_details, view_last_order],
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
            instructions="Greet the user warmly as a StyleHub shopping assistant and ask what they're looking for today."
        )
        logger.info("✅ Shopping session started!")
    except Exception as e:
        logger.error(f"❌ Error starting session: {e}")


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
