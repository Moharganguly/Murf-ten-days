#!/usr/bin/env python3
"""
Day 7: Food & Grocery Ordering Voice Agent
Intelligent shopping assistant with cart management
"""

import logging
import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional
from dotenv import load_dotenv

# Logging
logger = logging.getLogger("grocery-agent")
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
LIVEKIT_AGENT_NAME = os.getenv("LIVEKIT_AGENT_NAME", "grocery-agent")

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

# Paths
CATALOG_FILE = os.path.join(os.path.dirname(__file__), "catalog.json")
RECIPES_FILE = os.path.join(os.path.dirname(__file__), "recipes.json")
ORDERS_DIR = os.path.join(os.path.dirname(__file__), "orders")
os.makedirs(ORDERS_DIR, exist_ok=True)

# Global state
catalog = {}
recipes = {}
cart = {}  # {item_id: {name, price, quantity}}

# Helper functions
def load_catalog():
    """Load product catalog from JSON"""
    global catalog
    try:
        with open(CATALOG_FILE, 'r', encoding='utf-8') as f:
            catalog = json.load(f)
        logger.info(f"✅ Loaded catalog with {sum(len(items) for items in catalog['categories'].values())} items")
    except Exception as e:
        logger.error(f"❌ Failed to load catalog: {e}")
        catalog = {"store_name": "QuickMart", "categories": {}}

def load_recipes():
    """Load recipes mapping from JSON"""
    global recipes
    try:
        with open(RECIPES_FILE, 'r', encoding='utf-8') as f:
            recipes = json.load(f)
        logger.info(f"✅ Loaded {len(recipes.get('recipes', {}))} recipes")
    except Exception as e:
        logger.error(f"❌ Failed to load recipes: {e}")
        recipes = {"recipes": {}}

def find_item_by_name(item_name: str) -> Optional[Dict]:
    """Find an item in catalog by name (case-insensitive partial match)"""
    item_name_lower = item_name.lower()
    
    for category_items in catalog.get('categories', {}).values():
        for item in category_items:
            if item_name_lower in item['name'].lower():
                return item
    return None

def get_cart_total() -> float:
    """Calculate cart total"""
    return sum(item['price'] * item['quantity'] for item in cart.values())

def format_cart() -> str:
    """Format cart contents as a string"""
    if not cart:
        return "Your cart is empty."
    
    items_list = []
    for item_id, item_data in cart.items():
        items_list.append(
            f"{item_data['quantity']}x {item_data['name']} @ ₹{item_data['price']:.2f} each"
        )
    
    total = get_cart_total()
    cart_text = "\n".join(items_list)
    cart_text += f"\n\nTotal: ₹{total:.2f}"
    return cart_text

# Tools
@function_tool
async def add_item_to_cart(context: RunContext, item_name: str, quantity: int = 1):
    """Add an item to the shopping cart"""
    global cart
    
    item = find_item_by_name(item_name)
    
    if not item:
        logger.warning(f"⚠️ Item not found: {item_name}")
        return f"Sorry, I couldn't find '{item_name}' in our catalog. Could you try a different name?"
    
    item_id = item['id']
    
    if item_id in cart:
        cart[item_id]['quantity'] += quantity
        logger.info(f"➕ Updated {item['name']}: {cart[item_id]['quantity']} total")
        return f"Updated! You now have {cart[item_id]['quantity']} {item['name']} in your cart."
    else:
        cart[item_id] = {
            'name': item['name'],
            'price': item['price'],
            'quantity': quantity,
            'unit': item.get('unit', 'unit')
        }
        logger.info(f"➕ Added {quantity}x {item['name']} to cart")
        return f"Added {quantity} {item['name']} to your cart for ₹{item['price']:.2f} each."

@function_tool
async def remove_item_from_cart(context: RunContext, item_name: str):
    """Remove an item from the shopping cart"""
    global cart
    
    item = find_item_by_name(item_name)
    
    if not item:
        return f"I couldn't find '{item_name}' in the catalog."
    
    item_id = item['id']
    
    if item_id in cart:
        removed_item = cart.pop(item_id)
        logger.info(f"➖ Removed {removed_item['name']} from cart")
        return f"Removed {removed_item['name']} from your cart."
    else:
        return f"{item['name']} is not in your cart."

@function_tool
async def show_cart(context: RunContext):
    """Show current cart contents and total"""
    cart_text = format_cart()
    logger.info("📋 Showing cart")
    return cart_text

@function_tool
async def add_recipe_ingredients(context: RunContext, recipe_name: str):
    """Add all ingredients for a recipe to the cart"""
    global cart
    
    recipe_name_lower = recipe_name.lower()
    recipe = recipes.get('recipes', {}).get(recipe_name_lower)
    
    if not recipe:
        logger.warning(f"⚠️ Recipe not found: {recipe_name}")
        return f"Sorry, I don't have a recipe for '{recipe_name}'. Try asking for specific items instead."
    
    added_items = []
    item_ids = recipe.get('items', [])
    quantities = recipe.get('quantities', [1] * len(item_ids))
    
    for idx, item_id in enumerate(item_ids):
        # Find item in catalog
        item = None
        for category_items in catalog.get('categories', {}).values():
            for cat_item in category_items:
                if cat_item['id'] == item_id:
                    item = cat_item
                    break
            if item:
                break
        
        if item:
            qty = quantities[idx] if idx < len(quantities) else 1
            
            if item_id in cart:
                cart[item_id]['quantity'] += qty
            else:
                cart[item_id] = {
                    'name': item['name'],
                    'price': item['price'],
                    'quantity': qty,
                    'unit': item.get('unit', 'unit')
                }
            added_items.append(item['name'])
    
    logger.info(f"🍳 Added recipe ingredients for: {recipe_name}")
    description = recipe.get('description', ', '.join(added_items))
    return f"I've added {description} to your cart for your {recipe_name}!"

@function_tool
async def place_order(context: RunContext, customer_name: str = "Guest", delivery_address: str = "Not provided"):
    """Place the order and save it to a JSON file"""
    global cart
    
    if not cart:
        return "Your cart is empty! Please add some items before placing an order."
    
    # Create order object
    order_id = f"ORD{datetime.now().strftime('%Y%m%d%H%M%S')}"
    order = {
        "order_id": order_id,
        "customer_name": customer_name,
        "delivery_address": delivery_address,
        "items": [],
        "total": get_cart_total(),
        "timestamp": datetime.now().isoformat(),
        "status": "placed"
    }
    
    # Add cart items to order
    for item_id, item_data in cart.items():
        order['items'].append({
            "item_id": item_id,
            "name": item_data['name'],
            "quantity": item_data['quantity'],
            "unit_price": item_data['price'],
            "subtotal": item_data['price'] * item_data['quantity']
        })
    
    # Save order to file
    order_file = os.path.join(ORDERS_DIR, f"{order_id}.json")
    try:
        with open(order_file, 'w', encoding='utf-8') as f:
            json.dump(order, f, indent=2)
        logger.info(f"✅ Order {order_id} saved to {order_file}")
    except Exception as e:
        logger.error(f"❌ Failed to save order: {e}")
        return "Sorry, there was an error saving your order. Please try again."
    
    # Clear cart
    cart_summary = format_cart()
    cart.clear()
    
    return f"Order placed successfully! Your order ID is {order_id}. Total: ₹{order['total']:.2f}. Estimated delivery in 30 minutes. Thank you for shopping with {catalog.get('store_name', 'QuickMart')}!"

# Main logic
def prewarm(proc: JobProcess):
    load_catalog()
    load_recipes()
    
    if silero:
        proc.userdata["vad"] = silero.VAD.load()
        logger.info("✅ VAD Loaded")

async def entrypoint(ctx: JobContext):
    logger.info(f"🚀 Starting Grocery Agent in room: {ctx.room.name}")
    
    global cart
    cart = {}
    
    await ctx.connect()

    llm = google.LLM()
    tts = murf.TTS(voice="en-US-matthew")
    stt = deepgram.STT(model="nova-2")
    vad = ctx.proc.userdata.get("vad")

    store_name = catalog.get('store_name', 'QuickMart Express')

    instructions = f"""
    You are a friendly shopping assistant for {store_name}, a food and grocery delivery service.
    
    Your conversation flow:
    
    1. GREETING:
       - Introduce yourself: "Hi! Welcome to {store_name}!"
       - Explain: "I can help you order groceries, snacks, prepared food, and more!"
       - Ask: "What would you like to order today?"
    
    2. TAKING ORDERS:
       - Listen for item names and quantities
       - Use add_item_to_cart for specific items
       - Use add_recipe_ingredients for meal requests like "peanut butter sandwich" or "pasta"
       - Confirm each addition: "Added [quantity] [item] to your cart"
       - Ask: "Anything else?"
    
    3. CART MANAGEMENT:
       - Use show_cart when user asks "What's in my cart?" or "Show my cart"
       - Use remove_item_from_cart if user wants to remove something
       - Provide running total when showing cart
    
    4. CHECKOUT:
       - When user says "I'm done", "Place order", "That's all", etc.
       - Use show_cart to confirm final items
       - Ask for customer name and delivery address
       - Use place_order tool with name and address
       - Confirm order ID and delivery time
    
    Important:
    - Be conversational and helpful
    - Confirm quantities if unclear
    - Suggest alternatives if item not found
    - Keep responses concise
    - Always confirm cart changes verbally
    """

    agent = Agent(
        instructions=instructions,
        tools=[add_item_to_cart, remove_item_from_cart, show_cart, add_recipe_ingredients, place_order],
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
            instructions=f"Greet the user warmly and introduce yourself as a {store_name} shopping assistant. Ask what they'd like to order today."
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
